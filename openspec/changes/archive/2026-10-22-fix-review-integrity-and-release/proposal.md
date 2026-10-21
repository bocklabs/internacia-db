# Change: repair repository integrity and release guarantees

## Why

The 2026-10-16 review demonstrated that artifact checks accept content corruption,
enrichment renews provenance without applying new observations, and ECOWAS still
marks withdrawn states as current members. Release, migration, and documentation
checks do not consistently establish the advertised consumer guarantees.

The user requested a plan and its implementation after reviewing
`REPOSITORY_REVIEW_2026-10-16.md`; this change implements that authorized scope.

## What Changes

- Restore content, uniqueness, source-freshness, and metadata checks (F01).
- Refresh existing observations only from successful provider responses and retain
  honest retrieval dates; normalize unknown/partial dates before writing (F02/F05).
- Correct ECOWAS and merge confirmed duplicate IDs through aliases (F03/F09).
- Check committed artifacts before rebuilding, test the final staged release,
  enforce quality/version gates, and publish a complete resource bundle (F04/F07).
- Detect recursive schema changes against a named previous release (F06).
- Validate known historical references without adding current-country records (F08).
- Correct member recipes and source/export availability documentation (F10).
- Share scope validation between the validator and analyzer, classify supported
  formal records, and ratchet missing-scope coverage (F11).
- Build documentation on PRs and fix MDX/site-specific links (F12).

No new country profile fields, historical dimension, hosted service, or public
release is introduced. Intentional source-only fields remain source-only.
Previously modified workflow and documentation content is preserved.

## Impact

- Specs: dataset-release, cross-dataset-integrity, countries-profile,
  intblocks-data-quality, contributor-docs, dev-tooling.
- Code: artifact/migration/distribution scripts, enrichment, scope/reference rules,
  CI workflows, regression tests.
- Data: corrected memberships; canonical records and alias migrations; explicit
  classifications. Exports are regenerated using the builder, never hand-edited.
- Compatibility: retired IDs remain resolvable; columnar schemas remain stable.
  Frictionless physical resource names become unique; consumers should select the
  desired table/format explicitly. See CHANGELOG for alias and resource guidance.
