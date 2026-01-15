"""Social Domain - Social media data."""

from .entities import SocialPost
from .reddit_adapter import RedditAdapter
from .repositories import SocialRepository

__all__ = [
    "SocialPost",
    "SocialRepository",
    "RedditAdapter",
]
