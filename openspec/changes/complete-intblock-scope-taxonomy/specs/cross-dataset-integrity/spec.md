## MODIFIED Requirements

### Requirement: Identifier stability policy

Country `code` and intblock `id` SHALL be treated as stable join keys. When an intblock id must change
(rename, merge, or acronym reassignment), the previous id SHALL be retained as an alias in the alias
source (`data/intblocks_aliases.yaml`) with a `reason` of `renamed`, `merged`, or `disambiguated`,
rather than removed without trace. When an intblock id is retired because its meaning moved to a
country attribute field, the retirement SHALL be recorded in `data/attribute_intblock_migrations.yaml`
instead of an intblock alias entry. When an intblock record is removed because it is out of scope and
has no successor, its id SHALL be retained as an alias with `reason: retired` and no `target`.

#### Scenario: Rename records an alias

- **WHEN** an intblock id is renamed from `OLD` to `NEW`
- **THEN** an alias entry `OLD → NEW` with `reason: renamed` is added to the alias source in the same change

#### Scenario: Merge records an alias

- **WHEN** two intblock records are merged into a single id
- **THEN** the removed id is recorded as an alias pointing to the surviving id with `reason: merged`

#### Scenario: Acronym reassignment records a disambiguation alias

- **WHEN** an entity vacates an id (e.g. `ASF`) which is then reused for a different entity, and the
  original entity moves to a new id (e.g. `FSA`)
- **THEN** an alias entry `ASF → FSA` with `reason: disambiguated` is recorded, even though `ASF`
  remains a current id for the different entity

#### Scenario: Attribute retirement records a field migration

- **WHEN** intblock id `LHTRAFFIC` is removed because driving side lives on countries
- **THEN** `data/attribute_intblock_migrations.yaml` contains a `LHTRAFFIC` entry mapping to `car_side: left` and no intblock alias target is required

#### Scenario: Out-of-scope removal records a retired alias

- **WHEN** an intblock record such as `TELESUR` is removed because the entity is out of scope and no
  current record replaces it
- **THEN** an alias entry `TELESUR` with `reason: retired` and no `target` is added in the same change

### Requirement: Alias integrity validation

Intblocks validation SHALL verify that every alias `target` resolves to an existing intblock id, that
each `reason` is one of `renamed`/`merged`/`disambiguated`/`retired`, and that an alias colliding with a
current intblock id is permitted only when its `reason` is `disambiguated`. An alias with `reason:
retired` SHALL have no `target` and SHALL NOT equal a current intblock id; every other alias SHALL have
a `target`.

#### Scenario: Dangling alias rejected

- **WHEN** an alias `target` references an id that does not exist in the intblocks dataset
- **THEN** validation reports an alias integrity error

#### Scenario: Unexpected alias/id collision rejected

- **WHEN** an alias id equals a current intblock id and its `reason` is not `disambiguated`
- **THEN** validation reports a collision error

#### Scenario: Disambiguation collision allowed

- **WHEN** an alias id equals a current intblock id and its `reason` is `disambiguated`
- **THEN** validation passes for that alias

#### Scenario: Retired alias without target allowed

- **WHEN** an alias has `reason: retired`, no `target`, and its id is not a current intblock id
- **THEN** validation passes for that alias

#### Scenario: Retired alias with a target rejected

- **WHEN** an alias has `reason: retired` and a non-empty `target`
- **THEN** validation reports an alias integrity error
