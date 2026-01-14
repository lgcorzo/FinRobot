"""Social Domain Repository Interface."""

from abc import ABC, abstractmethod
import pandas as pd


class SocialRepository(ABC):
    """Abstract repository for social media data access."""

    @abstractmethod
    def get_posts(
        self,
        query: str,
        start_date: str,
        end_date: str,
        limit: int = 100,
    ) -> pd.DataFrame:
        """Retrieve social media posts matching query."""
        pass
