"""Tests for general utilities."""

import json
import os
from datetime import datetime

import pandas as pd

from finrobot.infrastructure.io.files import register_keys_from_json, save_output
from finrobot.infrastructure.utils import get_current_date, get_next_weekday


def test_save_output(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Test saving dataframe to CSV."""
    df = pd.DataFrame({"a": [1, 2]})
    file_path = tmp_path / "test.csv"
    save_output(df, "Test Data", str(file_path))
    assert file_path.exists()

    # Test none path
    save_output(df, "Test Data", None)
    # Should just pass


def test_get_current_date() -> None:
    """Test date format."""
    d = get_current_date()
    assert isinstance(d, str)
    assert len(d.split("-")) == 3


def test_register_keys_from_json(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Test environment variable registration."""
    config = {"TEST_KEY_123": "VALUE_123"}
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f)

    register_keys_from_json(str(config_path))
    assert os.environ["TEST_KEY_123"] == "VALUE_123"


def test_get_next_weekday() -> None:
    """Test weekday calculation."""
    # Monday
    d1 = datetime(2025, 1, 13)
    assert get_next_weekday(d1) == d1

    # Saturday -> Monday
    d2 = datetime(2025, 1, 18)
    next_day = get_next_weekday(d2)
    assert next_day.weekday() == 0
    assert next_day == datetime(2025, 1, 20)
