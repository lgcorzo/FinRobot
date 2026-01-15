"""Data Source Domains - DDD structure for financial data access."""

from .filings import (
    FilingsRepository,
    FMPFilingsAdapter,
    SECAdapter,
    SECFiling,
)
from .market_data import (
    CompanyInfo,
    FinancialStatement,
    FinnHubMarketAdapter,
    MarketData,
    MarketDataRepository,
    YFinanceAdapter,
)
from .news import (
    FinnHubNewsAdapter,
    NewsArticle,
    NewsRepository,
)
from .social import (
    RedditAdapter,
    SocialPost,
    SocialRepository,
)

__all__ = [
    # Market Data
    "MarketData",
    "CompanyInfo",
    "FinancialStatement",
    "MarketDataRepository",
    "YFinanceAdapter",
    "FinnHubMarketAdapter",
    # Filings
    "SECFiling",
    "FilingsRepository",
    "SECAdapter",
    "FMPFilingsAdapter",
    # News
    "NewsArticle",
    "NewsRepository",
    "FinnHubNewsAdapter",
    # Social
    "SocialPost",
    "SocialRepository",
    "RedditAdapter",
]
