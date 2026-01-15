"""News Domain - Financial news and sentiment."""

from .entities import NewsArticle
from .finnhub_adapter import FinnHubNewsAdapter
from .repositories import NewsRepository

__all__ = [
    "NewsArticle",
    "NewsRepository",
    "FinnHubNewsAdapter",
]
