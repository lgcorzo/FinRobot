# Quantitative Stories

This document describes the quantitative analysis and metrics calculation capabilities.

## Overview

The quantitative module provides financial ratio calculations, valuation models, and statistical analysis for investment research.

## Location

```
src/finrobot/functional/
└── quantitative.py      # Quantitative metrics and calculations
```

## Financial Ratios

### Profitability Ratios

```python
from finrobot.functional.quantitative import get_profitability_ratios

ratios = get_profitability_ratios(ticker="AAPL")
# Returns:
# - gross_margin
# - operating_margin
# - net_margin
# - roe (Return on Equity)
# - roa (Return on Assets)
# - roic (Return on Invested Capital)
```

### Liquidity Ratios

```python
from finrobot.functional.quantitative import get_liquidity_ratios

ratios = get_liquidity_ratios(ticker="AAPL")
# Returns:
# - current_ratio
# - quick_ratio
# - cash_ratio
```

### Solvency Ratios

```python
from finrobot.functional.quantitative import get_solvency_ratios

ratios = get_solvency_ratios(ticker="AAPL")
# Returns:
# - debt_to_equity
# - interest_coverage
# - debt_to_ebitda
```

### Valuation Metrics

```python
from finrobot.functional.quantitative import get_valuation_metrics

metrics = get_valuation_metrics(ticker="AAPL")
# Returns:
# - pe_ratio
# - forward_pe
# - peg_ratio
# - price_to_book
# - ev_to_ebitda
# - ev_to_revenue
```

## Valuation Models

### DCF Valuation

```python
from finrobot.functional.quantitative import dcf_valuation

dcf = dcf_valuation(
    ticker="AAPL",
    growth_rate=0.08,
    terminal_growth=0.03,
    discount_rate=0.10,
    forecast_years=5,
)
# Returns:
# - intrinsic_value
# - upside_potential
# - sensitivity_table
```

## Peer Comparison

```python
from finrobot.functional.quantitative import peer_comparison

comparison = peer_comparison(
    ticker="AAPL",
    peers=["MSFT", "GOOGL", "AMZN"],
    metrics=["pe_ratio", "revenue_growth", "gross_margin"]
)
```
