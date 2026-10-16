"""Tests for scripts/generate_schema_migration.py"""

from __future__ import annotations

import json
from pathlib import Path

import generate_schema_migration as gsm
import pyarrow as pa
import pyarrow.parquet as pq


def test_diff_props_detects_added_removed_and_type_change(tmp_path: Path):
    prev = {
        "code": {"type": "string"},
        "name": {"type": "string"},
        "old_field": {"type": "integer"},
    }
    curr = {
        "code": {"type": "string"},
        "name": {"type": "integer"},
        "new_field": {"type": "string"},
    }
    d = gsm.diff_props(prev, curr)
    assert d["added"] == ["new_field"]
    assert d["removed"] == ["old_field"]
    assert d["type_changed"] == [{"field": "name", "from": "string", "to": "integer"}]


def test_build_migration_writes_versioned_file(tmp_path: Path):
    prev_dir = tmp_path / "prev"
    curr_dir = tmp_path / "curr"
    prev_dir.mkdir()
    curr_dir.mkdir()
    (prev_dir / "countries.schema.json").write_text(
        json.dumps({"properties": {"code": {"type": "string"}}}), encoding="utf-8"
    )
    (curr_dir / "countries.schema.json").write_text(
        json.dumps({"properties": {"code": {"type": "string"}, "ioc_code": {"type": "string"}}}),
        encoding="utf-8",
    )
    (curr_dir / "intblocks.schema.json").write_text(
        json.dumps({"properties": {"id": {"type": "string"}}}), encoding="utf-8"
    )
    migration = gsm.build_migration(prev_dir, curr_dir, "1.11.0")
    assert migration["version"] == "1.11.0"
    assert migration["schema_changed"] is True
    assert "ioc_code" in migration["datasets"]["countries"]["added"]


def test_nested_array_type_required_and_enum_changes_are_reported():
    before = {"includes": {"type": "array", "items": {"type": "object", "properties": {
        "id": {"type": "string", "enum": ["A", "B"]}, "year": {"type": "string"},
    }}}}
    after = {"includes": {"type": "array", "items": {"type": "object", "required": ["id"], "properties": {
        "id": {"type": "string", "enum": ["A"]}, "year": {"type": "integer"},
    }}}}
    result = gsm.diff_props(before, after)
    assert result["type_changed"] == [{"field": "includes[].year", "from": "string", "to": "integer"}]
    assert {x["field"] for x in result["constraints_changed"]} == {"includes[].required", "includes[].id.enum"}


def test_unknown_baseline_does_not_claim_unchanged_schema(tmp_path):
    current = tmp_path / "schemas"
    current.mkdir()
    result = gsm.build_migration(None, current, "2.1.1")
    assert result["schema_changed"] is None
    assert result["baseline"]["status"] == "unavailable"


def test_export_only_change_is_detected(tmp_path):
    previous, current = tmp_path / "previous", tmp_path / "current"
    previous.mkdir()
    current.mkdir()
    pq.write_table(pa.table({"n": pa.array([1], type=pa.int32())}), previous / "countries.parquet")
    pq.write_table(pa.table({"n": pa.array([1], type=pa.int64())}), current / "countries.parquet")
    result = gsm.build_migration(previous, current, "2.1.1", current_datasets=current)
    assert result["schema_changed"] is True
    assert result["exports"]["countries"]["type_changed"] == [{"field": "n", "from": "int32", "to": "int64"}]
