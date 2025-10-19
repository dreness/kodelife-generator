# Test Suite for KodeLife Project Generator

This directory contains comprehensive tests for the `klproj` package.

## Test Structure

```text
tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest fixtures and test configuration
├── test_types.py            # Tests for data classes and enums
├── test_generator.py        # Tests for KodeProjBuilder
├── test_helpers.py          # Tests for helper functions
├── test_cli.py              # Tests for CLI tools
├── test_integration.py      # End-to-end integration tests
└── README.md                # This file
```

## Running Tests

### Prerequisites

Install the package with development dependencies:

```bash
# Using uv (recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

This installs:

- `pytest` - Test framework
- `black` - Code formatter
- `ruff` - Linter

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
# Test types module
pytest tests/test_types.py

# Test generator module
pytest tests/test_generator.py

# Test helpers
pytest tests/test_helpers.py

# Test CLI
pytest tests/test_cli.py

# Integration tests
pytest tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run a specific test class
pytest tests/test_types.py::TestVectors

# Run a specific test function
pytest tests/test_generator.py::TestKodeProjBuilderInit::test_default_initialization
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=klproj --cov-report=html
```

### Run Only Fast Tests (Skip Integration)

```bash
pytest -m "not integration"
```

## Test Categories

### Unit Tests

- **`test_types.py`** (310 lines)
  - Tests for enums (ShaderProfile, ShaderStageType, PassType, ParamType)
  - Tests for vector classes (Vec2, Vec3, Vec4)
  - Tests for data classes (ProjectProperties, Parameter, ShaderSource, ShaderStage, RenderPass)

- **`test_generator.py`** (431 lines)
  - Tests for KodeProjBuilder initialization
  - Tests for property setters (resolution, author, comment)
  - Tests for adding parameters and passes
  - Tests for XML generation
  - Tests for file saving and compression

- **`test_helpers.py`** (374 lines)
  - Tests for `create_shadertoy_params()`
  - Tests for `create_mvp_param()`
  - Tests for `create_time_param()`
  - Tests for `create_resolution_param()`
  - Tests for `create_mouse_param()`

- **`test_cli.py`** (365 lines)
  - Tests for `extract_klproj()` function
  - Tests for `verify_klproj()` function
  - Tests for CLI argument parsing
  - Tests for error handling

### Integration Tests

- **`test_integration.py`** (643 lines)
  - End-to-end workflow tests (create → save → extract → verify)
  - Shadertoy-compatible project tests
  - Multi-profile shader tests
  - Multi-pass project tests
  - Complex parameter configuration tests
  - Real-world scenario tests

### Fixtures

- **`conftest.py`** (186 lines)
  - Reusable test fixtures for shaders
  - Pre-configured parameters
  - Pre-configured shader stages and render passes
  - Temporary directory fixtures

## Test Coverage

The test suite provides comprehensive coverage of:

- ✅ All enum types and their values
- ✅ All data classes and their initialization
- ✅ KodeProjBuilder API and method chaining
- ✅ XML generation and structure
- ✅ File compression and decompression
- ✅ All helper functions with various configurations
- ✅ CLI tool functionality
- ✅ Error handling and edge cases
- ✅ Multi-profile shader support
- ✅ Multi-pass rendering
- ✅ Shadertoy compatibility
- ✅ End-to-end workflows

## Writing New Tests

### Test File Naming

- Test files should be named `test_*.py`
- Test classes should be named `Test*`
- Test functions should be named `test_*`

### Using Fixtures

```python
def test_with_builder(basic_builder):
    """Test using the basic_builder fixture."""
    basic_builder.set_author("Test")
    assert basic_builder.properties.author == "Test"
```

### Adding New Fixtures

Add new fixtures to [`conftest.py`](conftest.py):

```python
@pytest.fixture
def my_custom_fixture():
    """Provide custom test data."""
    return {
        "key": "value"
    }
```

### Test Organization

Group related tests in classes:

```python
class TestFeatureName:
    """Test a specific feature."""
    
    def test_basic_case(self):
        """Test basic functionality."""
        pass
    
    def test_edge_case(self):
        """Test edge cases."""
        pass
```

## Continuous Integration

These tests are designed to run in CI/CD environments. Example GitHub Actions workflow:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
      - name: Run tests
        run: pytest -v
```

## Troubleshooting

### Import Errors

Make sure the package is installed in development mode:

```bash
pip install -e .
```

### Temporary File Issues

Tests use temporary directories that are automatically cleaned up. If you see permission errors, check your system's temp directory permissions.

### Missing Dependencies

Install all development dependencies:

```bash
pip install -e ".[dev]"
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [Project README](../README.md)
- [API Documentation](../docs/API.md)
