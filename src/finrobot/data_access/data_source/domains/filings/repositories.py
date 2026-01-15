"""Filings Domain Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional

from .entities import SECFiling


class FilingsRepository(ABC):
    """Abstract repository for SEC filings access."""

    @abstractmethod
    def get_sec_report(
        self,
        symbol: str,
        fiscal_year: str = "latest",
    ) -> SECFiling:
        """Retrieve SEC 10-K report."""
        pass
