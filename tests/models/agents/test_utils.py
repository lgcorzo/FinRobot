"""Tests for agent utils."""

from unittest.mock import MagicMock

from finrobot.models.agents.utils import instruction_trigger, order_trigger


def test_instruction_trigger():
    sender = MagicMock()
    sender.last_message.return_value = {"content": "instruction & resources saved to /tmp/file.txt"}
    assert instruction_trigger(sender)

    sender.last_message.return_value = {"content": "Hello world"}
    assert not instruction_trigger(sender)


def test_order_trigger():
    sender = MagicMock()
    sender.name = "Manager"
    sender.last_message.return_value = {"content": "[Order 1] Do something"}

    assert order_trigger(sender, "Manager", "[Order 1]")
    assert not order_trigger(sender, "Worker", "[Order 1]")
    assert not order_trigger(sender, "Manager", "[Order 2]")
