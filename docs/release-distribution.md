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

The workflow checks committed snapshot freshness before rebuilding. It tests and
checks the final `.release-datasets` staging directory, enforces the shared quality
gate and tag-version consistency, then publishes that exact bundle. Every
`datapackage.json` resource is attached. Hugging Face gets a separate validated
Parquet-only descriptor with `table/table.parquet` paths and all four tables' metadata.
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
