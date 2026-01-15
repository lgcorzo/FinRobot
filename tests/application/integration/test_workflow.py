"""Integration tests for agent workflow."""

import pytest
from unittest.mock import MagicMock, patch
from finrobot.models.agents.workflow import SingleAssistant
from finrobot.settings import FinRobotSettings


@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    return FinRobotSettings()


@patch("finrobot.models.agents.workflow.ChatAgent.run")
def test_single_assistant_chat(mock_run, mock_settings):
    """Test standard chat flow with mocked LLM."""

    # Configure mock to be awaitable
    async def mock_run_coro(*args, **kwargs):
        return "Mocked Response"

    mock_run.side_effect = mock_run_coro

    # Configure agent
    config = {"name": "TestAgent", "description": "A test agent"}

    # Instantiate assistant
    assistant = SingleAssistant(agent_config=config)

    # Run chat
    assistant.chat("Hello!")

    # Verify run was called
    assert mock_run.called


def test_single_assistant_initialization_error():
    """Test that missing config raises error."""
    with pytest.raises(AssertionError):
        SingleAssistant(agent_config={})  # Missing name
