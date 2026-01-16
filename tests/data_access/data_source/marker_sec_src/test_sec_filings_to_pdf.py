import json
import os
from unittest.mock import MagicMock, call, patch

import pytest

from finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf import (
    _convert_html_to_pdfs,
    get_cik_by_ticker,
    sec_save_pdfs,
)


@pytest.fixture
def mock_requests():
    with patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.requests.get") as mock:
        yield mock


@patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.requests.get")
def test_get_cik_by_ticker(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html>... CIK=0000320193 ...</html>"
    mock_get.return_value = mock_response

    cik = get_cik_by_ticker("AAPL")
    assert cik == "0000320193"


@patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.pdfkit.from_url")
@patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.get_cik_by_ticker")
@patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.requests.get")
def test_sec_save_pdfs(mock_get, mock_get_cik, mock_pdfkit, tmp_path):
    # Mock CIK
    mock_get_cik.return_value = "0000320193"

    # Mock SEC JSON
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "filings": {
            "recent": {
                "accessionNumber": ["0001-11-111111"],
                "form": ["10-K"],
                "filingDate": ["2023-01-01"],
                "reportDate": ["2023-01-01"],
            }
        }
    }
    mock_get.return_value = mock_response

    # Redirect BASE_DIR to tmp_path using patch on module attribute?
    # Or just rely on logic using os.path.join.
    # The module uses a global BASE_DIR. Let's patch it.

    with patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.BASE_DIR", str(tmp_path)):
        html_urls, metadata, meta_path, ticker_path = sec_save_pdfs("AAPL", "2023", include_amends=True)

    assert len(html_urls) == 1
    assert "10-K" in html_urls[0][1]
    assert mock_pdfkit.called
    assert os.path.exists(meta_path)


def test_convert_html_to_pdfs():
    with patch("finrobot.data_access.data_source.marker_sec_src.sec_filings_to_pdf.pdfkit.from_url") as mock_pdfkit:
        html_urls = [["http://site/file.htm", "10-K"]]
        meta = _convert_html_to_pdfs(html_urls, "base_path")

        assert len(meta) == 1
        key = list(meta.keys())[0]
        # Key contains .pdf filename
        assert key.endswith("-10-K.pdf")
        mock_pdfkit.assert_called()
