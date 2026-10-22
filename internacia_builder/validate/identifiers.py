"""Identifier stability: released IDs never disappear without an alias entry.

Record file names equal their IDs (enforced by the filename rules), so the IDs of the
previous release are the YAML file stems at the latest reachable release tag.
"""

from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath


def _git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return None
    return result.stdout if result.returncode == 0 else None


def previous_release_ref(root: Path) -> str | None:
    """Latest release tag reachable from HEAD, or None outside a tagged git checkout."""
    out = _git(root, "describe", "--tags", "--abbrev=0", "--match", "v[0-9]*", "HEAD")
    return out.strip() if out else None


def ids_at_ref(root: Path, ref: str, source_dir: str) -> set[str] | None:
    """IDs (YAML file stems) under ``source_dir`` at ``ref``."""
    out = _git(root, "ls-tree", "-r", "--name-only", ref, "--", source_dir)
    if out is None:
        return None
    return {PurePosixPath(line).stem for line in out.splitlines() if line.endswith(".yaml")}


def check_identifier_stability(
    kind: str,
    previous_ids: set[str],
    current_ids: set[str],
    alias_names: set[str],
    ref: str,
    aliases_file: str,
) -> list[str]:
    """One error per ID present at ``ref`` that is neither current nor aliased."""
    return [
        f"{kind} id '{missing}' existed in {ref} but has no record and no entry in {aliases_file}; "
        "add an alias (renamed, merged, disambiguated) instead of removing it silently"
        for missing in sorted(previous_ids - current_ids - alias_names)
    ]


def release_identifier_errors(
    root: Path, kind: str, source_dir: str, current_ids: set[str], alias_names: set[str], aliases_file: str
) -> list[str]:
    """Errors for IDs removed since the previous release; empty when git history is unavailable."""
    ref = previous_release_ref(root)
    if ref is None:
        return []
    previous = ids_at_ref(root, ref, source_dir)
    if previous is None:
        return []
    return check_identifier_stability(kind, previous, current_ids, alias_names, ref, aliases_file)
