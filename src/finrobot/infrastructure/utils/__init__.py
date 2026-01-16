"""Infrastructure Layer - General utilities."""

import typing as T
from datetime import datetime, timedelta

# %% UTILS


def get_current_date() -> str:
    """Get the current date as yyyy-mm-dd.

    Returns:
        str: current date.
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_next_weekday(date: datetime | None = None) -> datetime:
    """Get the next weekday of a given date.

    If the date is a weekday, return the same date.
    If the date is a weekend, return the next Monday.

    Parameters:
        date (datetime | None): date to check. Default to now.

    Returns:
        datetime: next weekday.
    """
    if date is None:
        date = datetime.now()
    if date.weekday() == 5:  # Saturday
        return date + timedelta(days=2)
    elif date.weekday() == 6:  # Sunday
        return date + timedelta(days=1)
    return date


def decorate_all_methods(decorator: T.Callable[..., T.Any]) -> T.Callable[[T.Type[T.Any]], T.Type[T.Any]]:
    """Decorate all methods of a class.

    Parameters:
        decorator (Callable): decorator to apply.

    Returns:
        Callable: class decorator.
    """

    def dectheclass(cls: T.Type[T.Any]) -> T.Type[T.Any]:
        for name, m in vars(cls).items():
            if callable(m) and not name.startswith("__"):
                setattr(cls, name, decorator(m))
        return cls

    return dectheclass


__all__ = ["get_current_date", "get_next_weekday", "decorate_all_methods"]
