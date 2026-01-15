"""Market Data Domain Entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional

import pandas as pd


@dataclass
class MarketData:
    """Represents OHLCV market data for a security."""

    symbol: str
    data: pd.DataFrame  # DataFrame with Open, High, Low, Close, Volume
    start_date: datetime
    end_date: datetime

    def to_dataframe(self) -> pd.DataFrame:
        return self.data


@dataclass
class CompanyInfo:
    """Represents company profile information."""

    symbol: str
    name: str
    industry: str
    sector: str
    country: str
    website: Optional[str] = None
    description: Optional[str] = None
    market_cap: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FinancialStatement:
    """Represents a financial statement (income, balance, cashflow)."""

    symbol: str
    statement_type: str  # "income", "balance_sheet", "cash_flow"
    data: pd.DataFrame
    period: str = "annual"  # "annual" or "quarterly"
