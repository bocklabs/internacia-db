## ADDED Requirements

### Requirement: Consistent scope reporting
Standalone validation and quality analysis SHALL emit the same missing formal
scope issue. Explicit historical identifiers SHALL be validated without treating
them as current-country rows.

#### Scenario: Missing formal scope
- **WHEN** a formal record omits scope_category
- **THEN** both validation and quality analysis report that omission

#### Scenario: Unknown historical reference
- **WHEN** a historical-country include references an unrecognized identifier
- **THEN** validation reports an unresolved historical reference

### Requirement: Honest enrichment dates
Enrichment SHALL preserve untouched retrieval dates, refresh provider-backed
values only from usable responses, and preserve declared observation precision.
Updating metadata alone SHALL NOT imply membership-roster verification.

#### Scenario: Provider failure
- **WHEN** a provider returns no usable observation for an existing field
- **THEN** its stored value and retrieval date remain unchanged

#### Scenario: Year-only inception
- **WHEN** Wikidata supplies a year-precision inception
- **THEN** the authored date contains only the year and no fabricated month or day
