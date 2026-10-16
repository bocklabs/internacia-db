## 1. Plan and baseline
- [x] 1.1 Read review, repository contracts, active proposals, and working-tree changes
- [x] 1.2 Preserve pre-existing changes and record implementation boundaries
- [x] 1.3 Validate this change proposal before implementation

## 2. Data trust (F02, F03, F05)
- [x] 2.1 Add regression cases for unused/failed fetches and newer observations
- [x] 2.2 Apply provider-backed refreshes with honest field provenance
- [x] 2.3 Normalize unknown years and Wikidata date precision; validate before writes
- [x] 2.4 Record ECOWAS departures with official sources and a 12-member current roster

## 3. Artifact and release integrity (F01, F04, F06, F07)
- [x] 3.1 Add end-to-end independent corruption fixtures and strengthen artifact checks
- [x] 3.2 Let artifact-dependent tests select a staging directory
- [x] 3.3 Validate committed snapshots before building and test final release staging
- [x] 3.4 Implement recursive source/export migration diffs and previous-release baselines
- [x] 3.5 Generate unique resource names and validate complete/channel-specific bundles
- [x] 3.6 Preserve existing mirror configuration while enforcing quality/version checks

## 4. Consumer semantics and content (F08–F11)
- [x] 4.1 Validate historical/territory references and document safe historical joins
- [x] 4.2 Reconcile confirmed duplicate records and retain retired IDs as aliases
- [x] 4.3 Fix current-full-member recipes and add status regression coverage
- [x] 4.4 Share scope checks, classify supported formal records, and ratchet coverage
- [x] 4.5 Update counts, source/export documentation, contributor guidance, and changelog

## 5. Documentation and verification (F12)
- [x] 5.1 Add a PR website build and repair MDX and plugin-external links
- [x] 5.2 Run focused regressions and lint during implementation
- [x] 5.3 Rebuild exports and quality reports through supported generators
- [x] 5.4 Run full tests/coverage, source validators, artifact checks, and documentation gates
- [x] 5.5 Run website build/typecheck and strict OpenSpec validation
- [x] 5.6 Record final outcomes and any evidence-dependent deferrals without publishing

## Completion evidence

See [verification.md](verification.md): 369 staged-suite tests plus two additional
atomic-write regressions pass (371 distinct tests), combined package coverage is
54.26%, source validators have zero errors, the complete artifact guard passes,
and website, distribution, documentation, lint, and OpenSpec checks pass. MSF and
CANTO remain the two explicitly gated NGO taxonomy exceptions. No publication or
commit was performed.
