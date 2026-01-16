"""Tests for toolkits."""

import pandas as pd

from finrobot.tools import get_toolkits, get_toolkits_from_cls, stringify_output


class MockClass:
    def method_a(self) -> str:
        return "a"

    def _private_method(self) -> str:
        return "private"


def test_stringify_output() -> None:
    """Test output stringification."""

    @stringify_output  # type: ignore[untyped-decorator]
    def return_df() -> pd.DataFrame:
        return pd.DataFrame({"a": [1, 2]})

    @stringify_output  # type: ignore[untyped-decorator]
    def return_int() -> int:
        return 123

    assert isinstance(return_df(), str)
    assert "a" in return_df()
    assert return_int() == "123"


def test_get_toolkits_from_cls() -> None:
    """Test pulling methods from a class."""
    tools = get_toolkits_from_cls(MockClass)
    assert len(tools) == 1
    assert tools[0].__name__ == "method_a"

    tools_private = get_toolkits_from_cls(MockClass, include_private=True)
    assert len(tools_private) == 2


def test_get_toolkits_mixed() -> None:
    """Test getting tools from config list."""

    def my_tool() -> str:
        """Docstring"""
        return "tool"

    config = [MockClass, my_tool]

    tools = get_toolkits(config)
    assert len(tools) == 2  # 1 from MockClass, 1 from function
