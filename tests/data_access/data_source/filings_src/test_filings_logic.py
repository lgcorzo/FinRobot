import typing as T
from unittest.mock import MagicMock, patch

import pytest

from finrobot.data_access.data_source.filings_src.sec_filings import SECExtractor, timeout
from finrobot.data_access.data_source.filings_src.secData import sec_main


def test_sec_extractor_init() -> None:
    extractor = SECExtractor(ticker="AAPL", sections=["BUSINESS"])
    assert extractor.ticker == "AAPL"
    assert extractor.sections == ["BUSINESS"]


def test_sec_extractor_get_year() -> None:
    extractor = SECExtractor(ticker="AAPL")
    extractor.filing_type = "10-K"
    assert extractor.get_year("some/url/2023.htm") == "2023"

    extractor.filing_type = "10-Q"
    assert extractor.get_year("some/url/202303.htm") == "202303"


def test_sec_extractor_get_all_text() -> None:
    extractor = SECExtractor(ticker="AAPL")
    all_narratives = {"BUSINESS": [{"text": "Hello"}, {"text": "World"}]}
    text = extractor.get_all_text("BUSINESS", all_narratives)
    assert text == "Hello World"


@patch("finrobot.data_access.data_source.filings_src.sec_filings.SECDocument")
@patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names")
@patch("finrobot.data_access.data_source.filings_src.sec_filings.convert_to_isd")
def test_pipeline_api(mock_convert: MagicMock, mock_validate: MagicMock, mock_sec_doc_cls: MagicMock) -> None:
    mock_sec_doc = MagicMock()
    mock_sec_doc_cls.from_string.return_value = mock_sec_doc
    mock_sec_doc.filing_type = "10-K"
    mock_sec_doc.get_section_narrative.return_value = ["narrative"]
    mock_convert.return_value = {"text": "converted"}

    extractor = SECExtractor(ticker="AAPL")
    res, ftype = extractor.pipeline_api("raw text", m_section=["BUSINESS"])
    assert ftype == "10-K"
    assert "BUSINESS" in res


def test_timeout() -> None:
    with timeout(seconds=1):
        pass  # Should not raise


@patch("finrobot.data_access.data_source.filings_src.secData.get_cik_by_ticker")
@patch("requests.get")
@patch("finrobot.data_access.data_source.filings_src.secData.get_filing")
@patch("finrobot.data_access.data_source.filings_src.secData.SECExtractor")
@patch("finrobot.data_access.data_source.filings_src.secData.Document")
def test_sec_main(
    mock_doc: MagicMock,
    mock_extractor_cls: MagicMock,
    mock_get_filing: MagicMock,
    mock_get_req: MagicMock,
    mock_get_cik: MagicMock,
) -> None:
    mock_get_cik.return_value = "0000320193"
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
    mock_get_req.return_value = mock_response
    mock_get_filing.return_value = "raw filing text"

    mock_extractor = MagicMock()
    mock_extractor_cls.return_value = mock_extractor
    mock_extractor.get_section_texts_from_text.return_value = {"BUSINESS": "Section text"}

    # Need to mock the pools or avoid them
    with patch("concurrent.futures.ThreadPoolExecutor") as mock_thread_pool:
        with patch("concurrent.futures.ProcessPoolExecutor") as mock_process_pool:
            mock_thread_instance = mock_thread_pool.return_value.__enter__.return_value
            mock_thread_instance.map.return_value = ["raw filing text"]

            mock_process_instance = mock_process_pool.return_value.__enter__.return_value
            mock_process_instance.map.return_value = [{"BUSINESS": "Section text"}]

            docs, form_names = sec_main("AAPL", "2023")
            assert len(docs) == 1
            assert "10-K" in form_names
