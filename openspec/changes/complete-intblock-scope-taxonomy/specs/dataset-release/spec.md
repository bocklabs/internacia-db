## MODIFIED Requirements

### Requirement: Identifier alias map artifact

Each successful build SHALL emit an intblock identifier alias artifact at
`data/datasets/intblocks_aliases.json` (and a Parquet equivalent) mapping every retired or renamed
intblock id to its current id. Each entry SHALL include `alias` (retired id), `target` (current id),
`reason` (`renamed`, `merged`, `disambiguated`, or `retired`), and `since` (the version that introduced
the change). For `reason: retired` the `target` SHALL be null.

#### Scenario: Alias artifact written on build

- **WHEN** `scripts/builder.py build` completes an intblocks export
- **THEN** `data/datasets/intblocks_aliases.json` exists and contains an entry for each known retired id

#### Scenario: Retired id is resolvable

- **WHEN** a consumer holds the retired id `ASF`
- **THEN** the alias artifact maps `ASF` to its current id `FSA`

#### Scenario: Retired id without successor is exported with a null target

- **WHEN** a consumer holds the id `TELESUR`, which was retired without a replacement
- **THEN** the alias artifact contains `TELESUR` with `reason: retired` and a null `target`
