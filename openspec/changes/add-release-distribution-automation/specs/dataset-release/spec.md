## ADDED Requirements

### Requirement: Hugging Face dataset mirror

Tagged releases SHALL publish countries and intblocks Parquet artifacts to a Hugging Face Datasets repository linked from README.

#### Scenario: HF dataset updated on release

- **WHEN** release workflow completes for tag `v*`
- **THEN** the Hugging Face dataset revision matches the release Parquet artifacts

### Requirement: Automated Zenodo deposit

Each published GitHub Release SHALL be archived to Zenodo by the Zenodo GitHub integration under the concept DOI, producing a version-specific DOI for each release. The release workflow SHALL NOT deposit to Zenodo itself, so each release has exactly one Zenodo version.

#### Scenario: Zenodo version follows tag

- **WHEN** tag `v2.0.0` is released
- **THEN** Zenodo records a new version linked to concept DOI `10.5281/zenodo.20706176`

#### Scenario: No duplicate deposit

- **WHEN** the release workflow runs for tag `v*`
- **THEN** it publishes the GitHub Release without calling the Zenodo API
