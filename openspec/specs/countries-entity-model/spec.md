# countries-entity-model Specification

## Purpose
TBD - created by archiving change add-countries-entity-status. Update Purpose after archive.
## Requirements
### Requirement: Entity type classification

Every country YAML record SHALL include `entity_type` from the allowed enumeration: `sovereign_state`, `dependent_territory`, `special_administrative_region`, `disputed_territory`, `historical_entity`, `supranational_grouping`, or `statistical_area`.

#### Scenario: Sovereign state classified

- **WHEN** a record represents an independent UN member state such as France
- **THEN** `entity_type` is `sovereign_state`

#### Scenario: Invalid entity type rejected

- **WHEN** a record has `entity_type: country`
- **THEN** validation reports an enum error

### Requirement: Code status classification

Every country record SHALL include `code_status` from: `official_iso3166_1`, `user_assigned`, `obsolete`, or `exceptionally_reserved`.

#### Scenario: Current ISO code marked official

- **WHEN** a record uses a current ISO 3166-1 alpha-2 code such as `FR`
- **THEN** `code_status` is `official_iso3166_1`

#### Scenario: Non-ISO code requires explicit status

- **WHEN** a record has `code` not in the current ISO 3166-1 set
- **THEN** `code_status` MUST NOT be `official_iso3166_1` and MUST be set explicitly

### Requirement: Netherlands Antilles obsolete status

Record `AN` SHALL have `entity_type: historical_entity` and `code_status: obsolete`.

#### Scenario: AN filtered from current ISO views

- **WHEN** a consumer queries records with `code_status == official_iso3166_1`
- **THEN** record `AN` is excluded

### Requirement: Channel Islands grouping status

Record `JG` SHALL have `entity_type: supranational_grouping` and `code_status: user_assigned`.

#### Scenario: JG documented as non-ISO collective

- **WHEN** `docs/country-code-policy.md` is read
- **THEN** it states that `GG` and `JE` are canonical territory codes for Channel Islands constituents

### Requirement: Current ISO filter cardinality

Records with `code_status: official_iso3166_1` SHALL number 249 when aligned with the 2026-05-28 ISO-style audit baseline.

#### Scenario: Official ISO count matches audit

- **WHEN** all country sources are annotated
- **THEN** exactly 249 records have `code_status: official_iso3166_1`

### Requirement: UN participation status

Country records SHALL carry a `un_status` field with values `member`, `observer`, or `non_member`, consistent with the boolean `un_member` field. Exactly the UN member states SHALL be `member` (193 as of 2026), and the UN permanent observer states (`PS`, `VA`) SHALL be `observer`.

#### Scenario: Observer states distinguishable

- **WHEN** a consumer filters countries by `un_status = 'observer'`
- **THEN** exactly `PS` and `VA` are returned

#### Scenario: Status consistent with boolean flag

- **WHEN** a record has `un_status: member`
- **THEN** it also has `un_member: true`, and validation fails on any inconsistency

### Requirement: Explicit status flags on non-standard codes

The non-standard code records (`AN`, `JG`, `KV`, `XA`, `XS`, `XT`, `XN`) SHALL state explicit values for `un_member`, `independent`, and `landlocked` rather than omitting them, and their Wikidata-sourced `population` entries SHALL carry a `year`.

#### Scenario: No ambiguous absence

- **WHEN** a consumer reads `data/countries/KV.yaml`
- **THEN** `un_member`, `independent`, and `landlocked` are explicitly present

#### Scenario: Population year present

- **WHEN** a consumer reads the population of `XA`
- **THEN** the entry includes a `year` value

### Requirement: Documented disputed-territory inclusion policy

`docs/country-code-policy.md` SHALL state the inclusion rule for disputed territories that explains which de facto states receive user-assigned records and which do not, SHALL warn that the `JG` aggregate population is not the sum of `GG` and `JE`, and SHALL note the exceptionally reserved ISO codes (`EU`, `EZ`, `UN`) with a pointer to the `EU` intblock.

#### Scenario: Inclusion rule answers the Somaliland question

- **WHEN** a reader asks why Abkhazia has a record but Somaliland does not
- **THEN** the policy doc states the inclusion criterion that produces this outcome (or documents planned additions)

#### Scenario: Aggregation trap warned

- **WHEN** a consumer sums populations over records including `JG`, `GG`, and `JE`
- **THEN** the policy doc warns about the double-count

### Requirement: Entity classification policy document

The repository SHALL maintain `docs/entity-classification-policy.md` explaining how `entity_type`, `independent`, `un_member`, `un_status`, and `recognition_status` interact for disputed territories, partially recognized states, and special cases (including Taiwan, Palestine, Kosovo, Western Sahara, Vatican City, and associated states).

#### Scenario: Taiwan classification explained

- **WHEN** a reader asks why Taiwan is `dependent_territory` rather than `disputed_territory`
- **THEN** the policy doc states the rationale and cites the relevant classification dimensions

#### Scenario: Independence vs UN membership distinguished

- **WHEN** a consumer filters `independent: true`
- **THEN** the policy doc explains how Vatican City, Kosovo, and associated states are classified

### Requirement: CIS2 build inclusion policy

`docs/country-code-policy.md` SHALL state explicitly whether user-assigned CIS2 codes (`XA`, `XS`, `XT`, `XN`) are included in all standard build exports (Parquet, DuckDB, JSONL, CSV) and how consumers should filter them for ISO-only views.

#### Scenario: CIS2 codes in DuckDB

- **WHEN** a consumer queries `SELECT code FROM countries` in `internacia.duckdb`
- **THEN** the policy doc matches actual export behavior for XA, XS, XT, and XN

### Requirement: Kosovo code XK

Record `XK` SHALL have `entity_type: disputed_territory`, `code_status: user_assigned`, and `recognition_status` indicating disputed or partially recognized status. The retired alpha-2 code `KV` and alpha-3 code `KSV` SHALL appear in `countries_aliases.json` mapping to `XK` and `XKX` respectively.

#### Scenario: XK is the primary Kosovo code

- **WHEN** a consumer loads `data/countries/XK.yaml` or queries countries by `code = 'XK'`
- **THEN** the Kosovo record is returned with complete profile fields

#### Scenario: Legacy KV resolves via alias

- **WHEN** a consumer looks up country code `KV` in `countries_aliases.json`
- **THEN** the alias resolves to `XK`

