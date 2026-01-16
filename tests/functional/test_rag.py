from unittest.mock import MagicMock, patch

import pytest

from finrobot.functional.rag import PROMPT_RAG_FUNC, get_rag_function


@patch("finrobot.functional.rag.RetrieveUserProxyAgent")
def test_get_rag_function(mock_agent_cls) -> None:
    # Mock instance
    mock_agent = MagicMock()
    mock_agent_cls.return_value = mock_agent

    # Mock internal methods
    mock_agent._check_update_context.return_value = (False, False)
    mock_agent.update_context = False
    mock_agent.message_generator.return_value = "Retrieved Content"

    # Test initialization
    retrieve_config = {"docs_path": ["/tmp/doc.txt"]}
    retrieve_content, agent_instance = get_rag_function(retrieve_config)

    assert agent_instance == mock_agent
    assert retrieve_config["customized_prompt"] == PROMPT_RAG_FUNC

    # Test retrieve_content calls - Case 1: No context update
    res = retrieve_content("query")
    assert res == "Retrieved Content"
    mock_agent.message_generator.assert_called()

    # Test retrieve_content logic - Case 2: Update context
    mock_agent._check_update_context.return_value = (True, False)
    mock_agent.update_context = True
    mock_agent._generate_retrieve_user_reply.return_value = (True, "New Context")

    res = retrieve_content("query2")
    assert res == "New Context"
    mock_agent._generate_retrieve_user_reply.assert_called_with("query2")


@patch("finrobot.functional.rag.RetrieveUserProxyAgent")
def test_get_rag_function_docstring(mock_agent_cls) -> None:
    retrieve_config = {"docs_path": ["doc1", "doc2"]}
    retrieve_content, _ = get_rag_function(retrieve_config)
    assert "Availale Documents" in retrieve_content.__doc__
    assert "doc1" in retrieve_content.__doc__
