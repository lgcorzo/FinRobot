"""News Domain - Financial news and sentiment."""

from .entities import NewsArticle
from .repositories import NewsRepository
from .finnhub_adapter import FinnHubNewsAdapter

__all__ = [
    "NewsArticle",
    "NewsRepository",
    "FinnHubNewsAdapter",
]
