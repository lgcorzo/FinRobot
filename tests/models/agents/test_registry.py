"""Tests for tool registry."""

from finrobot.models.agents.tools.registry import (
    get_coding_tools,
    get_toolkits,
    get_toolkits_from_cls,
)


class TestToolRegistry:
    """Test suite for tool registry."""

    def test_get_toolkits_from_list(self):
        """Test that get_toolkits works with a list of functions."""

        def sample_func():
            return "test"

        result = get_toolkits([sample_func])

        assert isinstance(result, list)
        assert len(result) == 1
        assert callable(result[0])

    def test_get_toolkits_from_class(self):
        """Test that get_toolkits works with a class."""

        class SampleClass:
            @staticmethod
            def method_one():
                return "one"

            @staticmethod
            def method_two():
                return "two"

        result = get_toolkits([SampleClass])

        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_toolkits_from_dict(self):
        """Test that get_toolkits works with dict configuration."""

        def sample_func():
            return "test"

        config = [{"function": sample_func, "name": "test_func"}]
        result = get_toolkits(config)

        assert isinstance(result, list)
        assert len(result) == 1

    def test_get_coding_tools(self):
        """Test that get_coding_tools returns tools."""
        result = get_coding_tools()

        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_toolkits_from_cls(self):
        """Test that get_toolkits_from_cls extracts class methods."""

        class TestClass:
            @staticmethod
            def public_method():
                pass

            @staticmethod
            def _private_method():
                pass

        result = get_toolkits_from_cls(TestClass)

        assert isinstance(result, list)
        # Should only include public methods by default
        assert any(callable(f) for f in result)

    def test_get_toolkits_from_cls_include_private(self):
        """Test that get_toolkits_from_cls can include private methods."""

        class TestClass:
            @staticmethod
            def public_method():
                pass

            @staticmethod
            def _private_method():
                pass

        result = get_toolkits_from_cls(TestClass, include_private=True)

        assert isinstance(result, list)
        assert len(result) >= 2
