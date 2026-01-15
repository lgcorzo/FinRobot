# FMP Adapter Stories

This document describes the Financial Modeling Prep (FMP) API adapter for market data.

## Overview

The FMP Adapter connects to the Financial Modeling Prep API to retrieve company profiles, financial statements, stock prices, and market metrics.

## Location

```
src/finrobot/data_access/data_source/
├── domains/market/
│   └── fmp_adapter.py       # DDD-style FMP adapter
└── fmp_utils.py             # FMP utility functions
```

## Key Functions

### FMPUtils

```python
from finrobot.data_access.data_source.fmp_utils import FMPUtils

# Initialize
fmp = FMPUtils()

# Company profile
profile = fmp.get_company_profile(ticker="AAPL")

# Financial statements
income = fmp.get_income_statement(ticker="AAPL", period="annual")
balance = fmp.get_balance_sheet(ticker="AAPL", period="annual")
cashflow = fmp.get_cash_flow_statement(ticker="AAPL", period="annual")

# Market data
price = fmp.get_stock_price(ticker="AAPL")
market_cap = fmp.get_historical_market_cap(ticker="AAPL")

# Financial metrics
metrics = fmp.get_financial_metrics(ticker="AAPL")
competitors = fmp.get_competitor_financial_metrics(ticker="AAPL")

# SEC filings link
filings = fmp.get_sec_filings(ticker="AAPL")
```

## Data Categories

| Category     | Endpoints                     |
| ------------ | ----------------------------- |
| Company Info | Profile, Executives, Peers    |
| Financials   | Income, Balance, Cash Flow    |
| Valuation    | Ratios, DCF, Enterprise Value |
| Market Data  | Price, Historical, Market Cap |
| SEC Filings  | 10-K, 10-Q, 8-K listings      |

## Environment Variables

```bash
FMP_API_KEY=your_fmp_api_key
```

## Usage in Agents

```python
# Agent tool registration
@register_tool
def get_company_fundamentals(ticker: str) -> dict:
    """Get company fundamental data from FMP."""
    fmp = FMPUtils()
    return {
        "profile": fmp.get_company_profile(ticker),
        "metrics": fmp.get_financial_metrics(ticker),
    }
```
