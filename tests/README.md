# A-Maze-ing Test Suite

This directory contains comprehensive unit tests for the A-Maze-ing maze generator project.

## Test Structure

```
tests/
├── __init__.py                 # Package initialization
├── conftest.py                 # Pytest fixtures and configuration
├── test_mazegen.py            # Maze generation and solving tests
├── test_serializer.py         # File I/O and format tests
├── test_config.py             # Configuration parsing tests
├── output_validator.py        # Official validator (provided by subject)
└── README.md                  # This file
```

## Running Tests

### Using Makefile (Recommended)

The project includes `Makefile_tests` with convenient targets:

```bash
# Show all available commands
make -f Makefile_tests help

# Quick tests (no pytest installation needed)
make -f Makefile_tests quick

# Run all tests with pytest
make -f Makefile_tests all

# Run specific test files
make -f Makefile_tests mazegen
make -f Makefile_tests serializer
make -f Makefile_tests config

# Generate coverage reports
make -f Makefile_tests coverage
make -f Makefile_tests coverage-html

# Clean test artifacts
make -f Makefile_tests clean

# Install test dependencies
make -f Makefile_tests install-deps
```

### Using pytest Directly

```bash
# Install dependencies first
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=. --cov-report=html

# Run specific test files
pytest tests/test_mazegen.py
pytest tests/test_serializer.py
pytest tests/test_config.py

# Run specific test classes or methods
pytest tests/test_mazegen.py::TestMazeGeneration
pytest tests/test_mazegen.py::TestMazeGeneration::test_dfs_generation_deterministic
```

### Using Basic Test Runner

```bash
# No installation required, runs 7 essential tests
python3 tests/run_basic_tests.py
```

## Test Coverage

The test suite covers:

### Maze Generation (`test_mazegen.py`)
- ✓ Maze structure and dimensions
- ✓ Valid wall bitmasks (0-15)
- ✓ DFS algorithm (deterministic, reproducible)
- ✓ Prim algorithm (deterministic, reproducible)
- ✓ Constraint enforcement (42 stamp, borders, no 3x3 open areas)
- ✓ BFS solver (shortest path)
- ✓ Path validation (reaches exit, respects walls)
- ✓ Edge cases (minimum size, rectangular, perfect vs imperfect)
- ✓ Algorithm switching

### Serialization (`test_serializer.py`)
- ✓ Output file format compliance
- ✓ Hex encoding (uppercase, 0-F)
- ✓ Structure validation (grid, entry, exit, path)
- ✓ Official validator integration
- ✓ Wall consistency between neighbors
- ✓ Edge cases (empty path, long path)

### Configuration (`test_config.py`)
- ✓ Parsing mandatory fields
- ✓ Parsing bonus fields
- ✓ Comment and empty line handling
- ✓ Boolean value parsing
- ✓ Tuple coordinate parsing
- ✓ Field validation (missing, invalid)
- ✓ Default values
- ✓ Edge cases (whitespace, duplicates, large dimensions)

## Test Fixtures

Common fixtures defined in `conftest.py`:
- `small_config`: 5x5 maze configuration
- `medium_config`: 10x10 maze configuration
- `dfs_generator`: DFS algorithm generator
- `prim_generator`: Prim algorithm generator
- `sample_maze`: Pre-generated sample maze

## Writing New Tests

Follow these patterns:

```python
def test_descriptive_name(fixture_name):
    """Clear description of what is being tested."""
    # Arrange
    # ... setup code
    
    # Act
    result = some_function()
    
    # Assert
    assert result == expected_value
```

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest tests/ -v --cov=.
```

## Notes

- Tests use `tmp_path` fixture for temporary file operations
- The official `output_validator.py` is integrated for format validation
- Tests are designed to be independent and can run in any order
- Random seeds are fixed for deterministic testing
- Edge cases include minimum sizes, invalid inputs, and boundary conditions

## Troubleshooting

### Import Errors
If you get import errors, make sure you're running pytest from the project root:
```bash
cd /path/to/A-Maze-ing
pytest tests/
```

### Missing Dependencies
Install all required packages:
```bash
pip install -r requirements.txt
pip install pytest pytest-cov
```

### Test Failures
Run with verbose output to see detailed failure information:
```bash
pytest tests/ -v -s
```
