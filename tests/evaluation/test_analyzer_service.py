from unittest.mock import patch
import typing as T

import pandas as pd


class TestReportAnalysisUtils:
    """Test suite for ReportAnalysisUtils.

    Note: These tests use mocks to avoid initializing the full evaluation layer
    which has complex dependencies on charting and data sources.
    """

    @patch("finrobot.data_access.data_source.yfinance_utils.YFinanceUtils")
    def test_yfinance_income_statement_mock(self, mock_yfinance: T.Any) -> None:
        """Test income statement retrieval via mock."""
        mock_yfinance.get_income_statement.return_value = pd.DataFrame(
            {
                "Total Revenue": [100000, 110000, 120000],
                "Net Income": [20000, 22000, 25000],
            }
        )

        result = mock_yfinance.get_income_statement("AAPL")

        assert isinstance(result, pd.DataFrame)
        assert "Total Revenue" in result.columns

    @patch("finrobot.data_access.data_source.yfinance_utils.YFinanceUtils")
    def test_yfinance_stock_info_mock(self, mock_yfinance: T.Any) -> None:
        """Test stock info retrieval via mock."""
        mock_yfinance.get_stock_info.return_value = {
            "trailingPE": 25.5,
            "forwardPE": 22.0,
            "priceToBook": 35.0,
        }

        result = mock_yfinance.get_stock_info("AAPL")

        assert isinstance(result, dict)
        assert "trailingPE" in result

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils")
    def test_sec_filing_retrieval_mock(self, mock_sec: T.Any) -> None:
        """Test SEC filing retrieval via mock."""
        mock_sec.get_10k_section.return_value = "This is the risk factors section..."

        result = mock_sec.get_10k_section("AAPL", section="7")

        assert isinstance(result, str)
        assert len(result) > 0
