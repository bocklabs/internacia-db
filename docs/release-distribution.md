# Maintainer release distribution

Tagged releases (`v*`) rebuild datasets and attach GitHub Release assets
(`.github/workflows/release.yml`). Optional mirrors:

| Channel | Secret / var | Behavior |
|---------|--------------|----------|
| Hugging Face Datasets | `HF_TOKEN`; optional `vars.HF_DATASET_REPO` (default `datenoio/internacia`) | Upload a validated Parquet bundle, rewritten descriptor, card, and all four tables' manifests/sidecars when token is set |
| Zenodo | None in this workflow (Zenodo GitHub integration on `datenoio/internacia-db`) | Zenodo archives each published GitHub Release as a new version under concept DOI [`10.5281/zenodo.20706176`](https://doi.org/10.5281/zenodo.20706176) |
| Schema migration | (always) | Writes `.release-datasets/migration.vX.Y.Z.json` comparing nested source/export contracts against the explicit previous release tag; attached as a Release asset |

Without `HF_TOKEN`, the Hugging Face step no-ops. GitHub Release assets still publish.

See [publishing-huggingface.md](publishing-huggingface.md) for the full
Hugging Face setup, manual publish, and verification guide.

## Release assets

The GitHub Release assets on tag `vX.Y.Z` are the **bundle of record** for that
version. The repository commits only the text descriptors in `data/datasets/`
(manifests, `contract.json`, `datapackage.json`, dataset card, alias JSON); the
binary and bulk exports exist only in Release assets and local builds.

Builds are reproducible: `build_date` is the commit time (or `SOURCE_DATE_EPOCH`) and
`git_commit` the built commit, so rebuilding a tag reproduces every asset byte for
byte except `internacia.duckdb`, whose table contents are identical.

Each release attaches every file in `.release-datasets/` (41 files for v3.0.0; 43 from
the next release, which adds `contract.json` and `SHA256SUMS`):

| Group | Files |
|-------|-------|
| DuckDB | `internacia.duckdb` |
| Countries | `countries.parquet`, `countries.jsonl`, `countries.jsonl.zst`, `countries.json.zst`, `countries.yaml.zst`, `countries.csv.zst`, `countries-lite.parquet`, `countries-lite.csv.zst`, `countries.manifest.json`, `countries.meta.json` |
| Intblocks | `intblocks.parquet`, `intblocks.jsonl`, `intblocks.jsonl.zst`, `intblocks.json.zst`, `intblocks.yaml.zst`, `intblocks.csv.zst`, `intblocks-lite.parquet`, `intblocks-lite.csv.zst`, `intblocks.manifest.json`, `intblocks.meta.json` |
| Blocktypes | `blocktypes.parquet`, `blocktypes.jsonl`, `blocktypes.jsonl.zst`, `blocktypes.yaml`, `blocktypes.yaml.zst`, `blocktypes.manifest.json`, `blocktypes.meta.json` |
| Memberships | `memberships.parquet`, `memberships.csv.zst`, `memberships.manifest.json`, `memberships.meta.json` |
| Aliases and migrations | `intblocks_aliases.json`, `intblocks_aliases.parquet`, `countries_aliases.json`, `countries_aliases.parquet`, `attribute_intblock_migrations.json`, `attribute_intblock_migrations.parquet` |
| Descriptors | `datapackage.json`, `README.md` (dataset card), `contract.json` (consumer contract) |
| Checksums | `SHA256SUMS` (every other asset, including the migration file) |
| Schema migration | `migration.vX.Y.Z.json` (release only; not committed) |

Verify a download with `sha256sum -c SHA256SUMS` (or `shasum -a 256 -c SHA256SUMS`
on macOS). Each `*.manifest.json` also lists `sha256` and `bytes` for the files of its
dataset, and `datapackage.json` resources carry `bytes` and `hash`. The table schemas,
keys, enum values and versioning rules are in `contract.json`; see
[data-contract.md](data-contract.md).

## Workflow

The workflow builds the bundle, checks that the committed descriptors match it, then tests and
checks the final `.release-datasets` staging directory, enforces the shared quality
gate and tag-version consistency, then publishes that exact bundle as listed
above. Hugging Face gets a separate validated Parquet-only descriptor with
`table/table.parquet` paths and all four tables' metadata.
Migration files identify the prior release; a first release without a baseline
reports compatibility as unknown rather than unchanged.

Before tagging, align the dated release entry in `CHANGELOG.md`, `pyproject.toml`,
`internacia_builder/__init__.py`, and `CITATION.cff` (`version` and `date-released`);
rebuild and commit exports so their manifest versions match the tag without `v`.
`scripts/check_release_bundle.py --version` fails the release when any of them
disagree. See [versioning-policy.md](versioning-policy.md).

Zenodo deposits come only from the GitHub integration, so the workflow has no
Zenodo step; adding one would create a duplicate deposit per release.
Cite the concept DOI `10.5281/zenodo.20706176` (resolves to the latest version)
or the version DOI listed on the Zenodo record for a specific release.
