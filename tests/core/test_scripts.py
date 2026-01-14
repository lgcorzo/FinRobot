"""Tests for CLI scripts."""

from unittest.mock import patch, MagicMock
from finrobot.scripts import main


@patch("finrobot.scripts.FinRobotSettings")
@patch("finrobot.agents.workflow.SingleAssistant")
def test_main_analyze(mock_assistant_cls, mock_settings_cls):
    """Test analyze task CLI."""
    mock_settings = MagicMock()
    mock_settings.openai_model = "gpt-4-test"
    mock_settings_cls.return_value = mock_settings

    mock_assistant = MagicMock()
    mock_assistant_cls.return_value = mock_assistant

    argv = ["--task", "analyze", "--company", "AAPL"]
    exit_code = main(argv)

    assert exit_code == 0
    mock_assistant_cls.assert_called()
    mock_assistant.chat.assert_called()
    args, _ = mock_assistant.chat.call_args
    assert "AAPL" in args[0]


def test_main_no_args():
    """Test CLI with no args."""
    exit_code = main([])
    assert exit_code == 0
