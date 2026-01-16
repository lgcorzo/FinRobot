from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.data_access.data_source.domains.market_data.yfinance_adapter import YFinanceAdapter


class TestYFinanceAdapter:
    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_stock_data(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.history.return_value = pd.DataFrame({"Close": [150.0]})
        mock_ticker.ticker = "AAPL"

        result = YFinanceAdapter.get_stock_data("AAPL", "2023-01-01", "2023-01-02")
        assert not result.empty
        assert result.iloc[0]["Close"] == 150.0

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_stock_info(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.info = {"shortName": "Apple"}

        result = YFinanceAdapter.get_stock_info("AAPL")
        assert result["shortName"] == "Apple"

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_income_stmt(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.financials = pd.DataFrame({"2023": [1000000]})

        result = YFinanceAdapter.get_income_stmt("AAPL")
        assert not result.empty

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_analyst_recommendations(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        df = pd.DataFrame({"period": ["0m"], "Strong Buy": [10]})
        mock_ticker.recommendations = df

        rec, count = YFinanceAdapter.get_analyst_recommendations("AAPL")
        assert rec == "Strong Buy"
        assert count == 10

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_analyst_recommendations_empty(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.recommendations = pd.DataFrame()

        rec, count = YFinanceAdapter.get_analyst_recommendations("AAPL")
        assert rec is None
        assert count == 0

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_company_info(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.info = {
            "shortName": "Apple",
            "industry": "Tech",
            "sector": "Consumer Electronics",
            "country": "USA",
            "website": "http",
        }

        # Test without save_path
        res = YFinanceAdapter.get_company_info("AAPL")
        assert res.iloc[0]["Company Name"] == "Apple"

        # Test with save_path
        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            res = YFinanceAdapter.get_company_info("AAPL", save_path="path.csv")
            mock_to_csv.assert_called_with("path.csv")

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_stock_dividends(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.dividends = pd.Series([0.23], index=pd.to_datetime(["2023-01-01"]))

        # Test without save_path
        res = YFinanceAdapter.get_stock_dividends("AAPL")
        assert not res.empty

        # Test with save_path
        with patch("pandas.Series.to_csv") as mock_to_csv:
            YFinanceAdapter.get_stock_dividends("AAPL", save_path="path.csv")
            mock_to_csv.assert_called_with("path.csv")

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_balance_sheet(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.balance_sheet = pd.DataFrame({"2023": [1]})
        res = YFinanceAdapter.get_balance_sheet("AAPL")
        assert not res.empty

    @patch("finrobot.data_access.data_source.domains.market_data.yfinance_adapter.yf.Ticker")
    def test_get_cash_flow(self, mock_ticker_cls) -> None:  # type: ignore[no-untyped-def]
        mock_ticker = MagicMock()
        mock_ticker_cls.return_value = mock_ticker
        mock_ticker.cashflow = pd.DataFrame({"2023": [1]})
        res = YFinanceAdapter.get_cash_flow("AAPL")
        assert not res.empty
