"""Social Domain Entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SocialPost:
    """Represents a social media post."""

    id: str
    title: str
    content: str
    created_at: datetime
    source: str  # "reddit", "twitter", etc.
    score: int = 0
    num_comments: int = 0
    url: Optional[str] = None
    author: Optional[str] = None
