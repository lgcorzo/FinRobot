from unittest.mock import MagicMock, patch
import pytest
from finrobot.data_access.data_source.filings_src.sec_filings import SECExtractor
from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sections import ALL_SECTIONS, SECTIONS_10Q


def test_sec_extractor_10q_pipeline():
    extractor = SECExtractor(ticker="AAPL")

    with patch("finrobot.data_access.data_source.filings_src.sec_filings.SECDocument") as mock_sec_document, patch(
        "finrobot.data_access.data_source.filings_src.sec_filings.convert_to_isd"
    ) as mock_convert, patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names"):
        mock_doc_instance = MagicMock()
        mock_doc_instance.filing_type = "10-Q"
        mock_doc_instance.get_section_narrative.return_value = []
        mock_sec_document.from_string.return_value = mock_doc_instance
        mock_convert.return_value = []

        # Test line 174 (10-Q branch in pipeline_api)
        result, f_type = extractor.pipeline_api("Text", m_section=[ALL_SECTIONS])

        assert f_type == "10-Q"
        # Verify 10-Q sections are in result
        for sec in SECTIONS_10Q:
            assert sec.name in result


def test_sec_extractor_year_logic_extended():
    extractor = SECExtractor(ticker="AAPL")
    # Test 10-K year regex (line 100)
    extractor.filing_type = "10-K"
    assert extractor.get_year(".../2023...") == "2023"

    # Test 10-Q year regex (line 102)
    extractor.filing_type = "10-Q"
    assert extractor.get_year(".../202301...") == "202301"


def test_sec_extractor_session_fallback_coverage():
    extractor = SECExtractor(ticker="AAPL")
    # Ensuring we cover lines 211-213 if company/email are None
    with patch.dict("os.environ", {"SEC_API_ORGANIZATION": "Org", "SEC_API_EMAIL": "Email"}):
        session = extractor._get_session()
        assert session.headers["User-Agent"] == "Org Email"
