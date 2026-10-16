"""Validate enriched source records before replacing a YAML file."""

from __future__ import annotations

import json
import os
import tempfile
from functools import lru_cache
from pathlib import Path

import jsonschema
import yaml

from internacia_builder.paths import project_root
from internacia_builder.validate.country_rules import check_country_indicator_values, check_country_indicator_years
from internacia_builder.validate.intblock_rules import check_intblock_chronology, check_intblock_include_dates


@lru_cache(maxsize=2)
def _validator(dataset: str):
    schema = json.loads((project_root() / "data" / "schemas" / f"{dataset}.schema.json").read_text())
    return jsonschema.validators.validator_for(schema)(schema)


def write_enriched_yaml(path: Path, record: dict, dataset: str) -> None:
    errors = [e.message for e in _validator(dataset).iter_errors(record)]
    checks = (
        check_country_indicator_years(record) + check_country_indicator_values(record)
        if dataset == "countries"
        else check_intblock_chronology(record) + check_intblock_include_dates(record)
    )
    errors.extend(issue["suggested_action"] for issue in checks)
    if errors:
        raise ValueError(f"Refusing invalid enrichment for {path}: {'; '.join(errors)}")
    payload = yaml.safe_dump(record, sort_keys=False, allow_unicode=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temp_path = Path(stream.name)
            stream.write(payload)
        if path.exists():
            temp_path.chmod(path.stat().st_mode)
        os.replace(temp_path, path)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
