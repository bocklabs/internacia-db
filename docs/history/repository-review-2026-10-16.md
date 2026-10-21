# Internacia DB repository review

**Review date:** 2026-10-16

**Base commit:** `f0472628e06f12bf95ee20ed493094bf1eff0e86`

**Dataset version inspected:** `2.1.0`
**Scope:** Python tooling, validation, exports, CI and releases, documentation website, repository governance, and data contents.

## Overall assessment

Internacia has a solid foundation: explicit schemas, field provenance, identifier aliases, multiple distribution formats, executable query examples, and a substantial test suite. All **319 tests passed**, with **50.18% package coverage**. Both source validators report zero errors. The largest opportunities concern the strength of the guarantees around those checks: artifact validation can miss corruption, enrichment can make stale values appear newly retrieved, and internally consistent rosters can still be factually wrong.

Prioritize artifact integrity, honest freshness metadata, the ECOWAS roster, and release validation before expanding the catalogue. The report contains **12 prioritized findings**, followed by smaller improvements and a suggested work sequence. No implementation changes are included.

The checkout contained pre-existing modifications to release files, generated datasets, quality reports, and documentation, plus untracked work directories. Those were preserved. Code findings below concern committed logic unless explicitly marked as a working-tree observation. The existing historical reviews were retained; their old counts and factual claims were not treated as current evidence.

## Verification and limits

| Check | Result |
|---|---|
| `python -m pytest tests/ --cov=internacia_builder --cov-report=term` | 319 passed; 50.18% coverage; configured 49% gate passed |
| `python scripts/validate_countries.py --json` | 256 records; 0 errors; 0 warnings |
| `python scripts/validate_intblocks.py --json` | 1,272 records; 0 errors; 114 warnings, all for missing formal-record `scope_category` |
| `python scripts/check_generated_artifacts.py` | Passed on the existing working-tree artifacts |
| Full build with `--output-dir <temporary-directory>` | Passed without replacing repository exports |
| Fresh-build verification | Artifact guard passed; full JSONL and Parquet record comparisons matched the existing countries, intblocks, and blocktypes exports after sorting by primary key |
| Deliberately corrupted temporary artifact copy | Also passed; see F01 |
| `python scripts/builder.py analyze-quality --output <temporary-directory>` | 1,528 records; 0 reported issues; see F11 for the difference from validator warnings |
| `python scripts/generate_data_dictionary.py --check` | Passed |
| `python scripts/check_doc_counts.py` | Passed: 256 countries, 1,272 intblocks, 78 blocktypes |
| `python scripts/check_markdown_links.py` | Passed: 535 links including this report; website warnings are a separate check |
| `openspec validate --all --strict --no-interactive` | 41 items passed |
| Website production build using an external output directory | Failed on existing untracked `docs/publishing-huggingface.md:6`; also emitted unresolved-link warnings |

Python checks used the existing `.venv`, running Python 3.13.7. Its Typer 0.26.3, DuckDB 1.5.3, and pytest 9.0.3 differ from the declared pins of 0.26.8, 1.5.4, and 9.1.1. Results therefore establish behavior in this local environment, not a clean installation of every pinned dependency or the full CI matrix. The website check used existing `node_modules`, without reinstalling dependencies. An offline lock check could not resolve uncached packages and is inconclusive; direct comparison found the runtime dependency pins in `uv.lock` and `pyproject.toml` agree.

Content statistics were queried from the exported DuckDB database, opened read-only. Its four metadata rows share version `2.1.0`, commit `f047262`, and build timestamp `2026-09-17T17:02:35Z`. Source YAML was inspected only where needed to review a concrete record or validation behavior. `data/_legacy/` was excluded. External factual verification was selective, using primary sources; this is not a complete fact check of 1,272 rosters. Live link sweeps, vulnerability audits, and linters were not rerun.

## Priority index

P1 means a current data error or a significant integrity/release guarantee gap. P2 means a correctness or maintenance issue to address in the next improvement cycle. Effort estimates are relative, not delivery commitments.

