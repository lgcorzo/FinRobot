"""Tests for analysis job."""

from unittest.mock import patch, MagicMock
from finrobot.application.jobs.analysis import FinancialAnalysisJob


@patch("finrobot.application.jobs.analysis.SingleAssistant")
def test_financial_analysis_job(mock_assistant_cls):
    """Test job execution."""
    mock_assistant = MagicMock()
    mock_assistant_cls.return_value = mock_assistant

    job = FinancialAnalysisJob(company="MSFT", model_id="gpt-3.5-turbo")
    job.run()

    mock_assistant_cls.assert_called_once()
    config_arg = mock_assistant_cls.call_args[0][0]
    assert config_arg["name"] == "Financial_Analyst"
    assert "MSFT" in config_arg["description"]

    mock_assistant.chat.assert_called_once()
    assert "MSFT" in mock_assistant.chat.call_args[0][0]
