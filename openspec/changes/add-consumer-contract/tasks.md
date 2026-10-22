## 1. Contract and checksums (db-1.2)
- [x] 1.1 Canonical logical type grammar and `schema_hash` in `internacia_builder/schemas.py`
- [x] 1.2 Generate `contract.json` (tables, columns, keys, enums, `contract_version`, `min_duckdb`, storage compatibility)
- [x] 1.3 `contract_version` in manifests, `.meta.json` sidecars and DuckDB `_meta`
- [x] 1.4 Per-file `sha256` and `bytes` in manifests; `bytes`, `hash` and Table Schema in `datapackage.json`
- [x] 1.5 `SHA256SUMS` written by the build and re-written after the release migration file
- [x] 1.6 Explicit DuckDB `storage_compatibility_version`
- [x] 1.7 Checks: contract drift and checksum coverage in `check_generated_artifacts.py` / `check_release_bundle.py`; release gate compares `contract.json` version with the tag
- [x] 1.8 Docs: `docs/data-contract.md`, release asset list, CHANGELOG

## 2. Deterministic builds (db-1.3)
- [ ] 2.1 Sorted inputs in `export.load_yaml_files`
- [ ] 2.2 `build_date` from `SOURCE_DATE_EPOCH` or the commit time; `git_commit` is the built commit
- [ ] 2.3 CI check: two builds produce identical text exports and identical DuckDB content
- [ ] 2.4 Stop committing binary artifacts in `data/datasets/` (D3); keep text manifests, `contract.json`, `datapackage.json`, `SHA256SUMS`

## 3. Aliases and canonical views in DuckDB (db-1.4)
- [ ] 3.1 Tables `intblock_aliases`, `country_aliases`, `attribute_migrations`
- [ ] 3.2 Views `current_memberships`, `country_currencies`, `country_languages`, `country_timezones`
- [ ] 3.3 Validator: an intblock ID or country code removed since the previous release must have an alias
- [ ] 3.4 Document the views and alias tables in `contract.json` and the cookbooks
