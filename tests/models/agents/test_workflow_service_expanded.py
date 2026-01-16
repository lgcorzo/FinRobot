import asyncio
import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from agent_framework import ChatMessage

from finrobot.models.agents.services.workflow_service import FinRobot, SingleAssistant, SingleAssistantRAG


@pytest.fixture
def mock_openai_client() -> None:
    with patch("finrobot.models.agents.services.workflow_service.OpenAIChatClient") as mock_client_cls:
        yield mock_client_cls


@pytest.fixture
def mock_toolkits() -> None:
    with patch("finrobot.models.agents.services.workflow_service.get_toolkits") as mock_get:
        mock_get.return_value = []
        yield mock_get


def test_finrobot_init_complex(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {
        "name": "TestAgent",
        "description": "desc",
        "title": "Agent Title",
        "responsibilities": ["Task 1", "Task 2"],
        "group_desc": "Leader of Group",
    }
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        agent = FinRobot("TestAgent_Shadow")
        assert agent.name == "TestAgent_Shadow"
        instr = getattr(agent, "_instructions", getattr(agent, "instructions", ""))
        assert "Agent Title" in instr
        assert "Leader of Group" in instr
        assert "Task 1" in agent.description


def test_single_assistant_chat_loops(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {"name": "TestAgent", "description": "desc"}
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        assistant = SingleAssistant("TestAgent")

        # Mock a loop that can run_until_complete
        mock_loop = MagicMock()
        mock_loop.is_running.return_value = False

        with patch("asyncio.get_event_loop", return_value=mock_loop):
            with patch.object(assistant, "_chat_async", return_value=MagicMock()) as mock_async:
                assistant.chat("hello")
                mock_loop.run_until_complete.assert_called_once()

        # Test line 140-143 (RuntimeError branch)
        with patch("asyncio.get_event_loop", side_effect=RuntimeError):
            with patch("asyncio.new_event_loop", return_value=mock_loop) as mock_new:
                with patch("asyncio.set_event_loop") as mock_set:
                    with patch.object(assistant, "_chat_async", return_value=MagicMock()):
                        assistant.chat("hello")
                        mock_new.assert_called_once()
                        mock_set.assert_called_once()

        # Test line 145-148 (is_running branch)
        mock_loop.is_running.return_value = True
        with patch("asyncio.get_event_loop", return_value=mock_loop):
            with patch.object(assistant, "_run_chat_sync") as mock_sync:
                assistant.chat("hello")
                mock_sync.assert_called_once()


def test_single_assistant_reset(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {"name": "TestAgent", "description": "desc"}
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        assistant = SingleAssistant("TestAgent")
        assistant.reset()


@pytest.mark.asyncio
async def test_chat_async_internals(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {"name": "TestAgent", "description": "desc"}
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        assistant = SingleAssistant("TestAgent")

        # Simulating the async run
        async def mock_run(*args: Any, **kwargs: Any) -> None:
            return None

        with patch.object(assistant.assistant, "run", side_effect=mock_run) as mock_run_patch:
            await assistant._chat_async("test message")
            mock_run_patch.assert_called_once()


def test_run_chat_sync(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {"name": "TestAgent", "description": "desc"}
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        assistant = SingleAssistant("TestAgent")
        with patch("asyncio.run") as mock_run_async:
            assistant._run_chat_sync("hello")
            mock_run_async.assert_called_once()


def test_single_assistant_rag_init(mock_openai_client, mock_toolkits) -> None:  # type: ignore[no-untyped-def]
    agent_config = {"name": "TestAgent", "description": "desc"}
    with patch("finrobot.models.agents.services.workflow_service.library", {"TestAgent": agent_config}):
        assistant = SingleAssistantRAG("TestAgent")
        assert assistant.assistant is not None
