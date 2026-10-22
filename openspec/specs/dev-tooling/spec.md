# dev-tooling Specification

## Purpose
TBD - created by archiving change add-dev-tooling. Update Purpose after archive.
## Requirements
### Requirement: Ruff lint and format configuration

The repository SHALL include ruff configuration in `pyproject.toml` enforcing consistent Python style for scripts.

#### Scenario: Ruff check passes on main

- **WHEN** a developer runs `ruff check scripts/`
- **THEN** no errors are reported on the default branch after initial cleanup

#### Scenario: Ruff runs in CI

- **WHEN** a pull request modifies Python files under `scripts/`
- **THEN** CI runs ruff and fails on new lint violations

### Requirement: Pre-commit hooks

The repository SHALL provide `.pre-commit-config.yaml` so contributors can run lint checks before commit.

#### Scenario: Pre-commit install documented

- **WHEN** a contributor follows `CONTRIBUTING.md` setup instructions
- **THEN** they can run `pre-commit install` and hooks execute on commit

### Requirement: Type checking configuration

The repository SHALL include mypy configuration for incremental adoption on new and test modules.

#### Scenario: Mypy config present

- **WHEN** mypy is installed and run against configured paths
- **THEN** configuration file exists and documents excluded legacy modules

### Requirement: Automated unit test suite

The repository SHALL include a `tests/` directory with pytest tests covering core build and validation logic.

#### Scenario: Tests run locally

- **WHEN** a developer runs `pytest tests/ -q` after installing dev dependencies
- **THEN** all tests pass on a clean checkout of `main`

#### Scenario: Tests run in CI

- **WHEN** a pull request modifies `scripts/` or `data/schemas/`
- **THEN** CI executes pytest and fails on test failures

### Requirement: Clean data normalization tests

Tests SHALL cover `clean_data()` edge cases including YAML boolean strings, None-to-default conversion, and list field normalization.

#### Scenario: Boolean string normalized

- **WHEN** source data contains the string `"yes"` for a boolean field
- **THEN** `clean_data()` produces a boolean `True` in exported records

### Requirement: Manifest generation tests

Tests SHALL verify that build manifest output includes required keys and stable `schema_hash` for unchanged PyArrow schemas.

#### Scenario: Manifest contains required fields

- **WHEN** a test invokes manifest generation for countries
- **THEN** output includes `version`, `build_date`, `git_commit`, `row_count`, and `schema_hash`

### Requirement: Offline test execution

The test suite SHALL NOT require network access to external APIs.

#### Scenario: CI pytest without network

- **WHEN** pytest runs in CI with network restricted
- **THEN** all tests pass without HTTP calls to Wikidata or World Bank

### Requirement: Repository ignores editor and OS artifacts

`.gitignore` SHALL ignore `.DS_Store` and similar OS/editor artifacts, and no such artifacts SHALL remain tracked in the repository.

#### Scenario: DS_Store ignored

- **WHEN** a contributor on macOS creates a `.DS_Store` file in the working tree
- **THEN** `git status` does not list it as an untracked or staged file

#### Scenario: No tracked DS_Store

- **WHEN** the repository file list is inspected
- **THEN** no `.DS_Store` file is tracked

### Requirement: Scheduled enrichment pull requests

The repository SHALL run a monthly scheduled workflow that checks enrichment freshness, applies enrichment scripts when updates are available, and opens a pull request with any resulting data changes for maintainer review.

#### Scenario: Stale World Bank data triggers PR

- **WHEN** the monthly enrichment workflow detects outdated World Bank provenance and enrichment produces diffs
- **THEN** a pull request is opened against the default branch with the updated YAML and regenerated artifacts

#### Scenario: No changes skips PR

- **WHEN** enrichment runs and produces no diffs
- **THEN** no pull request is opened and the workflow completes successfully

### Requirement: Test coverage reporting in CI

Pull request CI SHALL run pytest with coverage reporting for `internacia_builder` and fail when line coverage falls below a configured minimum threshold documented in `pyproject.toml`.

#### Scenario: Coverage reported on PR

- **WHEN** CI runs on a pull request modifying Python code
- **THEN** the workflow output includes a coverage summary for `internacia_builder`

#### Scenario: Coverage regression fails CI

- **WHEN** a change reduces coverage below the configured fail-under threshold
- **THEN** the validate workflow fails

### Requirement: Build and quality logic in installable package

Dataset build/export logic and the quality analyzer SHALL live in the installable `internacia_builder` package (for example `internacia_builder.build` and `internacia_builder.quality`), and `scripts/builder.py` SHALL be a thin CLI shim over that package. The quality analyzer SHALL reuse the package validators rather than duplicating validation rules.

#### Scenario: Build importable from package

- **WHEN** a developer imports the build entry point from `internacia_builder`
- **THEN** datasets can be built without importing from `scripts/` via `sys.path` mutation

#### Scenario: Analyzer reuses validators

- **WHEN** the quality analyzer checks intblock references or country borders
- **THEN** it calls shared validation functions rather than a duplicated copy

### Requirement: Console entry points for build and quality

`pyproject.toml` SHALL expose `internacia-build` and `internacia-analyze-quality` console entry points, and the package SHALL carry a documented version aligned with dataset releases rather than a placeholder.

#### Scenario: Build entry point runs

- **WHEN** a user runs `internacia-build` after `pip install -e .`
- **THEN** the datasets build the same as `python scripts/builder.py build`

#### Scenario: Package reports a real version

- **WHEN** a consumer inspects `internacia_builder.__version__`
- **THEN** it reports the current release version, not `0.0.0`

### Requirement: Cross-format export equivalence tests

The test suite SHALL verify that all committed export formats agree on row count and primary-key set per dataset, and that build manifests match actual exported rows.

#### Scenario: Format parity asserted

- **WHEN** the export equivalence test runs against a build
- **THEN** JSONL, YAML, Parquet, and DuckDB report identical id sets and row counts for each dataset

#### Scenario: Manifest count matches rows

- **WHEN** the manifest consistency test runs
- **THEN** each manifest `row_count` equals the number of exported rows for that dataset

