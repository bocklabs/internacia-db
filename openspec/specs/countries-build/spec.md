# countries-build Specification

## Purpose
TBD - created by archiving change add-countries-validation. Update Purpose after archive.
## Requirements
### Requirement: Builder validates before export

The dataset builder (`scripts/builder.py`) SHALL run country validation before generating JSONL, YAML, Parquet, or DuckDB outputs.

#### Scenario: Build aborts on validation failure

- **WHEN** country validation reports schema or identifier errors
- **THEN** the builder exits with non-zero status and does not write updated dataset files

#### Scenario: Successful build preserves row count

- **WHEN** all 252 country YAML sources pass validation
- **THEN** `countries.parquet` contains exactly 252 rows

### Requirement: Clean data normalization in builder

The builder `clean_data()` function SHALL apply identifier and categorical normalization rules consistent with `countries-data-quality` requirements.

#### Scenario: Builder applies whitespace cleanup

- **WHEN** the builder loads country sources with fixable whitespace issues
- **THEN** exported datasets contain trimmed categorical values without manual YAML edits

### Requirement: Countries validation before export

The dataset builder SHALL run country validation before export by importing the validation module directly rather than subprocess invocation.

#### Scenario: Country validation without subprocess

- **WHEN** the builder runs pre-export validation
- **THEN** it calls the countries validation module directly without `subprocess.run`

### Requirement: Shared HTTP client for enrichment and link validation

External HTTP calls in enrichment and link validation SHALL use a shared client module with configurable rate limiting and retry with backoff.

#### Scenario: Rate limit applied

- **WHEN** enrichment fetches multiple World Bank or Wikidata endpoints
- **THEN** requests respect the configured minimum delay between calls

#### Scenario: Retry on transient failure

- **WHEN** an HTTP request fails with a retryable status code
- **THEN** the client retries up to a configured limit before reporting failure

### Requirement: CLI backward compatibility shims

Existing `scripts/*.py` entry points SHALL remain functional for at least one release cycle after package extraction.

#### Scenario: Legacy script path works

- **WHEN** a user runs `python scripts/builder.py build`
- **THEN** the build completes successfully via shim delegation to the package CLI