| ID | Priority | Finding and recommended action | Effort |
|---|---|---|---|
| F01 | P1 | Artifact guard accepts changed values, duplicates, and missing metadata; compare normalized content and validate committed files before rebuilding | Medium |
| F02 | P1 | Enrichment renews provenance without refreshing existing values; tie retrieval dates to successful retrieval and application | Medium |
| F03 | P1 | ECOWAS still includes three withdrawn states as members; record their departures and change the current count to 12 | Small |
| F04 | P1 | Release workflow tests before building and omits the quality gate; validate the exact artifacts being published | Medium |
| F05 | P2 | Enrichment creates invalid or falsely precise dates; normalize unknown years and honor date precision before writing | Small–medium |
| F06 | P2 | Migration diffs miss nested contract changes and do not persist release baselines; compare complete contracts against a known prior release | Medium |
| F07 | P2 | Data package has duplicate resource names and references ten unattached release files; validate descriptors against each distribution bundle | Small–medium |
| F08 | P2 | Historical membership edges contradict the documented country join guarantee; define and validate historical references explicitly | Small initially |
| F09 | P2 | Duplicate organization records remain active under separate IDs; merge confirmed duplicates using aliases | Medium |
| F10 | P2 | Documented current-member filter includes partners and other participation roles; use explicit status sets | Small |
| F11 | P2 | Quality analyzer and validator disagree on scope warnings; share rule orchestration and complete formal-record classifications | Medium |
| F12 | P2 | Documentation build is checked only after merge; add a PR build and fix website-specific links | Small–medium |

## Findings

### F01 — Artifact checks do not establish content equivalence or freshness

