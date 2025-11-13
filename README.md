# pytest-param-table

Elegant table-driven parameterized tests for pytest.

## Why?

`pytest.mark.parametrize` is powerful but can be hard to read with multiple parameters:

```python
@pytest.mark.parametrize("text,expected", [
    ("", ""),
    ("x", "x"),
    ("hello", "olleh"),
])
def test_reverse(text, expected):
    assert reverse(text) == expected
```

With `pytest-param-table`, tests read like a table:

```python
from pytest_param_table import param_table

@param_table({
    "empty_string": {"text": "", "expected": ""},
    "one_character": {"text": "x", "expected": "x"},
    "multiple_characters": {"text": "hello", "expected": "olleh"},
})
def test_reverse(text: str, expected: str):
    assert reverse(text) == expected
```

## Features

- ✅ **Visual clarity**: Test cases read like a table with named columns
- ✅ **Type safety**: Validates parameter types at decoration time using type hints
- ✅ **Strict by default**: Every parameter must be provided or have an explicit default
- ✅ **Simple**: Delegates to `pytest.mark.parametrize` under the hood
- ✅ **Minimal API**: One decorator, one helper function
- ✅ **pytest marks support**: Easy integration with `xfail`, `skip`, and custom marks

## Installation

```bash
uv pip install pytest-param-table
# or
pip install pytest-param-table
```

## Usage

### Basic Usage

```python
from pytest_param_table import param_table

@param_table({
    "empty_string": {"text": "", "expected": ""},
    "one_character": {"text": "x", "expected": "x"},
    "multiple_characters": {"text": "hello", "expected": "olleh"},
})
def test_reverse(text: str, expected: str):
    assert reverse(text) == expected
```

### With Defaults

Use the `defaults` parameter for values that are usually the same:

```python
@param_table(
    {
        "with_flag": {"value": 5, "flag": True},
        "without_flag": {"value": 10},  # flag comes from defaults
    },
    defaults={"flag": False},
)
def test_with_flag(value: int, flag: bool):
    result = value * 2 if flag else value
    assert isinstance(result, int)
```

### With pytest Marks

Use the `marked()` helper to attach pytest marks to specific test cases:

```python
from pytest_param_table import param_table, marked
import pytest

@param_table({
    "normal": {"value": 5},
    "expected_fail": marked({"value": -1}, pytest.mark.xfail),
    "skip_slow": marked({"value": 999}, pytest.mark.skip(reason="Too slow")),
    "multiple_marks": marked({"value": 7}, pytest.mark.slow, pytest.mark.integration),
})
def test_with_marks(value: int):
    assert value > 0
```

### Nested for Cartesian Products

Stack decorators to test all combinations:

```python
@param_table({"case_a": {"x": 1}, "case_b": {"x": 2}})
@param_table({"upper": {"y": "A"}, "lower": {"y": "a"}})
def test_combine(x: int, y: str):
    # Runs 4 tests: case_a-upper, case_a-lower, case_b-upper, case_b-lower
    assert isinstance(x, int)
    assert isinstance(y, str)
```

### Real-World Example

```python
@param_table({
    "valid_email": {
        "input_email": "user@example.com",
        "expected_valid": True,
        "expected_domain": "example.com",
    },
    "invalid_no_at": {
        "input_email": "userexample.com",
        "expected_valid": False,
        "expected_domain": None,
    },
    "invalid_multiple_at": {
        "input_email": "user@@example.com",
        "expected_valid": False,
        "expected_domain": None,
    },
    "subdomain": {
        "input_email": "user@mail.example.com",
        "expected_valid": True,
        "expected_domain": "mail.example.com",
    },
})
def test_email_validation(
    input_email: str,
    expected_valid: bool,
    expected_domain: str | None,
):
    result = validate_email(input_email)
    assert result.is_valid == expected_valid
    assert result.domain == expected_domain
```

## Design Philosophy

### 1. Strict by Default

Every parameter must be explicitly provided or have a default:

