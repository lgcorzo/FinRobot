"""Filings Domain - SEC filings, annual reports."""

from .entities import SECFiling
from .repositories import FilingsRepository
from .sec_adapter import SECAdapter
from .fmp_adapter import FMPFilingsAdapter

__all__ = [
    "SECFiling",
    "FilingsRepository",
    "SECAdapter",
    "FMPFilingsAdapter",
]
