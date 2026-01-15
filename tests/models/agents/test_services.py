from unittest.mock import MagicMock, patch
from finrobot.models.agents.services.workflow_service import FinRobot, SingleAssistant
from finrobot.models.agents.services.prompt_service import leader_system_message, role_system_message, order_template


def test_workflow_service_import():
    # Verify we can instantiate from service module
    with patch("finrobot.models.agents.services.workflow_service.get_toolkits") as mock_get:
        with patch("finrobot.models.agents.services.workflow_service.OpenAIChatClient") as mock_client:
            agent = FinRobot(agent_config={"name": "test", "description": "test"})
            assert agent.name == "test"


def test_prompt_service_templates():
    # Verify templates can be formatted
    assert "{group_desc}" in leader_system_message
    formatted_leader = leader_system_message.format(group_desc="Developers")
    assert "Developers" in formatted_leader

    formatted_role = role_system_message.format(title="Analyst", responsibilities="Analyze data")
    assert "Analyst" in formatted_role
    assert "Analyze data" in formatted_role

    formatted_order = order_template.format(order="Buy stock")
    assert "Buy stock" in formatted_order
