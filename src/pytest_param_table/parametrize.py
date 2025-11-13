"""Table-driven test parametrization for pytest."""

import inspect
from dataclasses import dataclass
from typing import Any, Callable, get_type_hints

import pytest
from typeguard import check_type


@dataclass
class MarkedCase:
    """Wrapper for test case params with pytest marks."""

    params: dict[str, Any]
    marks: tuple[pytest.Mark, ...]


def marked(params: dict[str, Any], *marks: pytest.Mark) -> MarkedCase:
    """
    Attach pytest marks to a test case for use with @param_table.

    Args:
        params: Test case parameters
        marks: One or more pytest marks (xfail, skip, etc)

    Returns:
        MarkedCase wrapper containing params and marks

    Example:
        @param_table({
            "normal": {"x": 1},
            "expected_fail": marked({"x": -1}, pytest.mark.xfail),
        })
        def test_example(x: int):
            ...
    """
    return MarkedCase(params=params, marks=marks)


def param_table(
    cases: dict[str, dict[str, Any] | MarkedCase],
    *,
    defaults: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Table-driven test decorator with strict parameter validation.

    Every parameter in the test function must appear in each test case OR in defaults.
    Type checking happens at decoration time using the function's type hints.

    Args:
        cases: Test cases mapping name -> parameters dict.
               Values can be dict[str, Any] or MarkedCase (from marked() helper).
        defaults: Optional default values for parameters not present in all cases.

    Raises:
        ValueError: If cases is empty or duplicate case names detected
        TypeError: If parameter values don't match their type hints
        KeyError: If a required parameter is missing from a case (and not in defaults)

    Example:
        @param_table({
            "empty_string": {"text": "", "expected": ""},
            "one_character": {"text": "x", "expected": "x"},
        })
        def test_reverse(text: str, expected: str):
            assert reverse(text) == expected
    """
    if defaults is None:
        defaults = {}

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        # Get function signature and type hints
        sig = inspect.signature(func)
        params = sig.parameters

        # Filter out *args, **kwargs, self, and cls - we don't support these
        regular_params = {
            name: param
            for name, param in params.items()
            if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD,
                             inspect.Parameter.KEYWORD_ONLY)
            and name not in ("self", "cls")
        }

        # Get type hints for validation
        try:
            type_hints = get_type_hints(func)
        except Exception:
            # If we can't get type hints, just proceed without type checking
            type_hints = {}

        # Get function location for error messages
        try:
            filename = inspect.getsourcefile(func) or "<unknown>"
            lines, start_line = inspect.getsourcelines(func)
            location = f"{filename}:{start_line}"
        except Exception:
            location = "<unknown location>"

        # Validate cases is not empty
        if not cases:
            raise ValueError(
                f"@param_table requires at least one test case\n"
                f"  In function: {func.__name__} at {location}"
            )

        # Determine which parameters this decorator "owns" (mentioned in any case or defaults)
        # This allows nesting - each decorator manages its own parameters
        owned_params = set()
        for case_value in cases.values():
            if isinstance(case_value, MarkedCase):
                owned_params.update(case_value.params.keys())
            else:
                owned_params.update(case_value.keys())
        owned_params.update(defaults.keys())

        # Verify that owned params are actual function parameters
        function_param_names = set(regular_params.keys())
        extra_params = owned_params - function_param_names
        if extra_params:
            extra_list = ", ".join(sorted(extra_params))
            raise ValueError(
                f"@param_table provided parameter(s) not in function signature:\n"
                f"  Extra: {extra_list}\n"
                f"  Function parameters: {', '.join(sorted(function_param_names))}\n"
                f"\n"
                f"  In function: {func.__name__} at {location}"
            )

        # Build normalized cases and validate
        normalized_cases = []
        case_ids = []

        for case_name, case_value in cases.items():
            # Extract params and marks
            if isinstance(case_value, MarkedCase):
                case_params = case_value.params
                case_marks = case_value.marks
            else:
                case_params = case_value
                case_marks = ()

            # Combine case params with defaults
            combined_params = {**defaults, **case_params}

            # Check that all owned parameters are present in this case
            provided_param_names = set(combined_params.keys())
            missing_params = owned_params - provided_param_names

            if missing_params:
                missing_list = ", ".join(sorted(missing_params))
                provided_list = ", ".join(sorted(provided_param_names))
                raise KeyError(
                    f"@param_table missing required parameter(s) in test case '{case_name}':\n"
                    f"  Missing: {missing_list}\n"
                    f"  Provided: {provided_list}\n"
                    f"\n"
                    f"  Add the missing parameters or set defaults={{{missing_list}: ...}}\n"
                    f"  In function: {func.__name__} at {location}"
                )

            # Type check each parameter
            for param_name, param_value in combined_params.items():
                if param_name in type_hints:
                    expected_type = type_hints[param_name]
                    try:
                        check_type(param_value, expected_type)
                    except Exception as e:
                        actual_type = type(param_value).__name__
                        raise TypeError(
                            f"@param_table type mismatch in test case '{case_name}':\n"
                            f"  Parameter: {param_name}\n"
                            f"  Expected type: {expected_type}\n"
                            f"  Actual value: {param_value!r} (type: {actual_type})\n"
                            f"\n"
                            f"  In function: {func.__name__} at {location}"
                        ) from e

            # Store normalized case
            normalized_cases.append((case_name, combined_params, case_marks))
            case_ids.append(case_name)

        # Build parameter names list in consistent order
        # Use the order from the function signature, but only include owned params
        param_names_list = [name for name in regular_params.keys() if name in owned_params]

        # Build values for pytest.mark.parametrize
        if len(param_names_list) == 1:
            # Single parameter - use list of values
            param_name = param_names_list[0]
            values = []
            for case_name, combined_params, case_marks in normalized_cases:
                value = combined_params[param_name]
                if case_marks:
                    values.append(pytest.param(value, marks=case_marks, id=case_name))
                else:
                    values.append(pytest.param(value, id=case_name))
        else:
            # Multiple parameters - use list of tuples
            values = []
            for case_name, combined_params, case_marks in normalized_cases:
                value_tuple = tuple(combined_params[name] for name in param_names_list)
                if case_marks:
                    values.append(pytest.param(*value_tuple, marks=case_marks, id=case_name))
                else:
                    values.append(pytest.param(*value_tuple, id=case_name))

        # Delegate to pytest.mark.parametrize
        return pytest.mark.parametrize(
            ",".join(param_names_list), values
        )(func)

    return decorator
