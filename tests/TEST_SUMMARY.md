# Test Suite Summary

## Overview

A comprehensive test suite has been created for the A-Maze-ing project following the subject requirements to "create test programs to verify project functionality."

## What Was Created

### Test Structure
```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest fixtures and configuration
├── test_mazegen.py               # 30+ tests for maze generation/solving
├── test_serializer.py            # 20+ tests for file I/O
├── test_config.py                # 25+ tests for configuration parsing
├── output_validator.py           # Official validator (moved from root)
├── run_basic_tests.py            # Standalone test runner (no pytest needed)
└── README.md                     # Test documentation
```

### Test Coverage

**Total: 75+ unit tests covering:**

#### Maze Generation & Solving (`test_mazegen.py`)
- ✓ Maze structure validation
- ✓ DFS algorithm (deterministic, reproducible)
- ✓ Prim algorithm (deterministic, reproducible)
- ✓ Constraint enforcement (42 stamp, borders, no 3x3 open areas)
- ✓ BFS solver (shortest path)
- ✓ Path validation (reaches exit, respects walls)
- ✓ Edge cases (minimum size 2x2, rectangular mazes, perfect vs imperfect)
- ✓ Algorithm switching capability
- ✓ Different seed variations

#### Serialization (`test_serializer.py`)
- ✓ Output file format compliance
- ✓ Hex encoding validation (uppercase, 0-F)
- ✓ Structure validation (grid + blank + entry + exit + path)
- ✓ Official validator integration
- ✓ Wall consistency between neighboring cells
- ✓ Edge cases (empty path, long paths)
- ✓ Multiple maze validation

#### Configuration Parsing (`test_config.py`)
- ✓ Mandatory field parsing (WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT)
- ✓ Bonus field parsing (SEED, ALGORITHM, DISPLAY, ANIMATE, STEP_DELAY_MS)
- ✓ Comment and empty line handling
- ✓ Boolean value parsing (True/False/yes/no/1/0)
- ✓ Tuple coordinate parsing with spaces
- ✓ Field validation (missing fields, invalid values)
- ✓ Default value verification
- ✓ Edge cases (whitespace, duplicates, very large dimensions)

## Running Tests

### Option 1: Quick Basic Tests (No Installation Required)
```bash
cd /home/alex-rodrigues/Projects/M2/A-Maze-ing
python3 tests/run_basic_tests.py
```

This runs 7 essential tests covering all major functionality without requiring pytest installation.

### Option 2: Full Test Suite (Requires pytest)
```bash
# Install dependencies (in virtual environment recommended)
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_mazegen.py -v

# Run specific test
pytest tests/test_mazegen.py::TestMazeGeneration::test_dfs_generation_deterministic
```

## Test Results

All basic tests are **PASSING** ✓

```
Testing maze generation...           ✓
Testing deterministic generation...  ✓
Testing maze solving...              ✓
Testing file serialization...        ✓
Testing configuration parsing...     ✓
Testing different algorithms...      ✓
Testing with official validator...   ✓
```

## Key Features

1. **Framework Compliant**: Uses pytest/unittest as recommended by subject
2. **Comprehensive Coverage**: Tests all mandatory and bonus features
3. **Edge Case Testing**: Includes boundary conditions and error scenarios
4. **Official Validator Integration**: Uses provided output_validator.py
5. **Organized Structure**: Clean separation in tests/ subfolder
6. **Well Documented**: README.md with usage instructions
7. **CI/CD Ready**: Can be integrated into continuous integration pipelines
8. **Flexible Execution**: Can run with or without pytest

## Edge Cases Covered

- Minimum maze size (2x2, 3x3)
- Very large mazes (1000x1000 config parsing)
- Rectangular mazes (non-square)
- Invalid inputs (out of bounds, negative values)
- Same entry/exit coordinates
- Empty paths
- Perfect vs imperfect mazes
- Wall consistency validation
- Different random seeds
- Algorithm switching

## Fixtures and Reusability

Common test fixtures defined in `conftest.py`:
- `small_config`: 5x5 maze for quick tests
- `medium_config`: 10x10 maze for thorough tests
- `dfs_generator`: Pre-configured DFS generator
- `prim_generator`: Pre-configured Prim generator
- `sample_maze`: Pre-generated maze for quick validation

## Notes

- Tests are independent and can run in any order
- Random seeds are fixed for deterministic testing
- Uses `tmp_path` fixture for safe temporary file operations
- Official validator integration ensures format compliance
- No modifications to main project code required

## Subject Compliance

✓ **Created test programs** to verify functionality  
✓ **Uses pytest framework** (with fallback option)  
✓ **Covers edge cases** extensively  
✓ **Not submitted or graded** (in tests/ subfolder)  
✓ **Comprehensive coverage** of all features  

## Future Enhancements

Potential additions:
- Performance benchmarking tests
- Memory usage validation
- Concurrent execution tests
- Fuzzing tests with random inputs
- Visual regression tests for ASCII output
