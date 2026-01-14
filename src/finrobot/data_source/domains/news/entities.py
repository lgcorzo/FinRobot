"""News Domain Entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class NewsArticle:
    """Represents a financial news article."""

    headline: str
    summary: str
    source: str
    published_at: datetime
    url: Optional[str] = None
    symbol: Optional[str] = None
    sentiment: Optional[float] = None  # -1 to 1