**Evidence:** [artifact checker, lines 95–139](scripts/check_generated_artifacts.py#L95), [membership checks](scripts/check_generated_artifacts.py#L155), [validation workflow](.github/workflows/validate.yml#L72), and [consumer guarantee](docs/ai-consumers.md#L46).

Most primary-table comparisons reduce records to sets of IDs. Set equality hides duplicate rows and changes to every other field. Membership comparisons mostly check counts. Missing sidecars and missing `_meta` dataset rows are omitted from identity comparison rather than rejected. The blocktypes source is not compared because its source entry is `None`.

**Demonstrated:** in a temporary copy, the checker returned exit code 0 after all of these changes together:

- Changed France's DuckDB display name without changing the Parquet/JSONL values.
- Added a duplicate France row to DuckDB.
- Changed the NATO/US membership status to `INVALID_STATUS`.
- Removed `countries.meta.json` and the blocktypes `_meta` row.
- Changed France's source YAML name without rebuilding any export.

Its output still said all formats and sources agree. These are isolated corruption probes, not claims that the original artifacts contain those changes.

CI compounds the gap by running `build` at workflow line 73 before the “committed dataset artifacts” check at line 94. Rebuilding overwrites the files whose freshness that step claims to establish. Improving field comparisons alone will not make this ordering detect stale committed exports.

**Recommendation:** check committed artifacts before rebuilding; build separately into a temporary directory for integration tests. Compare normalized source projections and row values for every supported format, allowing explicitly documented differences between full and columnar exports. Check actual row counts and key uniqueness independently, compare membership edge tuples, require every expected metadata record, and check schema hashes and blocktypes against their source. Exclude volatile build timestamps from reproducibility comparisons while still requiring internal identity consistency.

**Acceptance:** each corruption above independently fails an end-to-end checker test; a source-only name edit fails committed-artifact freshness; a clean build passes.

### F02 — Scheduled enrichment can make old values appear freshly retrieved

**Evidence:** [field update conditions](scripts/enrich_countries.py#L446), [provenance synchronization](scripts/enrich_countries.py#L393), and [scheduled enrichment invocation](.github/workflows/enrichment-check.yml#L36).

The scheduled command does not pass `--force`. Existing population, area, and Gini structs therefore remain unchanged even when newer observations are fetched. `sync_provenance_from_record`, however, replaces their `retrieved_at` dates with today. Native-name and timezone provenance is also restamped without requiring that the corresponding existing value was refreshed.

**Demonstrated:** a population of 100 from 2020 stayed at 100/2020 when enrichment received a World Bank observation of 200/2025, while its provenance changed from `2020-01-01` to `2026-10-16`. The same restamping path is reachable with empty indicator responses.

**Recommendation:** distinguish missing-field backfills from reviewed refreshes. Track successful retrieval and the actual field decision, update only fields justified by that response, and preserve retrieval dates for untouched values. Report partial provider failures explicitly. Do not fix this merely by applying `--force` globally: that can overwrite curated values without resolving provenance semantics. Also distinguish an intblock metadata touch from a roster verification; [the current stamp helper](scripts/enrich_intblocks.py#L330) treats enrichment as record verification.

**Acceptance:** an older stored observation can be refreshed under an explicit policy; failed or unused fetches do not advance its retrieval date; a no-op run preserves provenance.

### F03 — ECOWAS contains a verified stale roster

**Evidence:** [ECOWAS source roster](data/intblocks/economic/ECOWAS.yaml#L16) and [stored member count](data/intblocks/economic/ECOWAS.yaml#L127).

`ML`, `BF`, and `NE` are all marked `member`, and `membership_count` is 15. ECOWAS states that their withdrawal took effect on **2025-01-29**, and its current published roster contains 12 states. Transitional travel and trade arrangements do not make them current members. Sources: [official withdrawal statement](https://www.ecowas.int/press-statement-2/) and [official ECOWAS overview and current roster](https://www.ecowas.int/about-ecowas/).

**Recommendation:** preserve those three historical edges as `former_member`, set `left: '2025-01-29'`, change the current member count to 12, and attach specific roster provenance and a verification date. Rebuild through the normal pipeline. Review dependent ECOWAS institutions individually rather than automatically copying the same changes into their rosters.

**Acceptance:** current-full-member queries return 12; the three former members remain discoverable with their departure dates. This example should become a regression fixture for current-versus-historical membership semantics.

### F04 — Release validation does not cover the final published build

**Evidence:** [release workflow](.github/workflows/release.yml#L30), [PR quality gate](.github/workflows/validate.yml#L108), and [metadata version source](internacia_builder/manifest.py#L32).

The release job runs tests before rebuilding exports. Tests reading on-disk datasets therefore exercise the checked-in artifacts, while the subsequently rebuilt artifacts are published after only the limited consistency check described in F01. The release workflow also omits the analyzer's CRITICAL/IMPORTANT gate, documentation drift checks, and coverage enforcement present in PR validation. This ordering exists in committed `HEAD`, as well as in the working-tree workflow.

**Recommendation:** use a shared validation job or command for PR and release behavior. Check committed freshness first, build into staging, run artifact-dependent tests and the quality gate against staging, and publish that exact directory. Assert that the tag version agrees with package and manifest versions. Keep optional mirror failures from leaving the primary release in an ambiguous state; make distribution steps resumable.

**Acceptance:** an introduced export regression or high-priority analyzer issue prevents publication; tests after the build read the same artifact paths that the release action uploads.

### F05 — Enrichment emits invalid years and ignores Wikidata date precision

**Evidence:** [country fallbacks](scripts/enrich_countries.py#L452), [inception parser](scripts/enrich_intblocks.py#L290), and [year validation](internacia_builder/validate/country_rules.py).

Country fallback population and area values use `year: 0`. A synthetic Wikidata population response produced that value, and `check_country_indicator_years` immediately returned `INVALID_INDICATOR_YEAR`. Although the export cleaner later normalizes zero to null, source validation runs before export cleaning, so it cannot rescue this path.

The inception parser uses only the textual timestamp and ignores its precision. A year-precision claim with `+1950-00-00T00:00:00Z` produced `1950-00-00`; year-precision timestamps with nonzero month/day fields can also imply unjustified day precision. Wikidata defines year, month, and day precision separately in its [date documentation](https://www.wikidata.org/wiki/Help:Dates).

**Recommendation:** omit unknown observation years in authored YAML under the current source schema, which accepts an integer when `year` is present; continue exporting unknown years as null. Read usable point-in-time qualifiers where available, without substituting the retrieval year. Respect Wikidata precision when emitting `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`; reject invalid calendar components. Validate enriched records before writing them.

**Acceptance:** fallback records pass the existing year validator; year-only and month-only claims preserve their precision; failed validation leaves the original source file intact.

### F06 — Migration reports underdescribe compatibility changes

**Evidence:** [type signature and diff implementation](scripts/generate_schema_migration.py#L32), [release baseline handling](.github/workflows/release.yml#L42), and [current migration tests](tests/test_schema_migration.py).

Only top-level property names and shallow type signatures are compared. Changing an array's item type from string to integer produced an empty diff. Nested struct changes, required-property changes, enum changes on already typed properties, and many constraints are similarly invisible. Export schemas are separately maintained in Python, so JSON Schema comparison alone does not describe every Parquet/DuckDB compatibility change.

The stored baseline exists, but the release workflow refreshes it only inside an ephemeral runner. That copy operation does not persist the baseline for the next tag. Unless separately maintained, later releases can compare against an older baseline rather than their immediate predecessor.

**Recommendation:** compare recursive source and export contracts, distinguish additive and breaking changes, and record the baseline version/hash. Load the baseline from an explicit previous release or persist a reviewed baseline update. A missing baseline should be clearly reported as unknown rather than interpreted as evidence of no change.

**Acceptance:** nested item-type changes, enum narrowing, added required fields, and Arrow-only changes are detected; two successive release fixtures compare against the correct predecessor.

### F07 — Distribution metadata does not match the distributed resource bundle

**Evidence:** [data package generator](internacia_builder/export.py#L296), [generated descriptor](data/datasets/datapackage.json), and [release asset list](.github/workflows/release.yml#L188).

The descriptor reuses `countries` four times, `intblocks` four times, and several other names twice. Present resource names must be unique within a package under the [Frictionless Data Resource specification](https://specs.frictionlessdata.io/data-resource/#name). Name-based selection is ambiguous even before a consumer attempts to load a file.

The GitHub asset list omits **ten paths referenced by the descriptor**: the countries/intblocks full CSVs, lite CSVs, lite Parquet files, JSON arrays, and plain JSONL files. A consumer downloading all declared release assets still cannot resolve the complete package. The optional Hugging Face upload includes an even smaller subset while uploading the same descriptor.

**Recommendation:** give each physical resource a unique name, and either publish its complete referenced bundle or generate a descriptor specific to the files available in that channel. Derive upload lists from a shared artifact inventory rather than maintaining several independent lists.

**Acceptance:** resource names are unique, and every descriptor path resolves inside a simulated GitHub/Hugging Face bundle. Validate the descriptor as part of build tests.

### F08 — Historical country edges do not satisfy the advertised join contract

**Evidence:** [membership exporter contract](internacia_builder/export.py#L403), [reference validator](internacia_builder/validate/cross_rules.py#L876), [Danube Commission historical edge](data/intblocks/water/DANUBECOM.yaml#L96), and [Warsaw Pact historical edge](data/intblocks/military/WARSAWPACT.yaml#L52).

The exporter says country, territory, and historical-country entries all join to `countries.code`. An anti-join found two exceptions: `DANUBECOM → SU` and `WARSAWPACT → SU`, both former Soviet Union memberships. `SU` has no country row. The reference validator checks only entries whose type is exactly `country`, so these records pass.

**Recommendation:** document the historical-ID exception and use left joins where history matters. Validate country and territory references against the current dimension and historical references against an explicit historical registry or controlled exception list. A separate historical dimension would require a schema proposal. Do not silently map `SU` to `RU` or add it as a current ISO entity.

**Acceptance:** consumers can account for every historical edge without losing it in an inner join; an unknown historical identifier is reported distinctly from an expected historical reference.

### F09 — Confirmed duplicate entities remain separate active records

**Evidence:** [duplicate-ID exceptions](data/schemas/intblocks_completeness.yaml#L123), [COL](data/intblocks/cultural/COL.yaml), [COMMLEARN](https://github.com/datenoio/internacia-db/blob/f0472628e06f12bf95ee20ed493094bf1eff0e86/data/intblocks/education/COMMLEARN.yaml), [UNASUR](data/intblocks/political/UNASUR.yaml), and [USAN](https://github.com/datenoio/internacia-db/blob/f0472628e06f12bf95ee20ed493094bf1eff0e86/data/intblocks/customs/USAN.yaml).

`COL` and `COMMLEARN` describe Commonwealth of Learning with the same Wikidata ID and 56 full members each. `ABCANZ` and `ABCZNZ` similarly duplicate the armies program. `UNASUR` and `USAN` share an entity ID but expose different current-full-member counts, 12 and 8. The suppression configuration already labels these as pending maintainer merges; they are not newly discovered identity collisions.

**Recommendation:** resolve those explicit merge debts, select canonical IDs, reconcile their sourced rosters, redirect organizational references, and retain retired IDs in the alias mechanism. Preserve legitimate distinctions such as World Bank reference groupings; do not merge every shared Wikidata ID automatically. Give remaining suppressions a rationale, owner, and review date.

**Acceptance:** one active canonical record per confirmed duplicate entity; aliases resolve old IDs; organization-density queries do not double-count these entities. Confirm the correct UNASUR roster from authoritative evidence before merging its records.

### F10 — The documented current-member predicate includes non-member roles

**Evidence:** [consumer membership guidance](docs/ai-consumers.md#L145) and [status vocabulary](data/schemas/includes_status.yaml).

The suggested predicate `status NOT IN ('former_member')` includes partners, participants, funders, recipients, and other roles. On the existing BRICS record it returns **21** edges, while `status IN ('member', 'founding_member')` returns **11**. Those figures demonstrate the predicate difference within this dataset; they do not independently verify BRICS's real-world roster.

**Recommendation:** give separate, explicit recipes for current full membership and broader current participation. Use `status IN ('member', 'founding_member')` for the former, and state which additional roles a broader query includes. Do not conflate edge status with whether the organization itself is currently active.

**Acceptance:** documentation tests assert expected inclusion/exclusion for full members, former members, partners, observers, and funding relationships.

### F11 — Quality reporting omits warnings detected by the standalone validator

**Evidence:** [scope validator](internacia_builder/validate/intblocks.py#L241), [validator orchestration](internacia_builder/validate/intblocks.py#L418), and [analyzer orchestration](internacia_builder/build.py#L409).

The standalone validator emits 114 scope-category warnings, while a fresh analyzer run reports zero issues and 100% clean records. There are 192 null scopes in total; 114 belong to formal records and trigger the explicit warning policy. Filtering by `scope_category = 'igo'` can therefore exclude formal bodies merely because classification is missing.

Shared low-level rule functions already exist, but the two entry points maintain separate check lists. The analyzer still occupies most of the 964-line `build.py`, while `quality.py` imports its implementation from the build module. This structure permits report parity to drift.

**Recommendation:** put rule selection and issue production behind one shared runner, keeping severity and reporting adapters separate. Include the scope warning in quality reports. Classify the 114 formal records using the existing inclusion policy, then ratchet a missing-scope threshold; do not automatically assign every unclassified record to `igo`.

**Acceptance:** the same fixture yields the same issue codes from validation and analysis, with intentional severity differences documented; formal-record scope coverage has a measurable gate.

### F12 — Website failures are discovered after merge

**Evidence:** [documentation deployment trigger](.github/workflows/deploy-docs.yml#L3), [validation path filters](.github/workflows/validate.yml#L3), and [lenient website link setting](website/docusaurus.config.ts#L29).

The website builds on pushes to `main` and manual dispatch, without a PR build. Website-only changes do not trigger the Python validation workflow either. The repository link checker verifies filesystem targets, so it cannot establish that links to root files resolve through the website's docs plugin.

The local production build emitted **25 unresolved Markdown-link warnings**, including links to README, attribution, changelog, and agent guides outside the configured docs content root.

**Working-tree observation:** that build then failed on the pre-existing untracked `docs/publishing-huggingface.md:6`, where the angle-bracket URL is parsed as MDX syntax. This is not a defect attributed to committed `HEAD`. Replace it with a normal Markdown link before including that guide in a commit.

**Recommendation:** run a build-only website job on PRs touching docs, website files, or site dependencies, and keep publishing permissions confined to deployment. Fix plugin-external links using valid site routes or repository URLs. Once the known warnings are resolved, make broken links fail the build. Build the final documentation tree, including generated pages, before merging.

**Acceptance:** the current MDX example is caught in PR validation; the site builds without unresolved-link warnings; no publication occurs during PR checks.

## Content coverage and improvement opportunities

These are measured gaps, not automatic assertions that every null needs a value.

| Measure | Observed result | Suggested treatment |
|---|---:|---|
| Current ISO-country records | 249 of 256 | Preserve explicit status filtering for the other seven |
| UN status | 193 members, 2 observers, 61 non-members | Retain this useful distinction and its query tests |
| Membership edges | 58,767 | Preserve status/type distinctions when aggregating |
| Membership edges with `joined` | 16,393 (27.9%) | Add dates from authoritative rosters where available; do not infer them from founding dates |
| Membership edges with `left` | 333 | Preserve history when correcting current rosters |
| Intblocks without scope category | 192 (15.1%) | Start with the 114 formal-record warnings |
| Intblocks without Wikidata ID | 170 (13.4%) | Review existing exclusions before treating these as defects |
| Intblocks without headquarters | 393 (30.9%) | Prioritize applicable standing organizations; many treaties/groupings need no headquarters |
| Intblocks without founded value | 96 (7.5%) | Prefer sourced dates with honest precision |
| Intblocks without last verification date | 309 (24.3%) | Prioritize large, frequently queried rosters; separate verification from enrichment touches |
| Country population / area with unknown year | 34 / 40 | Keep null when genuinely unknown; capture source observation qualifiers when available |
| Countries without Gini | 86 | Existing scope only; fill where supported, not to satisfy a blanket completeness target |
| Countries without World Bank region / adminregion | 8 / 39 | Expected policy gaps; do not backfill them indiscriminately |

Coverage expansion should follow the existing discovery backlog and inclusion policy. The measurable near-term value is correcting memberships, classifying formal bodies, reconciling duplicates, and improving field-specific evidence. This review does not propose adding socioeconomic country-profile fields.

Historical review recommendations also need date-aware rechecking. For example, this checkout's OPEC count of 11 should not be “fixed” by blindly re-adding the UAE: the [U.S. Energy Information Administration records its withdrawal effective 2026-05-01](https://www.eia.gov/todayinenergy/detail.php?id=67804). The old reviews are useful history, not a current roster authority.

## Smaller code and repository improvements

| Area | Evidence | Improvement |
|---|---|---|
| Test depth | Local coverage: build 5%, quality reports 3%, export 54%; aggregate 50.18% | Add focused CLI integration and failure-path tests for F01–F07. Do not raise a global percentage without covering these failure modes. Include enrichment scripts in a separate coverage view. |
| Source/export documentation | [README export table](README.md#L346) omits `includes.left` and calls `last_verified` source-only, although both exist in the columnar schema | Generate a source-versus-export availability matrix, complementing the generated source dictionary. Assert deliberate exclusions and exported columns in tests. |
| Context retained across formats | Full JSONL contains notes on 943 intblocks, founding members on 374, and membership-applicability markers on 8; those fields are absent from Parquet/DuckDB | Explain these differences at the preferred access entry point. Consider exporting `notes` and applicability markers through an approved schema change, since they explain interpretation and empty rosters. Deliberate omissions are not themselves corruption. |
| OpenSpec lifecycle | 27 active changes: 23 fully checked off and 4 partial; strict validation passes | Review and archive completed changes, reconcile implemented deltas into canonical specs, and explicitly retain deferred tasks. Archive status should reflect shipped work, not just checked boxes. |
| Dependency maintenance | Runtime pins are duplicated across requirements and project metadata; CI installs with pip rather than the committed lock; Dependabot has no npm entry | Choose a declared source of dependency truth, generate/check duplicate pin files, and either enforce the lock or explain its role. Add npm maintenance for the docs site. No vulnerability claim is made here. |
| CI path coverage | Validation filters omit release/enrichment workflow changes and several configuration files; docs deploy only after merge | Cover workflow, lock, pre-commit, and website changes with appropriate jobs or a small always-running workflow check. Avoid required-status checks being silently absent for relevant changes. |
| Build failure recovery | Writers update files in place; [DuckDB creation](internacia_builder/export.py#L453) removes the old database first | Stage a complete build, validate it, then replace the output bundle. A failed build should preserve the previous usable artifacts. |
| Cleaning behavior | [Cleaner](internacia_builder/clean.py#L8) copies only the outer record and mutates nested dictionaries | Either document in-place behavior or copy nested data intentionally. A probe changed an input member ID from `None` to `''` after cleaning. Add an input-preservation test only if purity is the intended contract. |
| Suppression governance | Duplicate/acronym exceptions include entries explicitly awaiting merges or cleanup | Track these as owned tasks with review dates, keeping permanent legitimate exceptions separate from temporary debt. |

## Suggested work sequence

1. **Repair data trust:** fix ECOWAS; prevent false provenance renewal; correct fallback date handling. Add small regression fixtures with known input and expected behavior.
2. **Strengthen publication guarantees:** implement F01's content checks and committed-before-build ordering; test staging artifacts during releases; validate the actual data package bundle.
3. **Align consumer semantics:** fix membership recipes, historical-reference guidance, export-availability documentation, and duplicate canonicalization. Follow the alias and versioning policies.
4. **Make maintenance observable:** unify validator/analyzer rule selection, classify formal-record scope gaps, build docs on PRs, and reconcile completed OpenSpec work.

Bug fixes restoring documented behavior can follow the repository's ordinary contribution workflow. New historical dimensions, new exported fields, and changes to compatibility policy should use the required OpenSpec proposal process before implementation.

## Reproduction queries

Run these against `data/datasets/internacia.duckdb`, opened read-only. They describe the inspected snapshot, so counts should change after the recommended repairs.

```sql
-- F03: all three withdrawn states are still recorded as members.
SELECT country_code, status, "left"
FROM memberships
WHERE intblock_id = 'ECOWAS' AND country_code IN ('ML', 'BF', 'NE');

-- F08: two historical membership edges have no current-country row.
SELECT m.*
FROM memberships m
ANTI JOIN countries c ON m.country_code = c.code;

-- F10: broader participation returns 21 BRICS edges; full membership returns 11.
SELECT
    count(*) FILTER (WHERE status NOT IN ('former_member')) AS broad_participation,
    count(*) FILTER (WHERE status IN ('member', 'founding_member')) AS full_members
FROM memberships
WHERE intblock_id = 'BRICS';

-- F11: 114 formal records lack the optional scope classification.
SELECT count(*)
FROM intblocks
WHERE status = 'formal' AND scope_category IS NULL;
```

The integrity reproduction for F01 used copies of `data/datasets`, `data/countries`, and `data/intblocks` under a temporary root, modified only those copies, and invoked:

```bash
python scripts/check_generated_artifacts.py \
  --root "$temporary_root" \
  --datasets-dir "$temporary_root/data/datasets"
```

The expected result after strengthening the guard is a nonzero exit for each independently introduced corruption, rather than the current success message.
