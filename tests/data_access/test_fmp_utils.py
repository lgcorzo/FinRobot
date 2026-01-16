import os
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest
from finrobot.data_access.data_source.fmp_utils import FMPUtils


@pytest.fixture
def fmp_api_key() -> None:
    with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
        yield "test_key"


class TestFMPUtils:
    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_target_price(self, mock_get, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"publishedDate": "2023-01-01T00:00:00", "priceTarget": 150.0},
            {"publishedDate": "2023-01-10T00:00:00", "priceTarget": 160.0},
        ]
        mock_get.return_value = mock_response

        result = FMPUtils.get_target_price("AAPL", "2023-01-05")
        assert "150.0 - 160.0" in result

    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_sec_report(self, mock_get, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"finalLink": "http://link1", "fillingDate": "2023-01-01"},
            {"finalLink": "http://link2", "fillingDate": "2022-01-01"},
        ]
        mock_get.return_value = mock_response

        result = FMPUtils.get_sec_report("AAPL", "2023")
        assert "http://link1" in result

        result_latest = FMPUtils.get_sec_report("AAPL", "latest")
        assert "http://link1" in result_latest

    @patch("finrobot.data_access.data_source.fmp_utils.get_next_weekday")
    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_historical_market_cap(self, mock_get, mock_get_next, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_get_next.return_value = MagicMock(strftime=lambda x: "2023-01-03")
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"marketCap": 2000000000000}]
        mock_get.return_value = mock_response

        result = FMPUtils.get_historical_market_cap("AAPL", "2023-01-01")
        assert result == 2000000000000

    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_historical_bvps(self, mock_get, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"date": "2023-01-01", "bookValuePerShare": 25.0},
            {"date": "2022-01-01", "bookValuePerShare": 22.0},
        ]
        mock_get.return_value = mock_response

        result = FMPUtils.get_historical_bvps("AAPL", "2023-01-05")
        assert result == 25.0

    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_financial_metrics(self, mock_get, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Need to handle multiple calls to requests.get
        mock_response.json.side_effect = [
            # Year 2023
            [
                {
                    "date": "2023-12-31",
                    "revenue": 100000000,
                    "grossProfit": 40000000,
                    "ebitda": 30000000,
                    "ebitdaratio": 0.3,
                    "netIncome": 20000000,
                }
            ],  # income
            [
                {
                    "date": "2023-12-31",
                    "enterpriseValue": 500000000,
                    "evToOperatingCashFlow": 10.0,
                    "roic": 0.15,
                    "enterpriseValueOverEBITDA": 15.0,
                    "pbRatio": 3.0,
                }
            ],  # metrics
            [{"date": "2023-12-31", "priceEarningsRatio": 25.0}],  # ratios
            # Year 2022 (needed for growth)
            [
                {
                    "date": "2022-12-31",
                    "revenue": 90000000,
                    "grossProfit": 35000000,
                    "ebitda": 25000000,
                    "ebitdaratio": 0.28,
                    "netIncome": 15000000,
                }
            ],
            [
                {
                    "date": "2022-12-31",
                    "enterpriseValue": 400000000,
                    "evToOperatingCashFlow": 8.0,
                    "roic": 0.12,
                    "enterpriseValueOverEBITDA": 12.0,
                    "pbRatio": 2.5,
                }
            ],
            [{"date": "2022-12-31", "priceEarningsRatio": 20.0}],
        ]
        mock_get.return_value = mock_response

        df = FMPUtils.get_financial_metrics("AAPL", years=1)
        assert isinstance(df, pd.DataFrame)
        assert "2023" in df.columns
        assert df.loc["Revenue", "2023"] == 100

    @patch("finrobot.data_access.data_source.fmp_utils.requests.get")
    def test_get_competitor_financial_metrics(self, mock_get, fmp_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mock responses for AAPL (income, ratios, key-metrics) and MSFT (income, ratios, key-metrics)
        # 2 companies * 3 calls each = 6 calls
        # Simply return valid data for all calls
        valid_response_income = [
            {
                "date": "2023-12-31",
                "revenue": 100000000,
                "grossProfit": 40000000,
                "ebitda": 30000000,
                "ebitdaratio": 0.3,
                "netIncome": 20000000,
            }
        ]
        valid_response_ratios = [{"date": "2023-12-31", "priceEarningsRatio": 25.0}]
        valid_response_metrics = [
            {
                "date": "2023-12-31",
                "enterpriseValue": 500000000,
                "evToOperatingCashFlow": 10.0,
                "roic": 0.15,
                "enterpriseValueOverEBITDA": 15.0,
                "pbRatio": 3.0,
            }
        ]

        mock_get.return_value.json.side_effect = [
            valid_response_income,
            valid_response_ratios,
            valid_response_metrics,  # AAPL
            valid_response_income,
            valid_response_ratios,
            valid_response_metrics,  # MSFT
        ]

        result = FMPUtils.get_competitor_financial_metrics("AAPL", ["MSFT"], years=1)
        assert "AAPL" in result
        assert "MSFT" in result
        assert isinstance(result["AAPL"], pd.DataFrame)
        # get_competitor_financial_metrics returns DF with Index=year_offset (0,1..) and Columns=Metrics
        assert result["AAPL"].loc[0, "Revenue"] == 100

    def test_init_fmp_api_no_key(self) -> None:
        # Unpatch environment for this test specifically if possible, or patch with None
        with patch.dict(os.environ, {}, clear=True):
            # FMPUtils methods are decorated. calling one should trigger the check.
            # but they are class methods, so we can call them directly.
            # However, the decorator checks env var.
            # We need to ensure capsys/print check if we want to be strict, or just return None
            pass  # The decorator logic returns None if key is missing.

            # Re-patching get_target_price to avoid actual network call if decorator fails (it shouldn't)
            with patch("finrobot.data_access.data_source.fmp_utils.requests.get"):
                res = FMPUtils.get_target_price("AAPL", "2023-01-01")
                assert res is None
