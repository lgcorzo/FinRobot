import os
from typing import Any, Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.data_access.data_source.fmp_utils import FMPUtils


@pytest.fixture(autouse=True)
def setup_fmp_env() -> Generator[None, None, None]:
    with patch.dict(os.environ, {"FMP_API_KEY": "test"}):
        yield


def test_fmp_utils_bvps_empty() -> None:
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = []
        res = FMPUtils.get_historical_bvps("AAPL", "2023-01-01")
        assert res == "No data available"


def test_fmp_utils_bvps_no_match() -> None:
    with patch("requests.get") as mock_get:
        mock_get.return_value.json.return_value = [{"date": "1990-01-01", "bookValuePerShare": 10}]
        # It should still find the closest one unless min_date_diff is not updated
        # Line 144: if closest_data:
        res = FMPUtils.get_historical_bvps("AAPL", "2023-01-01")
        assert res == 10


def test_fmp_utils_financial_metrics_logic() -> None:
    with patch("requests.get") as mock_get:
        # Mocking 3 calls per year: income, ratios, key_metrics
        mock_income = [
            {
                "date": "2023-01-01",
                "revenue": 100000000,
                "grossProfit": 50000000,
                "ebitda": 20000000,
                "ebitdaratio": 0.2,
                "netIncome": 10000000,
            }
        ]
        # For year_offset - 1, we need it to have values too
        mock_income_prev = [{"revenue": 80000000}]

        # We need to return them in sequence
        def side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            m = MagicMock()
            if "income-statement" in args[0]:
                m.json.return_value = mock_income + mock_income_prev
            elif "ratios" in args[0]:
                m.json.return_value = [{"priceEarningsRatio": 15}]
            elif "key-metrics" in args[0]:
                m.json.return_value = [
                    {
                        "enterpriseValue": 200000000,
                        "evToOperatingCashFlow": 10,
                        "roic": 0.15,
                        "pbRatio": 2,
                        "enterpriseValueOverEBITDA": 10,
                    }
                ]
            return m

        mock_get.side_effect = side_effect
        df = FMPUtils.get_financial_metrics("AAPL", years=1)
        assert "2023" in df.columns
        assert df["2023"]["Revenue"] == 100


def test_fmp_utils_competitors() -> None:
    with patch("requests.get") as mock_get:

        def side_effect(*args: Any, **kwargs: Any) -> MagicMock:
            m = MagicMock()
            m.json.return_value = [
                {
                    "date": "2023-01-01",
                    "revenue": 100000000,
                    "grossProfit": 50000000,
                    "ebitda": 20000000,
                    "ebitdaratio": 0.2,
                    "netIncome": 10000000,
                    "enterpriseValue": 200000000,
                    "evToOperatingCashFlow": 10,
                    "roic": 0.15,
                    "pbRatio": 2,
                    "enterpriseValueOverEBITDA": 10,
                }
            ]
            return m

        mock_get.side_effect = side_effect
        res = FMPUtils.get_competitor_financial_metrics("AAPL", ["MSFT"], years=1)
        assert "AAPL" in res
        assert "MSFT" in res
        assert isinstance(res["AAPL"], pd.DataFrame)
