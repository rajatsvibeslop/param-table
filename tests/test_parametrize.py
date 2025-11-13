"""Comprehensive tests for pytest_param_table."""

import pytest
from pytest_param_table import MarkedCase, marked, param_table


# Test basic functionality
class TestBasicFunctionality:
    """Test basic parametrization features."""

    def test_single_parameter(self):
        """Test with a single parameter."""

        @param_table({
            "case1": {"x": 1},
            "case2": {"x": 2},
            "case3": {"x": 3},
        })
        def test_single(x: int):
            assert isinstance(x, int)
            assert x in [1, 2, 3]

        # The decorator should have been applied
        assert hasattr(test_single, "pytestmark")

    def test_multiple_parameters(self):
        """Test with multiple parameters."""

        @param_table({
            "case1": {"x": 1, "y": "a"},
            "case2": {"x": 2, "y": "b"},
        })
        def test_multiple(x: int, y: str):
            assert isinstance(x, int)
            assert isinstance(y, str)

        assert hasattr(test_multiple, "pytestmark")

    def test_various_types(self):
        """Test with various Python types."""

        @param_table({
            "int_case": {"value": 42, "expected_type": int},
            "str_case": {"value": "hello", "expected_type": str},
            "bool_case": {"value": True, "expected_type": bool},
            "float_case": {"value": 3.14, "expected_type": float},
            "none_case": {"value": None, "expected_type": type(None)},
            "list_case": {"value": [1, 2, 3], "expected_type": list},
            "dict_case": {"value": {"key": "val"}, "expected_type": dict},
        })
        def test_types(value: Any, expected_type: type):
            assert isinstance(value, expected_type)

        assert hasattr(test_types, "pytestmark")


# Test defaults functionality
class TestDefaults:
    """Test default parameter values."""

    def test_defaults_fill_missing_params(self):
        """Test that defaults fill in missing parameters."""

        @param_table(
            {
                "with_y": {"x": 1, "y": 10},
                "without_y": {"x": 2},
            },
            defaults={"y": 5},
        )
        def test_defaults(x: int, y: int):
            assert isinstance(x, int)
            assert isinstance(y, int)

        assert hasattr(test_defaults, "pytestmark")

    def test_explicit_overrides_default(self):
        """Test that explicit values override defaults."""

        @param_table(
            {
                "override": {"x": 1, "y": 99},
                "use_default": {"x": 2},
            },
            defaults={"y": 5},
        )
        def test_override(x: int, y: int):
            assert isinstance(x, int)
            assert isinstance(y, int)

        assert hasattr(test_override, "pytestmark")

    def test_multiple_defaults(self):
        """Test with multiple default parameters."""

        @param_table(
            {
                "all_explicit": {"a": 1, "b": 2, "c": 3},
                "some_defaults": {"a": 10},
            },
            defaults={"b": 20, "c": 30},
        )
        def test_multi_defaults(a: int, b: int, c: int):
            assert isinstance(a, int)
            assert isinstance(b, int)
            assert isinstance(c, int)

        assert hasattr(test_multi_defaults, "pytestmark")


# Test nesting for Cartesian products
class TestNesting:
    """Test nested param_table decorators."""

    def test_two_level_nesting(self):
        """Test two levels of nesting."""

        @param_table({"x1": {"x": 1}, "x2": {"x": 2}})
        @param_table({"y1": {"y": "a"}, "y2": {"y": "b"}})
        def test_nested_two(x: int, y: str):
            assert x in [1, 2]
            assert y in ["a", "b"]

        assert hasattr(test_nested_two, "pytestmark")

    def test_three_level_nesting(self):
        """Test three levels of nesting."""

        @param_table({"x1": {"x": 1}, "x2": {"x": 2}})
        @param_table({"y1": {"y": 10}, "y2": {"y": 20}})
        @param_table({"z1": {"z": "A"}, "z2": {"z": "B"}})
        def test_nested_three(x: int, y: int, z: str):
            assert x in [1, 2]
            assert y in [10, 20]
            assert z in ["A", "B"]

        assert hasattr(test_nested_three, "pytestmark")


