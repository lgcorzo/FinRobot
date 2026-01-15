# Analysis Stories

This document describes the financial analysis capabilities in the functional layer.

## Overview

The analysis module provides core financial statement analysis functions, including income statement, balance sheet, and cash flow analysis.

## Location

```
src/finrobot/functional/
├── analyzer.py          # Financial statement analysis
└── quantitative.py      # Quantitative metrics and ratios
```

## Key Functions

### Financial Statement Analysis

```python
from finrobot.functional.analyzer import (
    analyze_income_statement,
    analyze_balance_sheet,
    analyze_cash_flow,
)

# Income statement analysis
income_analysis = analyze_income_statement(ticker="AAPL", year=2023)

# Balance sheet analysis
balance_analysis = analyze_balance_sheet(ticker="AAPL", year=2023)

# Cash flow analysis
cashflow_analysis = analyze_cash_flow(ticker="AAPL", year=2023)
```

### Quantitative Metrics

```python
from finrobot.functional.quantitative import (
    calculate_financial_ratios,
    calculate_dcf_valuation,
    get_peer_comparison,
)

# Financial ratios
ratios = calculate_financial_ratios(ticker="AAPL")
# Returns: P/E, EV/EBITDA, ROE, ROA, Debt/Equity, etc.

# DCF valuation
dcf = calculate_dcf_valuation(ticker="AAPL", growth_rate=0.10)

# Peer comparison
peers = get_peer_comparison(ticker="AAPL", metrics=["pe_ratio", "revenue_growth"])
```

## Analysis Output

| Metric Type   | Examples                                   |
| ------------- | ------------------------------------------ |
| Profitability | Gross Margin, Operating Margin, Net Margin |
| Liquidity     | Current Ratio, Quick Ratio                 |
| Solvency      | Debt/Equity, Interest Coverage             |
| Efficiency    | Asset Turnover, Inventory Turnover         |
| Valuation     | P/E, P/B, EV/EBITDA, DCF                   |
