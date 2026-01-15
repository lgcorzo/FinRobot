"""Filings Domain - SEC filings, annual reports."""

from .entities import SECFiling
from .fmp_adapter import FMPFilingsAdapter
from .repositories import FilingsRepository
from .sec_adapter import SECAdapter

__all__ = [
    "SECFiling",
    "FilingsRepository",
    "SECAdapter",
    "FMPFilingsAdapter",
]
