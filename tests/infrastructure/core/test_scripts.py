"""Tests for CLI scripts."""

import typing as T
from unittest.mock import MagicMock, patch

from finrobot.scripts import main


@patch("finrobot.scripts.FinRobotSettings")
@patch("finrobot.application.jobs.analysis.FinancialAnalysisJob")
def test_main_analyze(mock_job_cls: MagicMock, mock_settings_cls: MagicMock) -> None:
    """Test analyze task CLI."""
    mock_settings = MagicMock()
    mock_settings.openai_model = "gpt-4-test"
    mock_settings_cls.return_value = mock_settings

    mock_job = MagicMock()
    mock_job_cls.return_value = mock_job

    argv = ["--task", "analyze", "--company", "AAPL"]
    exit_code = main(argv)

    assert exit_code == 0
    mock_job_cls.assert_called_with(company="AAPL", model_id="gpt-4-test")
    mock_job.run.assert_called()


def test_main_no_args() -> None:
    """Test CLI with no args."""
    exit_code = main([])
    assert exit_code == 0
