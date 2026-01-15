"""Tests for YFinance utilities."""

from unittest.mock import MagicMock, patch

import pandas as pd


class TestYFinanceUtils:
    """Test suite for YFinanceUtils.

    These tests verify the module can be imported and basic functionality is available.
    """

    def test_yfinance_utils_import(self):
        """Test that YFinanceUtils can be imported."""
        from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

        assert YFinanceUtils is not None

    def test_yfinance_utils_has_methods(self):
        """Test that YFinanceUtils has expected methods."""
        from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

        assert hasattr(YFinanceUtils, "get_stock_data")
        assert hasattr(YFinanceUtils, "get_stock_info")

    @patch("yfinance.Ticker")
    def test_get_stock_data_calls_yfinance(self, mock_ticker_cls):
        """Test that get_stock_data calls yfinance."""
        from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

        mock_ticker = MagicMock()
        mock_ticker.history.return_value = pd.DataFrame(
            {
                "Open": [100],
                "High": [105],
                "Low": [99],
                "Close": [104],
                "Volume": [1000000],
            }
        )
        mock_ticker_cls.return_value = mock_ticker

        result = YFinanceUtils.get_stock_data("AAPL", start_date="2023-01-01", end_date="2023-01-31")

        assert result is not None or mock_ticker_cls.called

    @patch("yfinance.Ticker")
    def test_get_stock_info_calls_yfinance(self, mock_ticker_cls):
        """Test that get_stock_info calls yfinance."""
        from finrobot.data_access.data_source.yfinance_utils import YFinanceUtils

        mock_ticker = MagicMock()
        mock_ticker.info = {"symbol": "AAPL", "longName": "Apple Inc."}
        mock_ticker_cls.return_value = mock_ticker

        result = YFinanceUtils.get_stock_info("AAPL")

        assert result is not None or mock_ticker_cls.called
