# ETL Pipeline Test Suite

This directory contains comprehensive unit tests for the ETL pipeline (`src/pipeline/etl_to_graph.py`).

## Test Coverage

The test suite covers all major functions in the ETL pipeline:

### Data Transformation Tests
- ✅ `normalize_column_names` - Column name normalization
- ✅ `clean_text` - Text cleaning and validation
- ✅ `normalize_linkedin_url` - LinkedIn URL normalization
- ✅ `normalize_quantum_experience` - Experience category normalization
- ✅ `parse_interests` - Interest string parsing
- ✅ `normalize_organization_name` - Organization name normalization
- ✅ `normalize_industry_sector` - Industry sector normalization
- ✅ `transform_dataframe` - Complete DataFrame transformation

### Neo4j Integration Tests
- ✅ `prepare_row_for_neo4j` - Row data preparation
- ✅ `generate_cypher_query` - Cypher query generation
- ✅ `create_driver` - Neo4j driver creation
- ✅ `close_driver` - Driver connection closure
- ✅ `get_session` - Session context manager
- ✅ `insert_row_to_neo4j` - Row insertion into Neo4j

### Pipeline Tests
- ✅ `run_etl_pipeline` - Complete ETL pipeline execution
- ✅ Error handling and edge cases
- ✅ Missing credentials validation
- ✅ File not found handling

## Running Tests

### Install Dependencies

First, install the development dependencies:

```bash
uv sync --group dev
```

Or with pip:

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_etl_pipeline.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=src.pipeline.etl_to_graph --cov-report=html
```

### Run Specific Test Class

```bash
pytest tests/test_etl_pipeline.py::TestNormalizeColumnNames -v
```

### Run Specific Test

```bash
pytest tests/test_etl_pipeline.py::TestNormalizeColumnNames::test_normalize_all_columns -v
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_etl_pipeline.py` - Main test suite for ETL pipeline functions

## Fixtures

The test suite includes the following fixtures (defined in `conftest.py`):

- `sample_csv_data` - Sample CSV data with original column names
- `sample_normalized_data` - Sample data after normalization
- `mock_neo4j_driver` - Mock Neo4j driver for testing
- `mock_neo4j_session` - Mock Neo4j session for testing
- `temp_csv_file` - Temporary CSV file for integration tests

## Notes

- All tests use mocks for Neo4j connections to avoid requiring a live database
- Tests are designed to be fast and isolated
- Edge cases and error conditions are thoroughly tested

