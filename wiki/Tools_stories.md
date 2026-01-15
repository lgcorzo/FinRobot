# Tools Stories

This document describes the agent tools that provide specialized capabilities for financial analysis.

## Overview

Tools are callable functions that agents use to interact with external data sources and perform specialized computations. They bridge the gap between LLM reasoning and real-world data.

## Location

```
src/finrobot/models/agents/tools/
├── __init__.py
└── registry.py          # Tool registration and management
```

## Tool Categories

### Data Retrieval Tools

| Tool                       | Purpose                                      |
| -------------------------- | -------------------------------------------- |
| `get_company_profile`      | Fetch company information from FMP           |
| `get_stock_price`          | Get current/historical stock prices          |
| `get_financial_statements` | Retrieve income/balance/cash flow statements |
| `get_sec_filing`           | Download SEC filings (10-K, 10-Q, S-1)       |
| `get_news`                 | Fetch market news from Finnhub               |

### Analysis Tools

| Tool                 | Purpose                              |
| -------------------- | ------------------------------------ |
| `analyze_financials` | Perform financial statement analysis |
| `calculate_ratios`   | Compute financial ratios             |
| `compare_peers`      | Peer comparison analysis             |
| `generate_chart`     | Create data visualizations           |

### RAG Tools

| Tool             | Purpose                         |
| ---------------- | ------------------------------- |
| `query_earnings` | Query earnings call transcripts |
| `search_filings` | Semantic search in SEC filings  |

## Tool Registration

Tools are registered using a decorator pattern:

```python
from finrobot.models.agents.tools import register_tool

@register_tool
def get_company_profile(ticker: str) -> dict:
    """Fetch company profile from FMP API."""
    from finrobot.data_access.data_source import FMPUtils
    return FMPUtils.get_company_profile(ticker)
```

## Tool Usage by Agents

Agents automatically select and call tools based on the task:

```python
# Agent query
"Analyze AAPL's revenue growth over the last 3 years"

# Agent reasoning
# 1. Call get_financial_statements(ticker="AAPL", type="income")
# 2. Call calculate_ratios(metric="revenue_growth")
# 3. Call generate_chart(data=growth_data, type="line")
# 4. Synthesize findings into response
```
