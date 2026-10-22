## ADDED Requirements

### Requirement: Content-complete artifact verification
Artifact verification SHALL reject changed projected values, duplicate keys,
missing metadata, invalid schema hashes, changed source records, and mismatched
membership edges. Checks SHALL account for deliberate source-only fields.

#### Scenario: Content corruption preserves identifiers
- **WHEN** one exported value changes without changing its primary key
- **THEN** verification fails and identifies the dataset and format

#### Scenario: Committed freshness precedes fresh-build tests
- **WHEN** CI validates a change
- **THEN** it verifies committed exports before rebuilding and tests the final staged artifacts

### Requirement: Resolvable distribution package
Each distribution descriptor SHALL contain unique physical resource names and
reference only files included in that distribution. Release publication SHALL
follow tests, quality checks, and release-version consistency validation.

#### Scenario: Partial mirror
- **WHEN** a mirror publishes only selected formats
- **THEN** its descriptor lists only those published resource paths

### Requirement: Recursive migration evidence
Migration reports SHALL compare nested source and export contracts against a
named previous release, recording baseline identity or explicit unavailability.

#### Scenario: Nested type change
- **WHEN** an array item or nested field type changes
- **THEN** the migration report identifies the affected field path
