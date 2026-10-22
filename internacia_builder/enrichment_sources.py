"""Split an enrichment run into one pull request per source and decide which may auto-merge.

The policy lives in data/schemas/enrichment_sources.yaml. ``split`` takes the records before
and after enrichment and returns, per source, the records with only that source's fields (and
their provenance entries) changed. ``review_reasons`` lists why a source's changes need review;
an empty list means the pull request may merge once CI passes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from internacia_builder.paths import project_root
from internacia_builder.validate.registry import load_yaml

OTHER = "other"
POLICY_FILE = Path("data/schemas/enrichment_sources.yaml")

Records = dict[str, dict[str, Any]]


@dataclass
class Source:
    name: str
    title: str
    dataset: str
    fields: frozenset[str]
    always_review: bool = False


@dataclass
class Policy:
    sources: dict[str, Source]
    thresholds: dict[str, dict[str, float]] = field(default_factory=dict)

    def source_of(self, dataset: str, name: str) -> str:
        for source in self.sources.values():
            if source.dataset == dataset and name in source.fields:
                return source.name
        return OTHER

    def fields(self, dataset: str) -> frozenset[str]:
        return frozenset().union(*(s.fields for s in self.sources.values() if s.dataset == dataset))


def load_policy(root: Path | None = None) -> Policy:
    data = load_yaml((root or project_root()) / POLICY_FILE) or {}
    sources = {
        name: Source(
            name=name,
            title=str(spec.get("title") or name),
            dataset=str(spec["dataset"]),
            fields=frozenset(spec.get("fields") or []),
            always_review=spec.get("review") == "always",
        )
        for name, spec in (data.get("sources") or {}).items()
    }
    sources[OTHER] = Source(OTHER, "Other enrichment changes", "*", frozenset(), always_review=True)
    return Policy(sources, data.get("thresholds") or {})


def dataset_of(path: str) -> str:
    return "countries" if path.startswith("data/countries/") else "intblocks"


def record_id(path: str, record: dict[str, Any]) -> str:
    return str(record.get("code") or record.get("id") or Path(path).stem)


def changed_fields(before: dict[str, Any], after: dict[str, Any]) -> set[str]:
    """Top-level fields that differ, with provenance changes attributed to their field."""
    names = {k for k in before.keys() | after.keys() if k != "provenance" and before.get(k) != after.get(k)}
    old_prov = {p.get("field"): p for p in before.get("provenance") or [] if isinstance(p, dict)}
    new_prov = {p.get("field"): p for p in after.get("provenance") or [] if isinstance(p, dict)}
    names |= {str(f) for f in old_prov.keys() | new_prov.keys() if old_prov.get(f) != new_prov.get(f)}
    return names


def _apply(base: dict[str, Any], enriched: dict[str, Any], fields: set[str]) -> dict[str, Any]:
    """``base`` with ``fields`` (and their provenance entries) taken from ``enriched``."""
    out: dict[str, Any] = {}
    for key in list(base) + [k for k in enriched if k not in base]:
        source = enriched if key in fields else base
        if key in source:
            out[key] = source[key]
    base_prov = [p for p in base.get("provenance") or [] if isinstance(p, dict)]
    new_prov = {p.get("field"): p for p in enriched.get("provenance") or [] if isinstance(p, dict)}
    provenance = []
    for entry in base_prov:
        name = entry.get("field")
        if name not in fields:
            provenance.append(entry)
        elif name in new_prov:
            provenance.append(new_prov[name])
    present = {p.get("field") for p in base_prov}
    provenance += [p for name, p in new_prov.items() if name in fields and name not in present]
    if provenance or "provenance" in base or "provenance" in enriched:
        out["provenance"] = provenance
    return out


def split(base: Records, enriched: Records, policy: Policy) -> dict[str, Records]:
    """Per source, the changed records with only that source's fields from ``enriched``."""
    result: dict[str, Records] = {}
    for path, after in enriched.items():
        before = base.get(path)
        if before is None:
            result.setdefault(OTHER, {})[path] = after
            continue
        dataset = dataset_of(path)
        by_source: dict[str, set[str]] = {}
        for name in changed_fields(before, after):
            by_source.setdefault(policy.source_of(dataset, name), set()).add(name)
        for source, names in by_source.items():
            result.setdefault(source, {})[path] = _apply(before, after, names)
    return result


def _number(value: Any) -> float | None:
    if isinstance(value, dict):
        value = value.get("value")
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return float(value)


def _empty(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _additive(old: Any, new: Any) -> bool:
    if isinstance(old, list) and isinstance(new, list):
        return all(item in new for item in old)
    if isinstance(old, dict) and isinstance(new, dict):
        return all(new.get(k) == v for k, v in old.items())
    return False


def review_reasons(source: str, base: Records, patched: Records, policy: Policy) -> list[str]:
    """Why ``source``'s changes need review; empty when they may merge automatically."""
    spec = policy.sources[source]
    reasons: list[str] = []
    if spec.always_review:
        reasons.append(f"{spec.title}: always reviewed")
    for path, after in sorted(patched.items()):
        before = base.get(path)
        rid = record_id(path, after)
        if before is None:
            reasons.append(f"{rid}: new record")
            continue
        for name in sorted(changed_fields(before, after)):
            old, new = before.get(name), after.get(name)
            if old == new or _empty(old):
                continue
            if _empty(new):
                reasons.append(f"{rid}.{name}: value removed")
                continue
            limit = policy.thresholds.get(name)
            old_n, new_n = _number(old), _number(new)
            if limit and old_n is not None and new_n is not None:
                if "relative" in limit and old_n and abs(new_n - old_n) / abs(old_n) > limit["relative"]:
                    reasons.append(f"{rid}.{name}: {old_n:g} -> {new_n:g} exceeds ±{limit['relative']:.0%}")
                if "absolute" in limit and abs(new_n - old_n) > limit["absolute"]:
                    reasons.append(f"{rid}.{name}: {old_n:g} -> {new_n:g} exceeds ±{limit['absolute']:g}")
                continue
            if not _additive(old, new):
                reasons.append(f"{rid}.{name}: existing value replaced")
    return reasons
