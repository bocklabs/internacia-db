# Implementation verification — 2026-10-16

The implementation follows the [plan](tasks.md) and [design](design.md) for the
[repository review](../../../docs/history/repository-review-2026-10-16.md). Changes are local;
no commit, release, or remote dataset publication was performed.

## Implemented outcomes

| Findings | Result |
|---|---|
| F01 | Full source/projection comparisons, independent uniqueness/count checks, edge-tuple checks, required metadata and schema hashes; negative corruption fixtures |
| F02/F05 | Provider-backed refreshes preserve curated sources, observation years, and unchanged provenance; partial fetches are reported; fallback years and inception precision are honest; source writes validate before atomic replacement |
| F03 | ECOWAS has 12 current members and retains BF/ML/NE as former members with departure date 2025-01-29 and official provenance |
| F04 | Committed checks precede builds; tests select the final staging directory; releases enforce quality, descriptor, and version checks |
| F06 | Recursive source and Arrow contract differences, including nested types and constraints; explicit prior-release identity and unknown-baseline state |
| F07 | Unique table/format resource names, complete GitHub/Zenodo bundles, and a separately validated four-table Hugging Face bundle |
| F08 | Known historical identifiers such as SU are explicit exceptions to current-country joins; unknown historical references fail validation; safe left joins are documented |
| F09 | COMMLEARN → COL, ABCZNZ → ABCANZ, USAN → UNASUR aliases preserve retired IDs; richer records and membership history are retained |
| F10 | Full-member recipes explicitly select member/founding_member and are tested using the actual documentation query |
| F11 | Scope warnings share one rule; 111 classifications and one duplicate removal reduce missing formal scope from 114 to two documented NGO exceptions; both count and exception identity are gated |
| F12 | PR website builds/typechecks have read-only permissions; deployment is excluded for PRs; repository links resolve before rendering; MDX URL issues are repaired |

The current snapshot contains 256 countries, 1269 intblocks, 78 blocktypes, and
58694 membership edges. Removed duplicate records account for 73 duplicate edges;
country identifiers and columnar schema hashes remain unchanged.

Supporting improvements include generated columnar availability documentation,
a maintained dataset-card template that preserves the pre-existing Hugging Face
configuration, npm dependency maintenance, and rebuilt monthly enrichment PRs.

## Acceptance results

| Gate | Observed result |
|---|---|
| Full suite against the staged build | 369 passed; all final implementation modules exercised |
| Added atomic-write boundary cases | 2 passed separately; 371 distinct tests verified overall |
| Package coverage, combined runs | 54.26% (baseline 50.18%); configured 49% gate passes |
| Countries validation | 256 records; 0 errors, 0 warnings |
| Intblock validation | 1269 records; 0 errors, 2 documented scope warnings |
| Fresh full-format build | Passed; generated snapshot and data card rebuilt from sources/template |
| Artifact verification | All source projections, values, keys, schemas, row counts, aliases, and metadata agree |
| Quality gate | 0 CRITICAL/IMPORTANT issues; only MSF/CANTO scope advisories remain |
| Migration smoke check against original HEAD | Baseline available with commit identity; source/export schemas unchanged |
| Real HF staging bundle | All four table/config paths, manifests, sidecars, and descriptor verified locally |
| Documentation checks | Current counts and generated dictionary match; internal Markdown links resolve |
| Ruff and workflow checks | Passed; shell/embedded Python parses; committed-before-build ordering and PR deployment exclusion tested |
| Website typecheck | Passed |
| Website production build | Passed after the translated-guide correction; zero unresolved-link warnings |
| OpenSpec | 42 items pass strict validation |

The first full test run identified two expected snapshot-count changes from the
roster correction and duplicate consolidation; those expectations were updated.
The content guard also rejected an intermediate merged-COL parent projection,
and the final rebuild now carries `partof: [COMMONWEALTH]`. An initial scope-classification edit also placed some provenance entries outside
their list; validation caught this, and I corrected the placement. These failures
were resolved before acceptance rather than bypassed.

## Deliberate boundaries

- MSF and CANTO remain visible LOW-priority scope warnings. They are respectively
  an NGO and an industry association, and assigning either to `igo` would misstate
  the existing four-value taxonomy. The explicit exception identities and a
  maximum of two omissions prevent unrelated scope regressions.
- Observation coverage gaps, absent headquarters where inapplicable, and the
  documented World Bank classification exclusions are preserved.
- No new country fields or historical-country dimension were introduced.
- Older completed OpenSpec proposals were not bulk-archived without verifying
  their deployment state. Optional architecture and coverage expansion beyond
  the reviewed corrections remains separate work.
- Local checks use the existing Python 3.13.7 environment and installed website
  dependencies. CI's Python matrix and actual external publishing were not run.
