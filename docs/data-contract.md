# Data contract

Every build writes `contract.json` next to the other artifacts, and every GitHub Release
attaches it. It is the machine-readable statement of what a release contains and which
changes the [versioning policy](versioning-policy.md) treats as breaking. The SDK and the
API check it; other consumers (DuckDB, R, Polars) can read it directly.

`contract.json` is generated from `internacia_builder/schemas.py` (columns and types) and
`data/schemas/*.schema.json` (enum values). CI fails if the committed file differs from the
generated one.

## Fields

| Field | Meaning |
|-------|---------|
| `contract_version` | `MAJOR.MINOR` of the dataset version. PATCH releases never change the contract. Pin the MAJOR; treat a newer MINOR as compatible. |
| `dataset_version` | The dataset version the file was built for (equals the release tag). |
| `min_duckdb` | Oldest DuckDB version the release is tested with. |
| `duckdb_storage_compatibility_version` | DuckDB storage format used for `internacia.duckdb` (set explicitly by the builder). |
| `enum_policy` | Always `open`: see [Open enums](#open-enums). |
| `type_grammar` | Version of the logical type grammar below. |
| `tables[]` | One entry per table: `name`, `in_duckdb`, `primary_key`, `foreign_keys`, `schema_hash`, `columns[]` (`name`, `type`, `nullable`). |
| `enums[]` | Enum-like columns: `table`, `column` (nested paths use `field[].sub`), `values`, `open`. |
| `deprecated[]` | Columns or resources scheduled for removal in the next MAJOR release. |

Tables in `internacia.duckdb`: `countries`, `intblocks`, `blocktypes`, `memberships`, `_meta`.
Tables shipped as separate files only: `intblocks_aliases`, `countries_aliases`,
`attribute_intblock_migrations`. The `*-lite` projections and CSV files are derived
convenience exports and are not part of the contract.

Foreign keys with known exceptions carry a `note`: `memberships.country_code` can reference
historical codes such as `SU` that are not in `countries`.

```sql
-- Read the contract from DuckDB without Python
SELECT t.name, t.schema_hash
FROM read_json('contract.json') AS c, UNNEST(c.tables) AS u(t);
```

## Logical types

`internacia-logical-types/1`:

| Type | Meaning |
|------|---------|
| `string`, `boolean`, `int32`, `int64`, `float64` | Scalars |
| `list<T>` | List of `T` |
| `struct<a:T,b:U>` | Struct; fields in declared order |
| `map<K,V>` | Map from `K` to `V` |

Example: `countries.native_names` is `map<string,struct<official:string,common:string>>`.

## `schema_hash`

`schema_hash` is the SHA-256 hex digest of the table's columns as a canonical JSON array of
`[name, logical_type, nullable]` in column order, serialized without spaces:

```python
import hashlib, json

columns = [[c["name"], c["type"], c["nullable"]] for c in table["columns"]]
schema_hash = hashlib.sha256(
    json.dumps(columns, separators=(",", ":"), ensure_ascii=False).encode()
).hexdigest()
```

It appears in `contract.json`, every `*.manifest.json` and `*.meta.json`, and DuckDB `_meta`.
It does not depend on the pyarrow or DuckDB version, so it only changes when a column is
added, removed, renamed, retyped, or changes nullability.

## Open enums

Every column listed in `enums[]` is open. Consumers must accept values they do not know
(map them to "other", pass them through, or ignore them), because adding a value is a MINOR
change. Removing or renaming a value is a MAJOR change. Each release's `contract.json` lists
the values that release uses.

## Checksums

- `SHA256SUMS` (`sha256sum` format) covers every other file in the bundle, including
  `migration.vX.Y.Z.json`. Verify a download with `sha256sum -c SHA256SUMS`.
- Each `*.manifest.json` lists `files[]` with `path`, `sha256` and `bytes` for its dataset's
  files, plus `contract_version`.
- `datapackage.json` resources carry `bytes`, `hash` (`sha256:<hex>`) and, for Parquet
  resources, a Frictionless Table Schema.
- DuckDB `_meta` carries `contract_version`. A file cannot contain its own checksum, so the
  checksum of `internacia.duckdb` is in `SHA256SUMS` and `datapackage.json`.

## Checking compatibility

1. Read `contract_version`; refuse a different MAJOR than the one you support.
2. Compare each table's `schema_hash` with the one you tested against. A different hash with
   the same MAJOR means additive changes: read `migration.vX.Y.Z.json` and the CHANGELOG.
3. Verify downloads with `SHA256SUMS`.
4. Remap stored IDs through the alias files before joining.
