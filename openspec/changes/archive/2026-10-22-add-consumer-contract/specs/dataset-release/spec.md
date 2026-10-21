## ADDED Requirements

### Requirement: Consumer contract artifact

Each build SHALL write `contract.json` next to the other artifacts. It SHALL list every published table with its columns (name, logical type, nullability), primary key, foreign keys, `schema_hash`, and whether it is present in `internacia.duckdb`; every enum-like column with its allowed values and openness; `contract_version` (`MAJOR.MINOR` of the dataset version); `min_duckdb`; and the DuckDB storage compatibility version. The file SHALL be generated from `internacia_builder/schemas.py` and the source JSON Schemas, committed, and attached to every GitHub Release.

#### Scenario: Contract matches the build

- **WHEN** `scripts/builder.py build` completes
- **THEN** `contract.json` exists and regenerating it from the schemas produces an identical file

#### Scenario: Release contract version

- **WHEN** the release workflow runs for tag `v3.2.0`
- **THEN** `contract.json` has `dataset_version` `3.2.0` and `contract_version` `3.2`

### Requirement: Canonical schema hash

`schema_hash` SHALL be the SHA-256 hex digest of the canonical JSON array `[[name, logical_type, nullable], ...]` of a table's columns in column order, serialized with `separators=(",", ":")`, using the logical type grammar documented in `docs/data-contract.md`. It SHALL NOT depend on the pyarrow or DuckDB version.

#### Scenario: pyarrow upgrade

- **WHEN** the builder's pyarrow version changes and the schemas do not
- **THEN** every `schema_hash` stays the same

#### Scenario: Column added

- **WHEN** a column is added to a table
- **THEN** that table's `schema_hash` changes and the other tables' hashes do not

### Requirement: Bundle checksums

Each bundle SHALL contain `SHA256SUMS` listing the SHA-256 of every other file in the bundle in `sha256sum` format. Each `*.manifest.json` SHALL list `sha256` and `bytes` for the files of its dataset and SHALL include `contract_version`. DuckDB `_meta` SHALL include `contract_version`. Each `datapackage.json` resource SHALL include `bytes`, `hash` (`sha256:<hex>`) and, for tabular resources, a `schema`.

#### Scenario: Corrupted download detected

- **WHEN** a consumer runs `sha256sum -c SHA256SUMS` on a downloaded bundle with a truncated file
- **THEN** the check reports that file as failed

#### Scenario: Release assets covered

- **WHEN** the release workflow publishes a GitHub Release
- **THEN** every attached asset other than `SHA256SUMS` is listed in `SHA256SUMS`, including `migration.vX.Y.Z.json`

### Requirement: Open enum values

Enum-like columns SHALL be declared `"open": true` in `contract.json`. Consumers SHALL accept values they do not recognize. Adding a value to an open enum SHALL be a MINOR change; removing or renaming a value SHALL be a MAJOR change.

#### Scenario: New scope category

- **WHEN** a release adds a new `scope_category` value
- **THEN** the release is MINOR and the contract lists the value under the open enum

### Requirement: Data versioning policy

Dataset versions SHALL follow these rules. MAJOR: removing or renaming a table or column, changing a column type, narrowing an enum, or changing key semantics. MINOR: adding tables, columns, views or identifiers, adding open-enum values, or adding a validation gate. PATCH: value changes only. A column or resource SHALL be marked `deprecated` in `contract.json` in a MINOR release before it is removed, and SHALL NOT be removed before the next MAJOR release.

#### Scenario: Column removal requires deprecation

- **WHEN** a column is removed in a MAJOR release
- **THEN** an earlier MINOR release listed that column under `deprecated` in `contract.json`

### Requirement: Identifier stability

An intblock ID or country code present in the previous release SHALL NOT disappear unless the alias files (`intblocks_aliases` / `countries_aliases`) contain an entry for it with a `reason` of `merged`, `renamed`, `disambiguated` or `retired` (`retired` entries have no target). Validation SHALL fail otherwise.

#### Scenario: Silent removal rejected

- **WHEN** a pull request deletes an intblock YAML file without adding an alias entry for its ID
- **THEN** validation fails and names the missing alias

### Requirement: Explicit DuckDB compatibility

The builder SHALL set DuckDB `storage_compatibility_version` explicitly and `contract.json` SHALL declare it together with `min_duckdb`, the oldest DuckDB version the release is tested with.

#### Scenario: Builder DuckDB upgrade

- **WHEN** the builder's DuckDB pin is raised
- **THEN** the storage compatibility version of `internacia.duckdb` does not change unless `contract.json` is changed in the same pull request
