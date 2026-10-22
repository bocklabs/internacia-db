## ADDED Requirements

### Requirement: Monthly release train

A scheduled workflow SHALL compare the repository with the latest `vX.Y.Z` tag and, when the data sources or the builder changed, open or refresh one release pull request. The release level SHALL follow docs/versioning-policy.md: MINOR when tables, columns, source fields, enum values or records were added, PATCH for any other change. When a table, column, source field, enum value or record id was removed, or a column type changed, the train SHALL NOT open a release pull request and SHALL report the changes instead. The release pull request SHALL date the CHANGELOG entry, add a summary of record and membership changes, and write the version to every place the release gate checks. Merging it SHALL tag the merge commit, which runs the semver tag release workflow.

#### Scenario: Data correction produces a PATCH release PR

- **WHEN** the only change since `v3.1.0` is a corrected NATO roster
- **THEN** the train opens a pull request for `v3.1.1` whose CHANGELOG entry lists the changed membership edges

#### Scenario: New intblock produces a MINOR release PR

- **WHEN** an intblock was added since `v3.1.0`
- **THEN** the train opens a pull request for `v3.2.0`

#### Scenario: Removed id stops the train

- **WHEN** an intblock id present in `v3.1.0` no longer exists
- **THEN** the train opens no pull request and its summary lists the removed id as a MAJOR change

#### Scenario: Merged release PR is tagged

- **WHEN** a maintainer merges the release pull request for `v3.1.1`
- **THEN** tag `v3.1.1` is pushed on the merge commit and the release workflow publishes it

### Requirement: Downstream release notification

After publishing a release, the release workflow SHALL send a `repository_dispatch` event `internacia-db-release` with the version to internacia-python and internacia-api when the bot credentials are configured. A failed notification SHALL NOT fail the release.

#### Scenario: Release notifies the SDK and the API

- **WHEN** `v3.1.1` is published and the bot credentials are configured
- **THEN** internacia-python and internacia-api receive `internacia-db-release` with version `3.1.1`

### Requirement: Record-level release diff

`migration.vX.Y.Z.json` SHALL include a `data` section listing, per dataset, the record ids added, removed and changed since the previous release, and the membership edges added, removed and changed.

#### Scenario: Release diff lists a new membership

- **WHEN** a country joined an intblock since the previous release
- **THEN** `data.memberships.added` in the release's migration JSON lists the intblock, the country and its status
