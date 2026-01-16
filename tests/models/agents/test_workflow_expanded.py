import asyncio
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest
from agent_framework import ChatMessage

from finrobot.models.agents.workflow import FinRobot, SingleAssistant, SingleAssistantRAG


@pytest.fixture
def mock_agent_config() -> Dict[str, Any]:
    return {
        "name": "TestAnalyst",
        "description": "Test analyst description",
        "responsibilities": ["Task 1", "Task 2"],
        "title": "Senior Analyst",
        "group_desc": "Group of analysts",
    }


class TestFinRobotExpanded:
    @patch("finrobot.models.agents.workflow.get_toolkits")
    @patch("finrobot.models.agents.workflow.OpenAIChatClient")
    def test_preprocess_config(self, mock_client_cls, mock_get_toolkits, mock_agent_config) -> None:  # type: ignore[no-untyped-def]
        mock_get_toolkits.return_value = []
        agent = FinRobot(agent_config=mock_agent_config)

        # Check if responsibilities were formatted
        assert "Senior Analyst" in agent._instructions
        assert " - Task 1" in agent._instructions
        assert " - Task 2" in agent._instructions
        # Check if group desc was formatted
        assert "leader of the following group members" in agent._instructions
        assert "Group of analysts" in agent._instructions

    @patch("finrobot.models.agents.workflow.get_toolkits")
    @patch("finrobot.models.agents.workflow.OpenAIChatClient")
    def test_preprocess_config_title_no_name(self, mock_client_cls, mock_get_toolkits) -> None:  # type: ignore[no-untyped-def]
        # Line 75 coverage
        mock_get_toolkits.return_value = []
        config = {"title": "Manager", "description": "test", "responsibilities": ["manage"]}
        agent = FinRobot(agent_config=config)
        assert agent.name == "Manager"

    def test_register_proxy(self) -> None:
        # Line 104 coverage
        agent_mock = MagicMock(spec=FinRobot)
        FinRobot.register_proxy(agent_mock, "proxy")  # Should just pass


class TestSingleAssistantExpanded:
    @patch("finrobot.models.agents.workflow.FinRobot")
    def test_chat_loop_logic(self, mock_finrobot_cls) -> None:  # type: ignore[no-untyped-def]
        mock_assistant = MagicMock()
        mock_finrobot_cls.return_value = mock_assistant

        async def mock_run(msg: Any) -> None:
            pass

        mock_assistant.run = mock_run

        assistant = SingleAssistant(agent_config={"name": "test", "description": "test"})

        # Test chat when loop is running (simulated)
        with patch("asyncio.get_event_loop") as mock_get_loop:
            mock_loop = MagicMock()
            mock_get_loop.return_value = mock_loop
            mock_loop.is_running.return_value = True

            with patch.object(assistant, "_run_chat_sync") as mock_run_sync:
                assistant.chat("hello")
                mock_run_sync.assert_called_once_with("hello")

        # Test RuntimeError in loop (Lines 141-143)
        with patch("asyncio.get_event_loop", side_effect=RuntimeError):
            with patch("asyncio.new_event_loop") as mock_new_loop:
                with patch("asyncio.set_event_loop"):
                    loop = MagicMock()
                    mock_new_loop.return_value = loop
                    loop.is_running.return_value = False
                    assistant.chat("hello")
                    mock_new_loop.assert_called_once()

        # Test _run_chat_sync (Line 164)
        with patch("asyncio.run") as mock_run_async:
            assistant._run_chat_sync("hello")
            mock_run_async.assert_called_once()

        # Test reset (Line 168)
        assistant.reset()  # Should just pass

    def test_rag_init(self) -> None:
        # Line 181
        with patch("finrobot.models.agents.workflow.FinRobot") as mock_finrobot_cls:
            rag = SingleAssistantRAG(agent_config={"name": "rag", "description": "rag"})
            assert rag.assistant is not None


@pytest.mark.asyncio
async def test_chat_async() -> None:
    # Line 159 implementation coverage
    with patch("finrobot.models.agents.workflow.FinRobot") as mock_finrobot_cls:
        mock_agent = MagicMock()
        mock_finrobot_cls.return_value = mock_agent
        mock_agent.run = MagicMock(return_value=asyncio.Future())
        mock_agent.run.return_value.set_result(None)

        assistant = SingleAssistant(agent_config={"name": "test", "description": "test"})
        await assistant._chat_async("test message")
        mock_agent.run.assert_called_once()
        args = mock_agent.run.call_args[0][0]
        assert isinstance(args, ChatMessage)
        assert args.text == "test message"
