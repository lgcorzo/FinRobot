"""Tests for prompts templates."""

from finrobot.models.agents.prompts import leader_system_message, role_system_message


def test_leader_prompt_format() -> None:
    """Test leader prompt formatting."""
    formatted = leader_system_message.format(group_desc="Team A")
    assert "Team A" in formatted
    assert "You are the leader" in formatted


def test_role_prompt_format() -> None:
    """Test role prompt formatting."""
    formatted = role_system_message.format(title="Manager", responsibilities="Manage stuff")
    assert "Manager" in formatted
    assert "Manage stuff" in formatted
