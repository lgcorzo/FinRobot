"""Social Domain - Social media data."""

from .entities import SocialPost
from .repositories import SocialRepository
from .reddit_adapter import RedditAdapter

__all__ = [
    "SocialPost",
    "SocialRepository",
    "RedditAdapter",
]
