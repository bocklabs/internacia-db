# Maintainer release distribution

Tagged releases (`v*`) rebuild datasets and attach GitHub Release assets
(`.github/workflows/release.yml`). Optional mirrors:

| Channel | Secret / var | Behavior |
|---------|--------------|----------|
| Hugging Face Datasets | `HF_TOKEN`; optional `vars.HF_DATASET_REPO` (default `datenoio/internacia`) | Upload a validated Parquet bundle, rewritten descriptor, card, and all four tables' manifests/sidecars when token is set |
| Zenodo | `ZENODO_TOKEN`; optional secret `ZENODO_CONCEPT_DOI` (default `10.5281/zenodo.21452328`) | Create a draft deposition and upload the complete release bundle; maintainer publication is still required |
| Schema migration | (always) | Writes `.release-datasets/migration.vX.Y.Z.json` comparing nested source/export contracts against the explicit previous release tag; attached as a Release asset |

Without HF/Zenodo secrets, those steps no-op. GitHub Release assets still publish.

See [publishing-huggingface.md](publishing-huggingface.md) for the full
Hugging Face setup, manual publish, and verification guide.

## Release assets

The GitHub Release assets on tag `vX.Y.Z` are the **bundle of record** for that
version. The committed `data/datasets/` snapshot is a development copy: its bytes
and build identity (`git_commit`, `build_date` in manifests and `_meta`) can
differ from the release build, so pin and verify against Release assets.

Each release attaches every file in `.release-datasets/` — 41 files for v3.0.0:

| Group | Files |
|-------|-------|
| DuckDB | `internacia.duckdb` |
| Countries | `countries.parquet`, `countries.jsonl`, `countries.jsonl.zst`, `countries.json.zst`, `countries.yaml.zst`, `countries.csv.zst`, `countries-lite.parquet`, `countries-lite.csv.zst`, `countries.manifest.json`, `countries.meta.json` |
| Intblocks | `intblocks.parquet`, `intblocks.jsonl`, `intblocks.jsonl.zst`, `intblocks.json.zst`, `intblocks.yaml.zst`, `intblocks.csv.zst`, `intblocks-lite.parquet`, `intblocks-lite.csv.zst`, `intblocks.manifest.json`, `intblocks.meta.json` |
| Blocktypes | `blocktypes.parquet`, `blocktypes.jsonl`, `blocktypes.jsonl.zst`, `blocktypes.yaml`, `blocktypes.yaml.zst`, `blocktypes.manifest.json`, `blocktypes.meta.json` |
| Memberships | `memberships.parquet`, `memberships.csv.zst`, `memberships.manifest.json`, `memberships.meta.json` |
| Aliases and migrations | `intblocks_aliases.json`, `intblocks_aliases.parquet`, `countries_aliases.json`, `countries_aliases.parquet`, `attribute_intblock_migrations.json`, `attribute_intblock_migrations.parquet` |
| Descriptors | `datapackage.json`, `README.md` (dataset card) |
| Schema migration | `migration.vX.Y.Z.json` (release only; not committed) |

There is no checksum file yet; the `*.manifest.json` files carry `version`,
`git_commit`, `row_count`, and `schema_hash` but no content hash.

## Workflow

The workflow checks committed snapshot freshness before rebuilding. It tests and
checks the final `.release-datasets` staging directory, enforces the shared quality
gate and tag-version consistency, then publishes that exact bundle as listed
above. Hugging Face gets a separate validated Parquet-only descriptor with
`table/table.parquet` paths and all four tables' metadata.
Migration files identify the prior release; a first release without a baseline
reports compatibility as unknown rather than unchanged.

Before tagging, align the dated release entry in `CHANGELOG.md`, `pyproject.toml`,
and `internacia_builder/__init__.py`; rebuild and commit exports so their manifest
versions match the tag without `v`. See [versioning-policy.md](versioning-policy.md).

The Zenodo step leaves the deposition as a draft and logs its id. It creates a
new deposition with an `isVersionOf` reference to the configured concept DOI;
it does not call Zenodo's existing-record versioning or publish action. Review
the draft and complete the intended versioning/publication before citing it as
a published release.
