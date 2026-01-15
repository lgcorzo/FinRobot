import asyncio
from unittest.mock import MagicMock, patch

import pytest
from finrobot.models.agents.workflow import FinRobot, SingleAssistant


@pytest.fixture
def mock_agent_config():
    return {
        "name": "Finance_Analyst",
        "description": "Financial Analyst agent",
        "profile": "I am an analyst.",
        "toolkits": ["yfinance"],
    }


class TestWorkflow:
    @patch("finrobot.models.agents.workflow.get_toolkits")
    @patch("finrobot.models.agents.workflow.OpenAIChatClient")
    @patch("finrobot.models.agents.workflow.library")
    def test_finrobot_init_with_dict(self, mock_library, mock_client_cls, mock_get_toolkits, mock_agent_config):
        mock_get_toolkits.return_value = []
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        agent = FinRobot(agent_config=mock_agent_config)
        assert agent.name == "Finance_Analyst"
        assert agent._instructions == "I am an analyst."

    @patch("finrobot.models.agents.workflow.get_toolkits")
    @patch("finrobot.models.agents.workflow.OpenAIChatClient")
    @patch("finrobot.models.agents.workflow.library")
    def test_finrobot_init_with_library_name(self, mock_library, mock_client_cls, mock_get_toolkits, mock_agent_config):
        mock_get_toolkits.return_value = []
        mock_library.__contains__.return_value = True
        mock_library.__getitem__.return_value = mock_agent_config

        agent = FinRobot(agent_config="Finance_Analyst")
        assert agent.name == "Finance_Analyst"

    @patch("finrobot.models.agents.workflow.FinRobot")
    def test_single_assistant_chat(self, mock_finrobot_cls):
        mock_agent = MagicMock()
        mock_finrobot_cls.return_value = mock_agent

        # mock_agent.run is an async method
        async def mock_run(msg):
            pass

        mock_agent.run = mock_run

        assistant = SingleAssistant(agent_config={"name": "test", "description": "test"})
        # We need to test the chat method which runs async loop
        with patch("finrobot.models.agents.workflow.asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            mock_loop.is_running.return_value = False

            assistant.chat("test message")
            # Ensure the loop runner was called
            mock_loop.run_until_complete.assert_called_once()
        # To avoid RuntimeWarning: coroutine '...' was never awaited
        # we can inspect the call args and close the coroutine if needed,
        # or just ignore it since it's a mock return.
        # But wait, helper .chat() CALLS run_until_complete(coro).
        # We passed the coro to the mock. The mock didn't run it (it just returned mock value).
        # The coro object is left unawaited.
        # Let's extract it and close it.
        coro = mock_loop.run_until_complete.call_args[0][0]
        coro.close()