```python
# ❌ This raises KeyError
@param_table({
    "incomplete": {"x": 1},  # Missing 'y'!
})
def test_example(x: int, y: int):
    pass

# ✅ Either provide all parameters
@param_table({
    "complete": {"x": 1, "y": 2},
})
def test_example(x: int, y: int):
    pass

# ✅ Or use defaults
@param_table(
    {"partial": {"x": 1}},
    defaults={"y": 2},
)
def test_example(x: int, y: int):
    pass
```

### 2. Type Safety

Type hints are validated at decoration time:

```python
# ❌ This raises TypeError at import time
@param_table({
    "bad_type": {"x": "not an int"},
})
def test_example(x: int):
    pass
```

### 3. Clear Error Messages

Errors are caught early with helpful messages:

```
@param_table missing required parameter(s) in test case 'incomplete':
  Missing: y, z
  Provided: x

  Add the missing parameters or set defaults={'y': ..., 'z': ...}
  In function: test_example at test_file.py:42
```

## API Reference

### `param_table(cases, *, defaults=None)`

Table-driven test decorator with strict parameter validation.

**Parameters:**
- `cases` (dict): Test cases mapping name → parameters dict or `MarkedCase`
- `defaults` (dict, optional): Default values for parameters not in all cases

**Raises:**
- `ValueError`: If cases is empty
- `TypeError`: If parameter values don't match their type hints
- `KeyError`: If a required parameter is missing (and not in defaults)

### `marked(params, *marks)`

Attach pytest marks to a test case.

**Parameters:**
- `params` (dict): Test case parameters
- `*marks`: One or more `pytest.Mark` objects

**Returns:**
- `MarkedCase`: Wrapper containing params and marks

**Example:**
```python
marked({"x": 1}, pytest.mark.xfail, pytest.mark.slow)
```

### `MarkedCase`

Dataclass wrapper for test case params with pytest marks.

**Attributes:**
- `params` (dict): Test case parameters
- `marks` (tuple): Pytest marks to apply

## Comparison with pytest.mark.parametrize

| Feature | `pytest.mark.parametrize` | `pytest-param-table` |
|---------|---------------------------|----------------------|
| Readability with many params | ❌ Hard to read | ✅ Table-like structure |
| Named test cases | ✅ Via `ids` | ✅ Built-in |
| Type checking | ❌ No | ✅ At decoration time |
| Missing parameter detection | ❌ Runtime error | ✅ Decoration time error |
| Default values | ❌ Manual | ✅ `defaults=` parameter |
| pytest marks | ✅ `pytest.param(..., marks=)` | ✅ `marked()` helper |

## Development

```bash
# Clone the repo
git clone https://github.com/yourusername/pytest-param-table
cd pytest-param-table

# Install in dev mode with hooks auto-install
uv pip install -e ".[dev]"

# Manually install git hooks (if needed)
pytest-param-table-install-hooks

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=pytest_param_table --cov-report=html

# Type checking
uv run pyright

# Linting and formatting
uv run ruff check src/ tests/
uv run ruff format src/ tests/

# Run pre-commit hooks manually
uv run pre-commit run --all-files
```

### Git Hooks

The project uses pre-commit hooks to ensure code quality:

- **pre-commit**: Runs ruff formatting, linting, and pyright type checking
- **pre-push**: Runs the full test suite

Hooks are automatically installed when you run `pip install -e ".[dev]"`. To manually install:

```bash
pytest-param-table-install-hooks
```

To skip hooks temporarily (not recommended):

```bash
git commit --no-verify
git push --no-verify
```

## Requirements

- Python >= 3.10
- pytest >= 7.0
- typeguard >= 4.0

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for any new functionality
4. Ensure all tests pass
5. Submit a pull request

## Changelog

### 0.1.0 (Initial Release)

- ✅ Core `@param_table` decorator
- ✅ `marked()` helper for pytest marks
- ✅ Strict parameter validation
- ✅ Type checking at decoration time
- ✅ Support for defaults
- ✅ Comprehensive test suite
- ✅ Full documentation

## Credits

Inspired by table-driven tests in Go and the need for more readable parametrized tests in Python.
