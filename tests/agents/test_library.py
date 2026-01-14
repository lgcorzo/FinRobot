"""Tests for agent library configuration."""

import pytest
from finrobot.agents.agent_library import library


def test_library_structure():
    """Test library contains valid agent configs."""
    assert isinstance(library, dict)
    assert "Financial_Analyst" in library

    config = library["Financial_Analyst"]
    assert "name" in config
    assert "profile" in config


def test_market_analyst_tools():
    """Test agents with toolkits defined."""
    config = library["Market_Analyst"]
    assert "toolkits" in config
    assert isinstance(config["toolkits"], list)
    assert len(config["toolkits"]) > 0
