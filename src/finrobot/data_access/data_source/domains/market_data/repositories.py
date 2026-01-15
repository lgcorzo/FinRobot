"""Market Data Domain Repository Interface."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pandas as pd

from .entities import MarketData, CompanyInfo, FinancialStatement


class MarketDataRepository(ABC):
    """Abstract repository for market data access."""

    @abstractmethod
    def get_stock_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> MarketData:
        """Retrieve historical stock price data."""
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> CompanyInfo:
        """Retrieve company profile information."""
        pass

    @abstractmethod
    def get_income_statement(self, symbol: str) -> FinancialStatement:
        """Retrieve income statement."""
        pass

    @abstractmethod
    def get_balance_sheet(self, symbol: str) -> FinancialStatement:
        """Retrieve balance sheet."""
        pass

    @abstractmethod
    def get_cash_flow(self, symbol: str) -> FinancialStatement:
        """Retrieve cash flow statement."""
        pass
