"""Agents Domain Entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class AgentProfile:
    """Represents an agent's configuration profile."""

    name: str
    description: str
    system_message: str
    model_id: str = "gpt-4"
    tools: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Message:
    """Represents a conversation message."""

    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """Represents a conversation history."""

    id: str
    agent_name: str
    messages: List[Message] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
