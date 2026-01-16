"""Test settings configuration."""

import typing as T

import pytest

from finrobot.settings import FinRobotSettings


def test_settings_defaults() -> None:
    """Test default values for settings."""
    settings = FinRobotSettings()
    assert settings.openai_model == "gpt-4"
    assert settings.work_dir == "coding"
    assert settings.openai_api_key is None


def test_settings_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test environment variable overrides."""
    monkeypatch.setenv("OPENAI_MODEL", "gpt-3.5-turbo")
    settings = FinRobotSettings()
    assert settings.openai_model == "gpt-3.5-turbo"
