import os
import re
import typing as T
from typing import Any, Dict, List, Optional

from .prompts import order_template


def instruction_trigger(sender: T.Any) -> bool:
    # Check if the last message contains the path to the instruction text file
    last_msg = sender.last_message()
    if last_msg and "content" in last_msg:
        return "instruction & resources saved to" in T.cast(str, last_msg["content"])
    return False


def instruction_message(recipient: T.Any, messages: T.List[T.Dict[str, T.Any]], sender: T.Any, config: T.Any) -> str:
    # Extract the path to the instruction text file from the last message
    msg_list = recipient.chat_messages_for_summary(sender)
    if not msg_list:
        return ""
    full_order = T.cast(str, msg_list[-1]["content"])
    txt_path = full_order.replace("instruction & resources saved to ", "").strip()
    if os.path.exists(txt_path):
        with open(txt_path, "r") as f:
            instruction = f.read() + "\n\nReply TERMINATE at the end of your response."
        return instruction
    return ""


def order_trigger(sender: T.Any, name: str, pattern: str) -> bool:
    # print(pattern)
    # print(sender.name)
    last_msg = sender.last_message()
    if last_msg and "content" in last_msg:
        return sender.name == name and pattern in T.cast(str, last_msg["content"])
    return False


def order_message(
    pattern: str, recipient: T.Any, messages: T.List[T.Dict[str, T.Any]], sender: T.Any, config: T.Any
) -> str:
    msg_list = recipient.chat_messages_for_summary(sender)
    if not msg_list:
        return ""
    full_order = T.cast(str, msg_list[-1]["content"])
    regex_pattern = rf"\[{pattern}\](?::)?\s*(.+?)(?=\n\[|$)"
    match = re.search(regex_pattern, full_order, re.DOTALL)
    if match:
        order = match.group(1).strip()
    else:
        order = full_order
    return order_template.format(order=order)
