import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from finrobot.data_access.data_source.sec_utils import SECUtils


@pytest.fixture
def sec_api_key() -> Generator[str, None, None]:
    with patch.dict(os.environ, {"SEC_API_KEY": "test_key"}):
        yield "test_key"


class TestSECUtils:
    @patch("finrobot.data_access.data_source.sec_utils.QueryApi")
    def test_get_10k_metadata(self, mock_query_api_cls: MagicMock, sec_api_key: str) -> None:
        mock_query_api = MagicMock()
        mock_query_api_cls.return_value = mock_query_api
        mock_query_api.get_filings.return_value = {
            "filings": [{"ticker": "AAPL", "filedAt": "2023-01-01T00:00:00", "linkToFilingDetails": "http://link"}]
        }

        result = SECUtils.get_10k_metadata("AAPL", "2023-01-01", "2023-12-31")
        assert result is not None
        assert result["ticker"] == "AAPL"

    @patch("finrobot.data_access.data_source.sec_utils.RenderApi")
    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    @patch("os.path.isdir")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    def test_download_10k_filing(
        self,
        mock_open: MagicMock,
        mock_makedirs: MagicMock,
        mock_isdir: MagicMock,
        mock_get_meta: MagicMock,
        mock_render_api_cls: MagicMock,
        sec_api_key: str,
    ) -> None:
        mock_render_api = MagicMock()
        mock_render_api_cls.return_value = mock_render_api
        mock_render_api.get_filing.return_value = "<html>content</html>"

        mock_get_meta.return_value = {
            "ticker": "AAPL",
            "filedAt": "2023-01-01T00:00:00",
            "linkToFilingDetails": "http://link/file.htm",
            "formType": "10-K",
        }
        mock_isdir.return_value = False

        result = SECUtils.download_10k_filing("AAPL", "2023-01-01", "2023-12-31", "save_folder")
        assert "download succeeded" in result
        mock_open.assert_called()

    @patch("finrobot.data_access.data_source.sec_utils.ExtractorApi")
    @patch("finrobot.data_access.data_source.sec_utils.FMPUtils.get_sec_report")
    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("builtins.open", new_callable=MagicMock)
    def test_get_10k_section(
        self,
        mock_open: MagicMock,
        mock_makedirs: MagicMock,
        mock_exists: MagicMock,
        mock_get_fmp: MagicMock,
        mock_extractor_api_cls: MagicMock,
        sec_api_key: str,
    ) -> None:
        mock_extractor_api = MagicMock()
        mock_extractor_api_cls.return_value = mock_extractor_api
        mock_extractor_api.get_section.return_value = "section text"

        mock_get_fmp.return_value = "Link: http://link"
        mock_exists.return_value = False

        # Mock file handle for writing cache
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = SECUtils.get_10k_section("AAPL", "2023", "1A")
        assert result == "section text"
        mock_extractor_api.get_section.assert_called_with("http://link", "1A", "text")

    @patch("finrobot.data_access.data_source.sec_utils.os.environ.get")
    def test_init_sec_api_missing_key(self, mock_get: MagicMock, sec_api_key: str) -> None:
        # Patch environ.get to return None for SEC_API_KEY
        # But sec_api_key fixture sets it in os.environ dict.
        # We need to ensure 'if os.environ.get("SEC_API_KEY") is None' returns True.
        mock_get.return_value = None

        # We need to call a method that triggers init_sec_api
        # But init_sec_api uses `if os.environ.get(...)`.
        # And it uses `global extractor_api`.

        # Test logic:
        # SECUtils.get_10k_metadata is decorated.
        # Calling it triggers wrapper. wrapper calls os.environ.get.
        # If None, prints and returns None.

        # Need to capture stdout?
        with patch.dict(os.environ, {}, clear=True):
            res = SECUtils.get_10k_metadata("AAPL", "2023-01-01", "2023-12-31")
            assert res is None

    @patch("finrobot.data_access.data_source.sec_utils.QueryApi")
    def test_get_10k_metadata_no_filings(self, mock_query_api_cls: MagicMock, sec_api_key: str) -> None:
        mock_query_api = MagicMock()
        mock_query_api_cls.return_value = mock_query_api
        mock_query_api.get_filings.return_value = {"filings": []}

        result = SECUtils.get_10k_metadata("AAPL", "2023-01-01", "2023-12-31")
        assert result is None

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    def test_download_10k_filing_no_metadata(self, mock_get_meta: MagicMock, sec_api_key: str) -> None:
        mock_get_meta.return_value = None
        res = SECUtils.download_10k_filing("AAPL", "2023-01-01", "2023-12-31", "save")
        assert "No 2023 10-K filing found" in res

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    def test_download_10k_filing_exception(self, mock_get_meta: MagicMock, sec_api_key: str) -> None:
        mock_get_meta.return_value = {
            "ticker": "AAPL",
            "filedAt": "2023-01-01",
            "linkToFilingDetails": "url",
            "formType": "10-K",
        }

        with patch("finrobot.data_access.data_source.sec_utils.render_api") as mock_render_api:
            # If render_api is None (not initialized globally in test context if mock failed?),
            # But init_sec_api sets it.
            # We assume it is set.
            # Actually, wrapper sets global `render_api`.
            # If we mock `finrobot...render_api`, it mocks the module level variable.
            mock_render_api.get_filing.side_effect = Exception("Fail")
            res = SECUtils.download_10k_filing("AAPL", "2023-01-01", "2023-12-31", "save")
            assert "downloaded failed" in res

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    def test_download_10k_pdf_no_metadata(self, mock_get_meta: MagicMock, sec_api_key: str) -> None:
        mock_get_meta.return_value = None
        res = SECUtils.download_10k_pdf("AAPL", "2023-01-01", "2023-12-31", "save")
        assert "No 2023 10-K filing found" in res

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    @patch("requests.get")
    def test_download_10k_pdf_success(self, mock_get: MagicMock, mock_get_meta: MagicMock, sec_api_key: str) -> None:
        mock_get_meta.return_value = {
            "ticker": "AAPL",
            "filedAt": "2023-01-01",
            "linkToFilingDetails": "http://url",
            "formType": "10-K",
        }
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b"pdf data"]
        mock_get.return_value = mock_response

        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            with patch("os.makedirs"):
                res = SECUtils.download_10k_pdf("AAPL", "2023-01-01", "2023-12-31", "save")
                assert "download succeeded" in res

    @patch("finrobot.data_access.data_source.sec_utils.SECUtils.get_10k_metadata")
    def test_download_10k_pdf_exception(self, mock_get_meta: MagicMock, sec_api_key: str) -> None:
        mock_get_meta.return_value = {
            "ticker": "AAPL",
            "filedAt": "2023-01-01",
            "linkToFilingDetails": "url",
            "formType": "10-K",
        }

        with patch("requests.get", side_effect=Exception("Net fail")):
            res = SECUtils.download_10k_pdf("AAPL", "2023-01-01", "2023-12-31", "save")
            assert "downloaded failed" in res

    def test_get_10k_section_invalid_section(self, sec_api_key: str) -> None:
        with pytest.raises(ValueError):
            SECUtils.get_10k_section("AAPL", "2023", "Invalid")

    @patch("finrobot.data_access.data_source.sec_utils.FMPUtils.get_sec_report")
    def test_get_10k_section_fmp_failure(self, mock_fmp: MagicMock, sec_api_key: str) -> None:
        mock_fmp.return_value = "Error from FMP"
        res = SECUtils.get_10k_section("AAPL", "2023", "1A")
        assert res == "Error from FMP"

    @patch("os.path.exists", return_value=True)
    @patch("builtins.open", new_callable=MagicMock)
    def test_get_10k_section_cache_hit(self, mock_open: MagicMock, mock_exists: MagicMock, sec_api_key: str) -> None:
        # report_address passed to avoid FMP call
        mock_file = MagicMock()
        mock_file.read.return_value = "cached text"
        mock_open.return_value.__enter__.return_value = mock_file

        res = SECUtils.get_10k_section("AAPL", "2023", 1, report_address="http://url")  # section as int
        assert res == "cached text"

    @patch("finrobot.data_access.data_source.sec_utils.ExtractorApi")
    @patch("os.path.exists", return_value=False)
    @patch("builtins.open", new_callable=MagicMock)
    @patch("os.makedirs")
    def test_get_10k_section_with_save_path(
        self,
        mock_mkdirs: MagicMock,
        mock_open: MagicMock,
        mock_exists: MagicMock,
        mock_extractor_cls: MagicMock,
        sec_api_key: str,
    ) -> None:
        mock_extractor = MagicMock()
        mock_extractor_cls.return_value = mock_extractor
        mock_extractor.get_section.return_value = "text"

        res = SECUtils.get_10k_section("AAPL", "2023", "1A", report_address="url", save_path="custom/path.txt")
        assert res == "text"
        # Should call open 2 times (cache + save_path)
        assert mock_open.call_count >= 2
