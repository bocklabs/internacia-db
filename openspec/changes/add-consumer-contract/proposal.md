# Change: Formal consumer contract for released datasets

## Why
The internacia SDK and the internacia-api broke silently on data v3: a removed column
(`intblocks.translations`), retired IDs without a machine-readable redirect, and NULL nested
columns. Consumers have no single machine-readable statement of what a release contains, which
changes are breaking, or how to verify the files they downloaded. `schema_hash` exists but is the
SHA-256 of `pyarrow.Schema.serialize()`, so it changes with the pyarrow version and cannot be
recomputed by non-Python consumers. Three MAJOR releases in ten months also show the need for an
explicit versioning and deprecation policy.

## What Changes
- **Contract artifact.** Every build writes `contract.json`: tables, columns, logical types,
  nullability, primary and foreign keys, enum value lists with their openness, `contract_version`,
  `min_duckdb` and the DuckDB storage compatibility version. It is generated from
  `internacia_builder/schemas.py` and the source JSON Schemas, committed, and attached to releases.
- **Canonical `schema_hash`.** SHA-256 of a canonical JSON list of `[name, logical_type, nullable]`
  per column, in column order, using a documented type grammar that does not depend on pyarrow.
- **Checksums.** `SHA256SUMS` covers every file in the bundle. Manifests list `sha256` and `bytes`
  for each file of their dataset and carry `contract_version`; `_meta` carries `contract_version`;
  `datapackage.json` resources carry `bytes`, `hash` and a Table Schema.
- **Open enums.** Enum-like columns (`status`, `scope_category`, `geographic_scope`, …) are declared
  open: consumers MUST accept values they do not know, and adding a value is a MINOR change.
- **SemVer for data.** MAJOR / MINOR / PATCH rules for schema and identifier changes, with batched
  MAJOR releases and a deprecation window of at least one MINOR release.
- **Identifier stability.** Removing an intblock ID or country code without an alias entry is
  forbidden and fails validation.
- **Deterministic builds.** Exports are byte-reproducible for a given commit (DuckDB by content);
  `build_date` is the commit time and `git_commit` the built commit. Binary and bulk exports are
  no longer committed; `data/datasets/` keeps manifests, `contract.json`, `datapackage.json`, the
  dataset card and alias JSON (decision D3).
- **Aliases and canonical views inside DuckDB** (`intblock_aliases`, `country_aliases`,
  `attribute_migrations`, `current_memberships`, `country_currencies`, `country_languages`,
  `country_timezones`), documented in the contract.

## Impact
- Affected specs: dataset-release
- Affected code: `internacia_builder/{schemas,manifest,export,build,distribution}.py`,
  `internacia_builder/validate/`, `scripts/check_generated_artifacts.py`,
  `scripts/check_release_bundle.py`, `.github/workflows/release.yml`, `docs/`
- Consumers: `schema_hash` values change once (new algorithm, full 64-hex digest). `_meta` gains
  `contract_version` (additive). New release assets `contract.json` and `SHA256SUMS`. The SDK and
  API gain contract checks in their own repositories (py-1.1, api-1.1).
- Release: ships in the next MINOR release.
