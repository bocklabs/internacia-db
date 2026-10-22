## Context
internacia-db has three consumers with different needs: DuckDB/R/Polars users reading files
directly, the `internacia` Python SDK (the only query layer), and the self-hosted internacia-api.
All three need to know, without reading the CHANGELOG, whether a release is compatible with them and
whether the downloaded files are intact.

## Goals / Non-Goals
- Goals: one machine-readable contract per release; a schema fingerprint any consumer can
  recompute; verifiable downloads; explicit rules for what counts as breaking.
- Non-Goals: a registry or API for contracts; changing table layouts; enforcing constraints inside
  DuckDB beyond what the contract documents.

## Decisions

### `contract.json` layout
```json
{
  "contract_version": "3.1",
  "dataset_version": "3.1.0",
  "min_duckdb": "1.5.4",
  "duckdb_storage_compatibility_version": "v1.0.0",
  "enum_policy": "open",
  "type_grammar": "internacia-logical-types/1",
  "tables": [
    {
      "name": "memberships",
      "in_duckdb": true,
      "primary_key": ["intblock_id", "country_code"],
      "foreign_keys": [
        {"columns": ["intblock_id"], "references": {"table": "intblocks", "columns": ["id"]}}
      ],
      "schema_hash": "<64 hex>",
      "columns": [{"name": "intblock_id", "type": "string", "nullable": false}]
    }
  ],
  "enums": [
    {"table": "intblocks", "column": "status", "values": ["formal", "…"], "open": true}
  ],
  "deprecated": []
}
```
- `contract_version` is `MAJOR.MINOR` of the dataset version. PATCH releases never change the
  contract, so consumers pin `MAJOR` and warn on a newer `MINOR`.
- Enum values come from the source JSON Schemas (`data/schemas/*.schema.json`), so the contract,
  the validator and the YAML sources share one list.
- Foreign keys that have documented exceptions carry a `note` instead of being dropped.

### Logical type grammar (`internacia-logical-types/1`)
`string`, `boolean`, `int32`, `int64`, `float64`, `list<T>`, `struct<name:T,...>` (fields in
declared order), `map<K,V>`. `schema_hash` is the SHA-256 (hex) of
`json.dumps([[name, type, nullable], ...], separators=(",", ":"), ensure_ascii=False)`.
- Alternatives considered: hashing DuckDB type strings (`duckdb_columns().data_type`) — rejected
  because DuckDB's type printing is not guaranteed stable across versions; hashing Arrow IPC bytes
  (current) — rejected because it depends on the pyarrow version.

### Checksums
- `SHA256SUMS` in `sha256sum` format, sorted by file name, covering every file in the bundle except
  itself. It is rewritten after the release workflow adds `migration.vX.Y.Z.json`.
- A file cannot contain its own checksum, so DuckDB `_meta` carries `contract_version` but not file
  checksums; those live in manifests, `datapackage.json` and `SHA256SUMS`.

### DuckDB compatibility
- The builder sets `storage_compatibility_version` explicitly, so upgrading the builder's DuckDB
  does not silently raise the minimum reader version.
- `min_duckdb` is the oldest DuckDB the release is tested with (the builder pin and the SDK's lower
  bound), not merely the oldest one able to open the file.

### Versioning
- MAJOR: remove or rename a table or column, change a type, narrow an enum, change key semantics.
  Removing an identifier without an alias is not allowed at all.
- MINOR: new tables, columns, views, identifiers; new values of open enums; new validation gates.
- PATCH: value changes only (enrichment, rosters, corrections).
- Deprecation: mark in `contract.json` `deprecated` in a MINOR release, remove no earlier than the
  next MAJOR. MAJOR changes are batched, at most one or two per year.

## Risks / Trade-offs
- `schema_hash` values change once → consumers that pinned hashes must update; documented in the
  CHANGELOG and covered by the MINOR release notes.
- Deterministic DuckDB files are not byte-reproducible (DuckDB storage layout); reproducibility is
  checked by content (row hashes) instead.

## Migration Plan
Ship in one MINOR release: contract + checksums (db-1.2), deterministic builds (db-1.3), aliases and
views inside DuckDB (db-1.4). The SDK and API adopt contract checks in their next releases.

## Open Questions
- None blocking. Whether to add PRIMARY KEY constraints inside DuckDB can be revisited once SDK
  query plans show a benefit.
