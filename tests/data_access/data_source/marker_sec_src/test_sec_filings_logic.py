import json
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf import (
    _convert_html_to_pdfs,
    _search_url,
    get_cik_by_ticker,
    sec_save_pdfs,
)


def test_search_url():
    assert "CIK=123" in _search_url("123")


def test_get_cik_by_ticker():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "CIK=0000320193"
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        cik = get_cik_by_ticker("AAPL")
        assert cik == "0000320193"


def test_sec_save_pdfs(tmp_path):
    with patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.get_cik_by_ticker") as mock_get_cik:
        with patch("requests.get") as mock_get:
            with patch(
                "finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf._convert_html_to_pdfs"
            ) as mock_convert:
                mock_get_cik.return_value = "0000320193"

                # Mock SEC API response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "filings": {
                        "recent": {
                            "accessionNumber": ["0000320193-23-000106"],
                            "form": ["10-K"],
                            "filingDate": ["2023-11-03"],
                            "reportDate": ["2023-09-30"],
                        }
                    }
                }
                mock_get.return_value = mock_response
                mock_convert.return_value = {"file.pdf": {"languages": ["English"]}}

                # Update BASE_DIR for test
                with patch(
                    "finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.BASE_DIR", str(tmp_path)
                ):
                    res = sec_save_pdfs("AAPL", "2023")
                    assert len(res[0]) == 1  # html_urls
                    assert "file.pdf" in res[1]  # metadata


def test_convert_html_to_pdfs(tmp_path):
    with patch("pdfkit.from_url") as mock_pdfkit:
        html_urls = [["http://example.com/file.htm", "10-K"]]
        res = _convert_html_to_pdfs(html_urls, str(tmp_path))
        assert "file-10-K.pdf" in res
        mock_pdfkit.assert_called_once()
