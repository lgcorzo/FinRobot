"""Data Source Domains - DDD structure for financial data access."""

from .market_data import (
    MarketData,
    CompanyInfo,
    FinancialStatement,
    MarketDataRepository,
    YFinanceAdapter,
    FinnHubMarketAdapter,
)
from .filings import (
    SECFiling,
    FilingsRepository,
    SECAdapter,
    FMPFilingsAdapter,
)
from .news import (
    NewsArticle,
    NewsRepository,
    FinnHubNewsAdapter,
)
from .social import (
    SocialPost,
    SocialRepository,
    RedditAdapter,
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
