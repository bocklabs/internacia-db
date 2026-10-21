"""Distribution descriptors must resolve inside the exact published bundle."""
import json

import pytest

from internacia_builder import __version__, distribution
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


def _release_root(tmp_path, citation_version, citation_date, changelog_date="2026-01-02"):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "pyproject.toml").write_text(f'[project]\nversion = "{__version__}"\n')
    (root / "CHANGELOG.md").write_text(f"## [Unreleased]\n\n## [{__version__}] - {changelog_date}\n")
    (root / "CITATION.cff").write_text(f"version: {citation_version}\ndate-released: {citation_date}\n")
    datasets = tmp_path / "datasets"
    datasets.mkdir()
    (datasets / "countries.manifest.json").write_text(json.dumps({"version": __version__}))
    return root, datasets


def test_release_version_accepts_consistent_citation(tmp_path, monkeypatch):
    root, datasets = _release_root(tmp_path, __version__, "2026-01-02")
    monkeypatch.setattr(distribution, "project_root", lambda: root)
    check_release_version(f"v{__version__}", datasets)


def test_release_version_rejects_stale_citation_version(tmp_path, monkeypatch):
    root, datasets = _release_root(tmp_path, "0.0.1", "2026-01-02")
    monkeypatch.setattr(distribution, "project_root", lambda: root)
    with pytest.raises(ValueError, match="CITATION.cff"):
        check_release_version(f"v{__version__}", datasets)


def test_release_version_rejects_stale_citation_date(tmp_path, monkeypatch):
    root, datasets = _release_root(tmp_path, __version__, "2025-12-31")
    monkeypatch.setattr(distribution, "project_root", lambda: root)
    with pytest.raises(ValueError, match="date-released"):
        check_release_version(f"v{__version__}", datasets)


def test_repository_citation_matches_current_release(tmp_path):
    (tmp_path / "countries.manifest.json").write_text(json.dumps({"version": __version__}))
    check_release_version(f"v{__version__}", tmp_path)
