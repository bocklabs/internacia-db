# Change: Monthly release train

## Why
Releases are cut by hand: a maintainer has to decide the level, date the CHANGELOG, bump the
version in five files, rebuild the descriptors and push a tag. The data changes every month
(enrichment, roster fixes), but releases are rare, so consumers wait. The SDK and API cannot
follow releases automatically because nothing announces them.

## What Changes
- `internacia_builder/release.py` and `scripts/prepare_release.py`: compare the working tree with
  the last `vX.Y.Z` tag, choose PATCH or MINOR from docs/versioning-policy.md (stop on MAJOR),
  and write the bump (CHANGELOG entry with a data-change summary, `pyproject.toml`,
  `internacia_builder/__init__.py`, `CITATION.cff`, `uv.lock`, rebuilt descriptors).
- `.github/workflows/release-train.yml` (monthly and on demand) opens or refreshes the release PR
  on `release/next`; `.github/workflows/release-tag.yml` tags its merge commit; `release.yml`
  then publishes as before and sends `repository_dispatch` (`internacia-db-release`) to
  internacia-python and internacia-api.
- `migration.vX.Y.Z.json` gains a `data` section: record ids added, removed and changed per
  dataset, and membership edges added, removed and changed.
- The bot workflows use the internacia-bot GitHub App (D7); without its secrets they report the
  plan and stop.

## Impact
- Affected specs: dataset-release
- Affected code: `internacia_builder/release.py`, `scripts/prepare_release.py`,
  `scripts/generate_schema_migration.py`, `.github/workflows/release*.yml`
- Needs: the internacia-bot App installed on internacia-db (contents and pull requests write)
  and, for the dispatch, on internacia-python and internacia-api (contents write).
