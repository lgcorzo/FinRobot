"""Tests for toolkits."""

import pytest
import pandas as pd
from finrobot.toolkits import stringify_output, get_toolkits, get_toolkits_from_cls


class MockClass:
    def method_a(self):
        return "a"

    def _private_method(self):
        return "private"


def test_stringify_output():
    """Test output stringification."""

    @stringify_output
    def return_df():
        return pd.DataFrame({"a": [1, 2]})

    @stringify_output
    def return_int():
        return 123

    assert isinstance(return_df(), str)
    assert "a" in return_df()
    assert return_int() == "123"


def test_get_toolkits_from_cls():
    """Test pulling methods from a class."""
    tools = get_toolkits_from_cls(MockClass)
    assert len(tools) == 1
    assert tools[0].__name__ == "method_a"

    tools_private = get_toolkits_from_cls(MockClass, include_private=True)
    assert len(tools_private) == 2


def test_get_toolkits_mixed():
    """Test getting tools from config list."""

    def my_tool():
        """Docstring"""
        return "tool"

    config = [MockClass, my_tool]

    tools = get_toolkits(config)
    assert len(tools) == 2  # 1 from MockClass, 1 from function
