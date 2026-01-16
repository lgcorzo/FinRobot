import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finrobot.data_access.data_source.finnhub_utils import FinnHubUtils


@pytest.fixture
def finnhub_api_key():
    with patch.dict(os.environ, {"FINNHUB_API_KEY": "test_key"}):
        yield "test_key"


class TestFinnHubUtils:
    @patch("finrobot.data_access.data_source.finnhub_utils.finnhub.Client")
    def test_get_company_profile(self, mock_client_cls, finnhub_api_key):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.company_profile2.return_value = {
            "name": "Apple Inc.",
            "finnhubIndustry": "Technology",
            "ipo": "1980-12-12",
            "marketCapitalization": 2000000.0,
            "currency": "USD",
            "shareOutstanding": 16000.0,
            "country": "US",
            "ticker": "AAPL",
            "exchange": "NASDAQ",
        }

        result = FinnHubUtils.get_company_profile("AAPL")
        assert "Apple Inc." in result
        assert "Technology" in result

    @patch("finrobot.data_access.data_source.finnhub_utils.finnhub.Client")
    def test_get_company_news(self, mock_client_cls, finnhub_api_key):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.company_news.return_value = [
            {"datetime": 1672531200, "headline": "Headline 1", "summary": "Summary 1"},
            {"datetime": 1672617600, "headline": "Headline 2", "summary": "Summary 2"},
        ]

        df = FinnHubUtils.get_company_news("AAPL", "2023-01-01", "2023-01-02")
        assert len(df) == 2
        assert "Headline 1" in df["headline"].values

    @patch("finrobot.data_access.data_source.finnhub_utils.finnhub.Client")
    def test_get_basic_financials_history(self, mock_client_cls, finnhub_api_key):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.company_basic_financials.return_value = {
            "series": {"annual": {"eps": [{"period": "2023-12-31", "v": 6.0}, {"period": "2022-12-31", "v": 5.5}]}}
        }

        df = FinnHubUtils.get_basic_financials_history("AAPL", "annual", "2022-01-01", "2023-12-31")
        assert "eps" in df.columns
        assert len(df) == 2

    @patch("finrobot.data_access.data_source.finnhub_utils.finnhub.Client")
    def test_get_basic_financials(self, mock_client_cls, finnhub_api_key):
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.company_basic_financials.return_value = {
            "series": {"quarterly": {"eps": [{"period": "2023-09-30", "v": 1.5}]}},
            "metric": {"peTTM": 25.0},
        }

        result_json = FinnHubUtils.get_basic_financials("AAPL")
        import json

        result = json.loads(result_json)
        assert result["peTTM"] == 25.0
        assert result["eps"] == 1.5
