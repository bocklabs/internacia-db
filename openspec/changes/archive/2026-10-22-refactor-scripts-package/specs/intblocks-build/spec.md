## MODIFIED Requirements

### Requirement: Intblocks validation before export

The dataset builder SHALL run intblock validation before writing intblocks derived artifacts by importing the validation module directly rather than subprocess invocation.

#### Scenario: Build fails on intblock schema error

- **WHEN** the builder runs and an intblock YAML file fails schema validation
- **THEN** the build exits with non-zero status and does not overwrite intblocks outputs

#### Scenario: Validator importable in tests

- **WHEN** pytest imports the intblocks validation module
- **THEN** validation functions are callable without spawning a subprocess

#### Scenario: Build succeeds when intblocks valid

- **WHEN** all intblock YAML files pass validation
- **THEN** the build proceeds to export intblocks artifacts

#### Scenario: Intblock validator covered by tests

- **WHEN** `validate_intblocks.py` exists
- **THEN** pytest includes tests for schema pass/fail and duplicate id detection