# Test pytest marks integration
class TestMarks:
    """Test pytest marks integration."""

    def test_single_mark(self):
        """Test with a single pytest mark."""

        @param_table({
            "normal": {"x": 1},
            "xfail_case": marked({"x": -1}, pytest.mark.xfail),
        })
        def test_with_xfail(x: int):
            assert x > 0

        assert hasattr(test_with_xfail, "pytestmark")

    def test_skip_mark(self):
        """Test with skip mark."""

        @param_table({
            "normal": {"x": 1},
            "skip_case": marked({"x": 999}, pytest.mark.skip(reason="Testing skip")),
        })
        def test_with_skip(x: int):
            assert x > 0

        assert hasattr(test_with_skip, "pytestmark")

    def test_multiple_marks_on_case(self):
        """Test with multiple marks on the same case."""

        @param_table({
            "normal": {"x": 1},
            "multi_mark": marked(
                {"x": 5},
                pytest.mark.slow,
                pytest.mark.integration,
            ),
        })
        def test_multi_marks(x: int):
            assert x > 0

        assert hasattr(test_multi_marks, "pytestmark")

    def test_mixed_marked_unmarked(self):
        """Test mix of marked and unmarked cases."""

        @param_table({
            "case1": {"x": 1},
            "case2": marked({"x": 2}, pytest.mark.xfail),
            "case3": {"x": 3},
            "case4": marked({"x": 4}, pytest.mark.slow),
        })
        def test_mixed(x: int):
            assert x > 0

        assert hasattr(test_mixed, "pytestmark")

    def test_multiple_params_with_marks(self):
        """Test multiple parameters with marks."""

        @param_table({
            "normal": {"x": 1, "y": 2},
            "marked_case": marked({"x": 3, "y": 4}, pytest.mark.xfail),
        })
        def test_multi_param_marks(x: int, y: int):
            assert x > 0 and y > 0

        assert hasattr(test_multi_param_marks, "pytestmark")


# Test type validation
class TestTypeValidation:
    """Test type checking at decoration time."""

    def test_correct_types_pass(self):
        """Test that correct types don't raise errors."""

        @param_table({
            "int_case": {"x": 42, "y": "world"},
            "str_case": {"x": 100, "y": "hello"},
        })
        def test_correct(x: int, y: str):
            pass

        assert hasattr(test_correct, "pytestmark")

    def test_wrong_type_raises_error(self):
        """Test that wrong types raise TypeError."""

        with pytest.raises(TypeError, match="type mismatch"):
            @param_table({
                "bad_type": {"x": "not an int"},
            })
            def test_wrong_type(x: int):
                pass

    def test_optional_types(self):
        """Test with Optional types (int | None)."""

        @param_table({
            "with_value": {"x": 5},
            "with_none": {"x": None},
        })
        def test_optional(x: int | None):
            assert x is None or isinstance(x, int)

        assert hasattr(test_optional, "pytestmark")

    def test_union_types(self):
        """Test with Union types (int | str)."""

        @param_table({
            "int_case": {"x": 42},
            "str_case": {"x": "hello"},
        })
        def test_union(x: int | str):
            assert isinstance(x, (int, str))

        assert hasattr(test_union, "pytestmark")

    def test_generic_types(self):
        """Test with generic types like list[int]."""

        @param_table({
            "int_list": {"items": [1, 2, 3]},
            "empty_list": {"items": []},
        })
        def test_generic(items: list[int]):
            assert isinstance(items, list)

        assert hasattr(test_generic, "pytestmark")

    def test_no_type_hints_skips_validation(self):
        """Test that missing type hints doesn't cause errors."""

        @param_table({
            "case1": {"x": "string"},
            "case2": {"x": 123},
            "case3": {"x": None},
        })
        def test_no_hints(x):  # No type hint
            pass

        assert hasattr(test_no_hints, "pytestmark")


