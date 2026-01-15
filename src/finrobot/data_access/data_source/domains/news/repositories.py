"""News Domain Repository Interface."""

from abc import ABC, abstractmethod

import pandas as pd


class NewsRepository(ABC):
    """Abstract repository for news data access."""

    @abstractmethod
    def get_company_news(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        max_items: int = 10,
    ) -> pd.DataFrame:
        """Retrieve news for a company."""
        pass
