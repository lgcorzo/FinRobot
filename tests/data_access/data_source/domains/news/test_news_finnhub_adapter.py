import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finrobot.data_access.data_source.domains.news.finnhub_adapter import FinnHubNewsAdapter


@pytest.fixture
def finnhub_api_key() -> None:
    with patch.dict(os.environ, {"FINNHUB_API_KEY": "test_key"}):
        yield "test_key"


class TestFinnHubNewsAdapter:
    @patch("finrobot.data_access.data_source.domains.news.finnhub_adapter.finnhub.Client")
    def test_get_company_news(self, mock_client_cls, finnhub_api_key) -> None:
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client
        mock_client.company_news.return_value = [
            {"datetime": 1672531200, "headline": "Headline 1", "summary": "Summary 1"},
        ]

        df = FinnHubNewsAdapter.get_company_news("AAPL", "2023-01-01", "2023-01-02")
        assert len(df) == 1
        assert "Headline 1" in df["headline"].values