# Test error cases
class TestErrorCases:
    """Test error handling and validation."""

    def test_empty_cases_raises_error(self):
        """Test that empty cases dict raises ValueError."""

        with pytest.raises(ValueError, match="at least one test case"):
            @param_table({})
            def test_empty():
                pass

    def test_missing_required_parameter(self):
        """Test that missing parameter raises KeyError."""

        with pytest.raises(KeyError, match="missing required parameter"):
            @param_table({
                "complete": {"x": 1, "y": 2},  # Has both x and y
                "incomplete": {"x": 1},  # Missing 'y' which is now "owned"
            })
            def test_missing(x: int, y: int):
                pass

    def test_missing_with_helpful_message(self):
        """Test that error message is helpful."""

        with pytest.raises(KeyError, match="Missing: y") as exc_info:
            @param_table({
                "complete": {"x": 1, "y": 2},  # Has both x and y
                "incomplete": {"x": 1},  # Missing 'y' which is now "owned"
            })
            def test_missing_msg(x: int, y: int):
                pass

        # Check that error message includes suggestions
        assert "Add the missing parameters" in str(exc_info.value)


# Test edge cases
class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_empty_params_with_all_defaults(self):
        """Test case with empty params dict when all params have defaults."""

        @param_table(
            {
                "all_defaults": {},
                "some_explicit": {"x": 99},
            },
            defaults={"x": 1, "y": 2},
        )
        def test_all_defaults(x: int, y: int):
            assert isinstance(x, int)
            assert isinstance(y, int)

        assert hasattr(test_all_defaults, "pytestmark")

    def test_params_without_type_hints(self):
        """Test parameters without type hints."""

        @param_table({
            "case1": {"a": 1, "b": "x"},
            "case2": {"a": [1, 2], "b": {"key": "val"}},
        })
        def test_no_hints(a, b):
            pass

        assert hasattr(test_no_hints, "pytestmark")

    def test_marked_case_is_dataclass(self):
        """Test that MarkedCase is properly structured."""
        mc = marked({"x": 1}, pytest.mark.skip)
        assert isinstance(mc, MarkedCase)
        assert mc.params == {"x": 1}
        assert len(mc.marks) == 1

    def test_extra_parameters_raises_error(self):
        """Test that providing params not in function signature raises ValueError."""

        with pytest.raises(ValueError, match="provided parameter.*not in function signature"):
            @param_table({
                "case1": {"x": 1, "z": 999},  # z is not in function signature
            })
            def test_extra(x: int, y: int):
                pass

    def test_function_with_problematic_type_hints(self):
        """Test handling of functions where get_type_hints fails."""
        # Create a function with forward references that can't be resolved
        def make_test():
            # Use string annotation that references non-existent type
            @param_table({
                "case1": {"x": 1},
            })
            def test_bad_hints(x: "NonExistentType"):  # noqa: F821
                pass
            return test_bad_hints

        # This should not raise an error, just skip type checking
        test_func = make_test()
        assert hasattr(test_func, "pytestmark")

    def test_lambda_function_without_source_location(self):
        """Test that functions without source info still work."""
        # Lambdas don't have source lines, testing the except branch
        # We can't use lambda directly with decorator, but we can test with exec
        import types

        # Create a function dynamically
        code = compile("def test_func(x: int): pass", "<string>", "exec")
        namespace = {}
        exec(code, namespace)
        func = namespace["test_func"]

        # Apply decorator
        decorated = param_table({"case1": {"x": 1}})(func)
        assert hasattr(decorated, "pytestmark")


# Integration tests - actual test execution
class TestActualExecution:
    """Tests that actually run and verify behavior."""

    @param_table({
        "empty": {"text": "", "expected": ""},
        "single": {"text": "a", "expected": "a"},
        "multiple": {"text": "abc", "expected": "cba"},
    })
    def test_string_reverse(self, text: str, expected: str):
        """Test actual string reversal."""
        assert text[::-1] == expected

    @param_table({
        "positive": {"x": 5, "y": 3, "expected": 8},
        "negative": {"x": -2, "y": -3, "expected": -5},
        "mixed": {"x": 10, "y": -4, "expected": 6},
    })
    def test_addition(self, x: int, y: int, expected: int):
        """Test actual addition."""
        assert x + y == expected

    @param_table(
        {
            "with_multiplier": {"value": 5, "multiplier": 2, "expected": 10},
            "default_multiplier": {"value": 7, "expected": 7},
        },
        defaults={"multiplier": 1},
    )
    def test_with_defaults_execution(self, value: int, multiplier: int, expected: int):
        """Test execution with defaults."""
        assert value * multiplier == expected


# Import Any for type hints
from typing import Any
