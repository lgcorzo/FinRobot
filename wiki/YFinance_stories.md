# YFinance Adapter Stories

This document describes the Yahoo Finance adapter for historical market data.

## Overview

The YFinance Adapter uses the `yfinance` library to retrieve historical stock prices, dividends, splits, and company information.

## Location

```
src/finrobot/data_access/data_source/
├── domains/market/
│   └── yfinance_adapter.py  # DDD-style YFinance adapter
└── yfinance_utils.py        # YFinance utility functions
```

## Key Functions

```python
from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

yf = YFinanceUtils()

# Historical prices
prices = yf.get_historical_prices(
    ticker="AAPL",
    period="1y",
    interval="1d"
)

# Company info
info = yf.get_company_info(ticker="AAPL")

# Dividends
dividends = yf.get_dividends(ticker="AAPL")

# Stock splits
splits = yf.get_splits(ticker="AAPL")

# Options chain
options = yf.get_options(ticker="AAPL")
```

## Data Types

| Type              | Description                     |
| ----------------- | ------------------------------- |
| Historical Prices | OHLCV data at various intervals |
| Company Info      | Basic company information       |
| Financials        | Income, Balance, Cash Flow      |
| Dividends         | Historical dividend payments    |
| Splits            | Stock split history             |
| Options           | Options chain data              |

## Period Options

| Period                  | Description       |
| ----------------------- | ----------------- |
| `1d`, `5d`              | Days              |
| `1mo`, `3mo`, `6mo`     | Months            |
| `1y`, `2y`, `5y`, `10y` | Years             |
| `ytd`                   | Year to date      |
| `max`                   | Maximum available |

## Usage in Charts

```python
from finrobot.functional.charting import plot_stock_price
from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

# Get data
yf = YFinanceUtils()
prices = yf.get_historical_prices("AAPL", "1y")

# Plot
plot_stock_price(prices, save_path="aapl_price.png")
```
