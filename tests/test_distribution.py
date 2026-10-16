"""Distribution descriptors must resolve inside the exact published bundle."""
import json

import pytest

from internacia_builder.distribution import check_release_version, prepare_huggingface_bundle, validate_package
from internacia_builder.export import write_datapackage


def test_descriptor_names_are_unique_per_table_and_format(tmp_path):
    for name in ("countries.parquet", "countries.csv.zst", "countries-lite.parquet"):
        (tmp_path / name).write_bytes(b"fixture")
    write_datapackage(tmp_path, "2.1.0")
    validate_package(tmp_path)
    names = [r["name"] for r in json.loads((tmp_path / "datapackage.json").read_text())["resources"]]
    assert names == ["countries-csv", "countries-parquet", "countries-lite-parquet"]


def test_descriptor_rejects_missing_resources_and_duplicate_names(tmp_path):
    package = {"resources": [{"name": "a", "path": "missing.parquet"}]}
    with pytest.raises(ValueError, match="Unresolvable"):
        validate_package(tmp_path, package)
    package["resources"] *= 2
    with pytest.raises(ValueError, match="unique"):
        validate_package(tmp_path, package)


def test_partial_huggingface_bundle_has_resolvable_nested_paths(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    for table in ("countries", "intblocks", "blocktypes", "memberships"):
        (source / f"{table}.parquet").write_bytes(b"fixture")
        for suffix in ("manifest.json", "meta.json"):
            (source / f"{table}.{suffix}").write_text("{}")
    (source / "countries.jsonl").write_text("{}\n")
    write_datapackage(source, "2.1.0")
    target = tmp_path / "mirror"
    prepare_huggingface_bundle(source, target)
    resources = json.loads((target / "datapackage.json").read_text())["resources"]
    assert len(resources) == 4
    assert {r["path"] for r in resources} == {f"{r['table']}/{r['table']}.parquet" for r in resources}
    validate_package(target)


def test_release_tag_must_match_package_and_manifest_versions(tmp_path):
    (tmp_path / "countries.manifest.json").write_text(json.dumps({"version": "0.0.0"}))
    with pytest.raises(ValueError, match="disagrees"):
        check_release_version("v99.0.0", tmp_path)
