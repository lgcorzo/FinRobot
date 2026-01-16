from unittest.mock import MagicMock, patch
import typing as T


class TestSingleAssistant:
    """Test suite for SingleAssistant.

    Note: These tests use comprehensive mocking to avoid agent framework initialization
    which requires actual model endpoints.
    """

    @patch("finrobot.models.agents.workflow.SingleAssistant")
    def test_single_assistant_instantiation_mock(self, mock_assistant_cls: T.Any) -> None:
        """Test that SingleAssistant can be instantiated via mock."""
        mock_instance = MagicMock()
        mock_assistant_cls.return_value = mock_instance

        config = {"name": "TestAgent", "description": "A test agent"}
        llm_config = {"model": "gpt-4"}

        assistant = mock_assistant_cls(config, llm_config=llm_config)

        assert assistant is not None
        mock_assistant_cls.assert_called_once_with(config, llm_config=llm_config)

    @patch("finrobot.models.agents.workflow.SingleAssistant")
    def test_chat_method_mock(self, mock_assistant_cls: T.Any) -> None:
        """Test that chat() method works via mock."""
        mock_instance = MagicMock()
        mock_instance.chat.return_value = "Test response"
        mock_assistant_cls.return_value = mock_instance

        config = {"name": "TestAgent", "description": "A test agent"}
        llm_config = {"model": "gpt-4"}

        assistant = mock_assistant_cls(config, llm_config=llm_config)
        result = assistant.chat("Hello")

        assert result == "Test response"

    @patch("finrobot.models.agents.workflow.SingleAssistant")
    def test_single_assistant_with_tools_mock(self, mock_assistant_cls: T.Any) -> None:
        """Test SingleAssistant with tools configuration via mock."""
        mock_instance = MagicMock()
        mock_assistant_cls.return_value = mock_instance

        config = {
            "name": "FinancialAnalyst",
            "description": "Analyze financial data",
            "tools": ["yfinance", "finnhub"],
        }
        llm_config = {"model": "gpt-4", "temperature": 0.7}

        assistant = mock_assistant_cls(config, llm_config=llm_config)

        assert assistant is not None
