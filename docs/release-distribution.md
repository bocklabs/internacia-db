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

The workflow checks committed snapshot freshness before rebuilding. It tests and
checks the final `.release-datasets` staging directory, enforces the shared quality
gate and tag-version consistency, then publishes that exact bundle. Every
`datapackage.json` resource is attached. Hugging Face gets a separate validated
Parquet-only descriptor with `table/table.parquet` paths and all four tables' metadata.
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
