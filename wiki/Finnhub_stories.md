# Finnhub Adapter Stories

This document describes the Finnhub adapter for real-time market news and sentiment.

## Overview

The Finnhub Adapter connects to the Finnhub API for real-time market news, company fundamentals, and sentiment analysis data.

## Location

```
src/finrobot/data_access/data_source/
├── domains/market/
│   └── finnhub_adapter.py   # DDD-style Finnhub adapter
└── finnhub_utils.py         # Finnhub utility functions
```

## Key Functions

```python
from finrobot.data_access.data_source.finnhub_utils import FinnhubUtils

fh = FinnhubUtils()

# Company news
news = fh.get_company_news(
    ticker="AAPL",
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Basic financials
financials = fh.get_basic_financials(ticker="AAPL")

# Recommendations
recommendations = fh.get_recommendations(ticker="AAPL")

# Price target
target = fh.get_price_target(ticker="AAPL")

# Earnings surprises
earnings = fh.get_earnings_surprises(ticker="AAPL")
```

## Data Categories

| Category        | Description                      |
| --------------- | -------------------------------- |
| News            | Company-specific news articles   |
| Financials      | Basic financial metrics          |
| Recommendations | Analyst buy/sell ratings         |
| Price Targets   | Analyst price forecasts          |
| Earnings        | Historical earnings vs estimates |

## Environment Variables

```bash
FINNHUB_API_KEY=your_finnhub_api_key
```

## Usage in Agents

The Finnhub adapter is commonly used for market sentiment analysis:

```python
# Agent analyzes news sentiment
news = fh.get_company_news("AAPL", "2024-01-01", "2024-01-31")

# LLM analyzes sentiment from headlines
sentiment = agent.analyze_sentiment(news)
```
