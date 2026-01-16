import os
from unittest.mock import MagicMock, patch

import pytest

from finrobot.data_access.data_source.domains.filings.fmp_adapter import FMPFilingsAdapter


@pytest.fixture
def fmp_api_key() -> None:
    with patch.dict(os.environ, {"FMP_API_KEY": "test_key"}):
        yield "test_key"


class TestFMPFilingsAdapter:
    @patch("finrobot.data_access.data_source.domains.filings.fmp_adapter.requests.get")
    def test_get_sec_report_latest(self, mock_get, fmp_api_key) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"finalLink": "http://link1", "fillingDate": "2023-03-15"},
            {"finalLink": "http://link2", "fillingDate": "2022-03-15"},
        ]
        mock_get.return_value = mock_response

        result = FMPFilingsAdapter.get_sec_report("AAPL", "latest")
        assert "http://link1" in result
        assert "2023-03-15" in result

    @patch("finrobot.data_access.data_source.domains.filings.fmp_adapter.requests.get")
    def test_get_sec_report_year(self, mock_get, fmp_api_key) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"finalLink": "http://link1", "fillingDate": "2023-03-15"},
            {"finalLink": "http://link2", "fillingDate": "2022-03-15"},
        ]
        mock_get.return_value = mock_response

        result = FMPFilingsAdapter.get_sec_report("AAPL", "2022")
        assert "http://link2" in result
        assert "2022-03-15" in result
