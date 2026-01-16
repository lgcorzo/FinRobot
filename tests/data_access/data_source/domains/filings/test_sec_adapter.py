import os
from unittest.mock import MagicMock, patch

import pytest

from finrobot.data_access.data_source.domains.filings.sec_adapter import SECAdapter


@pytest.fixture
def sec_api_key() -> None:
    with patch.dict(os.environ, {"SEC_API_KEY": "test_key"}):
        yield "test_key"


class TestSECAdapter:
    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.QueryApi")
    def test_get_10k_metadata(self, mock_query_cls, sec_api_key) -> None:
        mock_query = MagicMock()
        mock_query_cls.return_value = mock_query
        mock_query.get_filings.return_value = {"filings": [{"ticker": "AAPL", "filedAt": "2023-01-01"}]}

        result = SECAdapter.get_10k_metadata("AAPL", "2023-01-01", "2023-01-31")
        assert result["ticker"] == "AAPL"

    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.RenderApi")
    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.SECAdapter.get_10k_metadata")
    def test_download_10k_filing(self, mock_get_metadata, mock_render_cls, sec_api_key, tmp_path) -> None:
        mock_render = MagicMock()
        mock_render_cls.return_value = mock_render
        mock_render.get_filing.return_value = "<html>Content</html>"

        mock_get_metadata.return_value = {
            "ticker": "AAPL",
            "linkToFilingDetails": "http://link",
            "filedAt": "2023-01-01",
            "formType": "10-K",
        }

        save_folder = str(tmp_path / "10k")
        result = SECAdapter.download_10k_filing("AAPL", "2023-01-01", "2023-01-31", save_folder)
        assert "download succeeded" in result
        assert os.path.isdir(save_folder)

    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.SECAdapter.get_10k_metadata")
    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.requests.get")
    def test_download_10k_pdf(self, mock_get, mock_get_metadata, sec_api_key) -> None:
        mock_get_metadata.return_value = {
            "ticker": "AAPL",
            "formType": "10-K",
            "filedAt": "2023-01-01T00:00:00",
            "linkToFilingDetails": "http://sec.gov/10k.htm",
        }

        # Mock streaming response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.iter_content.return_value = [b"chunk1", b"chunk2"]
        mock_get.return_value = mock_response

        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            result = SECAdapter.download_10k_pdf("AAPL", "2023-01-01", "2023-12-31", "save_folder")
            assert "download succeeded" in result
            mock_open.assert_called()
            handle = mock_open.return_value.__enter__.return_value
            handle.write.assert_any_call(b"chunk1")

    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.FMPUtils.get_sec_report")
    @patch("finrobot.data_access.data_source.domains.filings.sec_adapter.ExtractorApi")
    def test_get_10k_section(self, mock_extractor_cls, mock_get_report, sec_api_key) -> None:
        mock_extractor = MagicMock()
        mock_extractor_cls.return_value = mock_extractor
        mock_extractor.get_section.return_value = "Section Content"

        mock_get_report.return_value = "Link: http://report"

        result = SECAdapter.get_10k_section("AAPL", "2023", "1A")
        assert result == "Section Content"
