"""FinRobot Data Source Module.

This module provides access to various financial data sources through
a Domain-Driven Design (DDD) architecture.

Domains:
    - market_data: Stock prices, company info, financials
    - filings: SEC filings, annual reports
    - news: Financial news and sentiment
    - social: Social media data

For new code, prefer importing from domains directly:
    from finrobot.data_source.domains.market_data import YFinanceAdapter

Legacy aliases are maintained for backward compatibility.
"""

import importlib.util

# Domain exports (preferred)
from .domains import (
    # Market Data
    MarketData,
    CompanyInfo,
    FinancialStatement,
    MarketDataRepository,
    YFinanceAdapter,
    FinnHubMarketAdapter,
    # Filings
    SECFiling,
    FilingsRepository,
    SECAdapter,
    FMPFilingsAdapter,
    # News
    NewsArticle,
    NewsRepository,
    FinnHubNewsAdapter,
    # Social
    SocialPost,
    SocialRepository,
    RedditAdapter,
)

# Backward compatibility aliases (deprecated)
from .finnhub_utils import FinnHubUtils
from .yfinance_utils import YFinanceUtils
from .fmp_utils import FMPUtils
from .sec_utils import SECUtils
from .reddit_utils import RedditUtils


__all__ = [
    # New DDD exports
    "MarketData",
    "CompanyInfo",
    "FinancialStatement",
    "MarketDataRepository",
    "YFinanceAdapter",
    "FinnHubMarketAdapter",
    "SECFiling",
    "FilingsRepository",
    "SECAdapter",
    "FMPFilingsAdapter",
    "NewsArticle",
    "NewsRepository",
    "FinnHubNewsAdapter",
    "SocialPost",
    "SocialRepository",
    "RedditAdapter",
    # Legacy aliases
    "FinnHubUtils",
    "YFinanceUtils",
    "FMPUtils",
    "SECUtils",
    "RedditUtils",
]

if importlib.util.find_spec("finnlp") is not None:
    from .finnlp_utils import FinNLPUtils

    __all__.append("FinNLPUtils")
