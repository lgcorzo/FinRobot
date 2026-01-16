import os
import re
from unittest.mock import MagicMock, patch

import pytest

from finrobot.models.agents.utils import instruction_message, instruction_trigger, order_message, order_trigger


def test_instruction_trigger() -> None:
    sender = MagicMock()
    sender.last_message.return_value = {"content": "instruction & resources saved to some_path"}
    assert instruction_trigger(sender) is True

    sender.last_message.return_value = {"content": "something else"}
    assert instruction_trigger(sender) is False


def test_instruction_message(tmp_path) -> None:
    sender = MagicMock()
    recipient = MagicMock()

    # Create a dummy instruction file
    instr_file = tmp_path / "instruction.txt"
    instr_file.write_text("Do some analysis.")

    recipient.chat_messages_for_summary.return_value = [{"content": f"instruction & resources saved to {instr_file}"}]

    instruction = instruction_message(recipient, [], sender, {})
    assert "Do some analysis." in instruction
    assert "TERMINATE" in instruction


def test_order_trigger() -> None:
    sender = MagicMock()
    sender.name = "Analyst"
    sender.last_message.return_value = {"content": "Execute [TRADE] order"}

    assert order_trigger(sender, "Analyst", "[TRADE]") is True
    assert order_trigger(sender, "Manager", "[TRADE]") is False
    assert order_trigger(sender, "Analyst", "[ANALYSIS]") is False


def test_order_message() -> None:
    sender = MagicMock()
    recipient = MagicMock()

    # Test match
    recipient.chat_messages_for_summary.return_value = [{"content": "[TRADE]: Buy AAPL\n[NEXT]"}]
    order = order_message("TRADE", recipient, [], sender, {})
    assert "Buy AAPL" in order

    # Test no match
    recipient.chat_messages_for_summary.return_value = [{"content": "Just a regular message"}]
    order = order_message("TRADE", recipient, [], sender, {})
    assert "Just a regular message" in order
