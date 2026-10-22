# Change: One enrichment pull request per source, with auto-merge for safe changes

## Why
The monthly enrichment opens one large pull request mixing World Bank indicators,
classifications, Wikidata names and time zones. It is hard to review, so it waits, and one doubtful
value holds back hundreds of routine refreshes. Most changes are routine: a new population
estimate, a missing name filled in.

## What Changes
- `data/schemas/enrichment_sources.yaml` assigns enriched fields to sources and sets numeric
  thresholds. `internacia_builder/enrichment_sources.py` and `scripts/enrichment_split.py` split
  one enrichment run into per-source changes and decide whether each needs review.
- `enrichment-check.yml` opens one pull request per source on `enrichment/<source>`. Pull requests
  whose changes only fill empty values, add items or stay within the thresholds are set to
  auto-merge; the others get `needs-review` and a reviewer. Classifications and unassigned fields
  are always reviewed.
- The changed-record rule (`last_verified`) skips metadata-only intblock changes.

## Impact
- Affected specs: dev-tooling
- Affected code: `.github/workflows/enrichment-check.yml`, `internacia_builder/freshness.py`
- Supersedes the workflow change in #26 (App token for the enrichment PR), which this includes.
