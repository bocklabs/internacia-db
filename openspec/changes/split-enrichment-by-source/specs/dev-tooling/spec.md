## MODIFIED Requirements

### Requirement: Scheduled enrichment pull requests

The repository SHALL run a monthly scheduled workflow that checks enrichment freshness, applies enrichment scripts when updates are available, and opens one pull request per source (as assigned in `data/schemas/enrichment_sources.yaml`) with that source's data changes. A pull request whose changes only fill empty values, add list items or mapping keys, or stay within the configured thresholds, from a source not marked for review, SHALL be set to merge automatically once checks pass; any other pull request SHALL be labelled `needs-review`.

#### Scenario: Stale World Bank data triggers PR

- **WHEN** the monthly enrichment workflow detects outdated World Bank provenance and enrichment produces diffs
- **THEN** a pull request for the World Bank indicators source is opened against the default branch with the updated YAML and regenerated artifacts

#### Scenario: No changes skips PR

- **WHEN** enrichment runs and produces no diffs
- **THEN** no pull request is opened and the workflow completes successfully

#### Scenario: Routine refresh merges automatically

- **WHEN** the only changes are population estimates within 10% of the previous values
- **THEN** the World Bank indicators pull request is set to auto-merge

#### Scenario: Large swing needs review

- **WHEN** a country's population changes by more than 10%
- **THEN** the World Bank indicators pull request is labelled `needs-review` and its body lists the change

#### Scenario: Unassigned field needs review

- **WHEN** enrichment changes a field that no source lists
- **THEN** the change goes to the `other` pull request, which is labelled `needs-review`
