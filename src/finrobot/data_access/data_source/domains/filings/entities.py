"""Filings Domain Entities."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SECFiling:
    """Represents an SEC filing."""

    symbol: str
    form_type: str  # "10-K", "10-Q", "8-K", etc.
    filing_date: datetime
    url: str
    fiscal_year: Optional[str] = None
    fiscal_period: Optional[str] = None
