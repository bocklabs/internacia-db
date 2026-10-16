## Context

The review contains 12 findings. Existing work includes optional Hugging Face
publishing changes; these must survive integration. Baseline: 319 passing tests,
0 country errors, 0 intblock errors, and 114 formal-record scope warnings.

## Decisions

1. Compare normalized source records against full JSON/YAML and explicit Arrow
   projections. Sort by primary key, reject duplicates, and compare actual edge
   tuples. Require complete manifests, sidecars, DuckDB metadata, and schema hashes.
   Timestamp changes between separate builds are expected; mismatched identity
   within one bundle is an error.
2. Keep `data/datasets` as the committed consumer snapshot. Validate it before CI
   rebuilds anything; pass an artifact directory to tests through an environment
   variable so fresh staging builds receive the same tests.
3. Refresh provider-backed country fields when a usable response is available.
   Preserve manually curated sources unless forced; never fall back to less
   authoritative values just because a provider failed. Preserve provenance on
   no-op/failed fetches. Unknown source years are omitted and export as null.
4. Use existing aliases for duplicate consolidation. Prefer COL, ABCANZ, and
   UNASUR as canonical IDs; preserve richer fields and sourced membership history.
   Resolve conflicting rosters from primary sources before changing their status.
5. Keep historical IDs outside the current-country dimension. A small explicit
   historical-reference registry documents allowed IDs and validates their use.
6. Compare nested source JSON Schemas and Arrow contracts. Release baselines come
   from an explicit previous release ref, not an unpersisted runner-local copy.
   Missing baselines are reported as unknown, not unchanged.
7. Use one physical resource name per table/format and derive release resources
   from the descriptor. Build channel-specific descriptors for partial mirrors.
8. Reuse the existing scope rule seam, sharing it between entry points instead
   of extracting the entire analyzer as an unrelated refactor. Classify only
   records whose existing evidence supports the chosen category.
9. Run documentation build/type checks on PRs without deployment permissions;
   rewrite plugin-external links at render time to repository URLs so repository
   Markdown links remain valid.

## Rollback and verification

The initial working-tree diff is backed up outside the repository. Code changes
are reviewable without committing or publishing. Alias sources retain old IDs;
record history is preserved. Regenerated exports can be reproduced from sources.
Regression fixtures exercise individual corruption/fetch/date/descriptor cases.
Final proof includes lint, full tests with coverage, both validators, a complete
fresh build, artifact checks, quality reports, documentation checks and website
build, and strict OpenSpec validation.
