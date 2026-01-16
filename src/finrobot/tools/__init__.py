import typing as T
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Type, Union

from pandas import DataFrame

from finrobot.data_access.data_source import FinnHubUtils, FMPUtils, RedditUtils, SECUtils, YFinanceUtils
from finrobot.functional import ReportAnalysisUtils, ReportChartUtils, ReportLabUtils
from finrobot.functional.coding import CodingUtils


def stringify_output(func: Callable[..., Any]) -> Callable[..., str]:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> str:
        result = func(*args, **kwargs)
        if isinstance(result, DataFrame):
            return T.cast(str, result.to_string())
        else:
            return str(result)

    return wrapper


def get_toolkits(
    config: List[Union[Dict[str, Any], Callable[..., Any], Type[Any]]], **kwargs: Any
) -> List[Callable[..., Any]]:
    """Get tools from a configuration list."""
    tools = []

    for tool in config:
        if isinstance(tool, type):
            tools.extend(get_toolkits_from_cls(tool, **kwargs))
            continue

        tool_dict = {"function": tool} if callable(tool) else tool
        if "function" not in tool_dict or not callable(tool_dict["function"]):
            raise ValueError("Function not found in tool configuration or not callable.")

        tool_function = tool_dict["function"]
        # name = tool_dict.get("name", tool_function.__name__)
        # description = tool_dict.get("description", tool_function.__doc__)

        # agent_framework expects callable tools. It might handle name/docstring from function itself.
        # We apply stringify_output wrapper.
        tools.append(stringify_output(tool_function))

    return tools


def get_coding_tools() -> List[Callable[..., Any]]:
    """Get code writing tools."""

    return get_toolkits(
        [
            {
                "function": CodingUtils.list_dir,
                "name": "list_files",
                "description": "List files in a directory.",
            },
            {
                "function": CodingUtils.see_file,
                "name": "see_file",
                "description": "Check the contents of a chosen file.",
            },
            {
                "function": CodingUtils.modify_code,
                "name": "modify_code",
                "description": "Replace old piece of code with new one.",
            },
            {
                "function": CodingUtils.create_file_with_code,
                "name": "create_file_with_code",
                "description": "Create a new file with provided code.",
            },
        ]
    )


def get_toolkits_from_cls(
    cls: Type[Any],
    include_private: bool = False,
) -> List[Callable[..., Any]]:
    """Get all methods of a class as tools."""
    if include_private:
        funcs = [func for func in dir(cls) if callable(getattr(cls, func)) and not func.startswith("__")]
    else:
        funcs = [
            func
            for func in dir(cls)
            if callable(getattr(cls, func)) and not func.startswith("__") and not func.startswith("_")
        ]
    return [getattr(cls, func) for func in funcs]
