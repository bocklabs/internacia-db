# data-licensing Specification

## Purpose
TBD - created by archiving change add-data-license. Update Purpose after archive.
## Requirements
### Requirement: Explicit dataset license

The repository SHALL declare an explicit license for the compiled datasets in `data/datasets/`,
separate from the source-code license (`LICENSE`). The data license SHALL be recorded in a
`DATA_LICENSE` file at the repository root using a recognized open-data license (e.g. CC-BY-4.0 or
CC0-1.0).

#### Scenario: Data license file present

- **WHEN** a consumer inspects the repository root
- **THEN** a `DATA_LICENSE` file exists stating the license that applies to dataset artifacts

#### Scenario: Code and data licenses distinguished

- **WHEN** a consumer reads the README license section
- **THEN** it states that source code is MIT-licensed and dataset artifacts are covered by `DATA_LICENSE`

### Requirement: Source attribution documentation

The repository SHALL document upstream data sources and their license obligations in an
`ATTRIBUTION.md` file, including World Bank, Wikidata, IANA tzdata, and mledoze/countries
(ODbL-1.0), plus a recommended citation for reusing the datasets. Any upstream source cited in
per-record `provenance` entries SHALL appear in the attribution table, and share-alike-licensed
sources SHALL carry a documented compatibility rationale for redistribution under the dataset
license.

#### Scenario: Upstream sources attributed

- **WHEN** a consumer reads `ATTRIBUTION.md`
- **THEN** it lists World Bank (CC-BY-4.0), Wikidata (CC0), IANA tzdata, and mledoze/countries (ODbL-1.0) with links

#### Scenario: Citation guidance available

- **WHEN** a researcher wants to cite the datasets
- **THEN** `ATTRIBUTION.md` provides a recommended citation format

#### Scenario: Provenance-cited source appears in attribution table

- **WHEN** a source is named in any country or intblock `provenance` entry
- **THEN** `ATTRIBUTION.md` contains a row for that source with its license

#### Scenario: Share-alike source has compatibility rationale

- **WHEN** a consumer checks how ODbL-derived fields are redistributed under CC-BY-4.0
- **THEN** `ATTRIBUTION.md` (or a linked document) states the compatibility rationale

### Requirement: License metadata in build manifest

Each dataset build manifest (`countries.manifest.json`, `intblocks.manifest.json`) SHALL include a
machine-readable `data_license` field containing the SPDX identifier of the dataset license.

#### Scenario: Manifest declares data license

- **WHEN** `scripts/builder.py` writes a dataset manifest
- **THEN** the manifest contains a non-empty `data_license` field with an SPDX identifier (e.g. `CC-BY-4.0`)

### Requirement: Machine-readable citation metadata

The repository SHALL provide a valid `CITATION.cff` file at the root referencing the dataset's Zenodo DOI, and `README.md` SHALL display a DOI badge.

#### Scenario: GitHub citation widget works

- **WHEN** a visitor opens the repository on GitHub
- **THEN** the "Cite this repository" widget renders from `CITATION.cff` including the DOI

#### Scenario: DOI badge present

- **WHEN** a reader views `README.md`
- **THEN** a Zenodo DOI badge links to the dataset's DOI record

### Requirement: External distribution citation

`ATTRIBUTION.md` SHALL document Hugging Face Datasets and Zenodo as official distribution channels alongside GitHub Releases.

#### Scenario: Researcher finds HF path

- **WHEN** a reader opens ATTRIBUTION or README
- **THEN** they find the Hugging Face dataset URL and Zenodo concept DOI

