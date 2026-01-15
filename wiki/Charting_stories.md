# Charting Stories

This document describes the data visualization capabilities in FinRobot.

## Overview

The charting module creates financial visualizations including price charts, metric comparisons, and trend analysis using matplotlib and mplfinance.

## Location

```
src/finrobot/functional/
└── charting.py          # Data visualization functions
```

## Key Functions

### Stock Price Charts

```python
from finrobot.functional.charting import (
    plot_stock_price,
    plot_candlestick,
    plot_volume,
)

# Line chart
plot_stock_price(ticker="AAPL", period="1y", save_path="price.png")

# Candlestick chart
plot_candlestick(ticker="AAPL", period="6mo", save_path="candles.png")

# Volume chart
plot_volume(ticker="AAPL", period="1y", save_path="volume.png")
```

### Metric Visualizations

```python
from finrobot.functional.charting import (
    plot_pe_ratio_history,
    plot_revenue_trend,
    plot_peer_comparison,
)

# P/E ratio history
plot_pe_ratio_history(ticker="AAPL", years=5)

# Revenue trend
plot_revenue_trend(ticker="AAPL", quarters=12)

# Peer comparison bar chart
plot_peer_comparison(
    tickers=["AAPL", "MSFT", "GOOGL"],
    metric="gross_margin"
)
```

## Chart Types

| Type        | Use Case                           |
| ----------- | ---------------------------------- |
| Line        | Price trends, metric history       |
| Candlestick | OHLC price data                    |
| Bar         | Peer comparisons, categorical data |
| Area        | Cumulative metrics, stacked data   |
| Pie         | Revenue segments, market share     |

## Integration with Reports

Charts are automatically embedded in PDF reports:

```python
# Agent generates chart
chart_path = agent.generate_chart(ticker="AAPL", type="pe_history")

# Chart embedded in report section
section = Section(
    title="Valuation Analysis",
    content=analysis_text,
    charts=[chart_path]
)
```
