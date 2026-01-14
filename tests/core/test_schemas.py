"""Test data validation schemas."""

import pandas as pd
import pandera.errors as pa_errors
import pytest
from finrobot.core.schemas import MarketDataSchema, FinancialReportSchema


def test_market_data_schema_valid():
    """Test valid market data."""
    valid_data = pd.DataFrame(
        {
            "symbol": ["AAPL"],
            "date": [pd.to_datetime("2025-01-01")],
            "open": [150.0],
            "high": [155.0],
            "low": [149.0],
            "close": [154.0],
            "volume": [1000000],
        }
    )
    validated = MarketDataSchema.check(valid_data)
    assert not validated.empty


def test_market_data_schema_invalid():
    """Test invalid market data."""
    invalid_data = pd.DataFrame(
        {
            "symbol": ["AAPL"],
            "close": ["invalid_price"],  # Should be float
        }
    )
    with pytest.raises(pa_errors.SchemaError):
        MarketDataSchema.check(invalid_data)


def test_financial_report_schema_valid():
    """Test valid financial report."""
    valid_data = pd.DataFrame(
        {
            "company": ["AAPL"],
            "report_type": ["Annual"],
            "content": ["Report content..."],
            "timestamp": [pd.to_datetime("2025-01-01")],
        }
    )
    validated = FinancialReportSchema.check(valid_data)
    assert not validated.empty
