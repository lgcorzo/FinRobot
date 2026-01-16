import pytest
import requests
import typing as T
from unittest.mock import MagicMock, patch
from finrobot.data_access.data_source.filings_src.sec_filings import (
    REPORT_TYPES,
    SECTIONS_10K,
    SECTIONS_10Q,
    SECTIONS_S1,
    SECDocument,
    SECExtractor,
    get_regex_enum,
    timeout,
)


# Mock dependencies that might not be installed or heavy
@pytest.fixture
def mock_sec_document() -> T.Generator[MagicMock, None, None]:
    with patch("finrobot.data_access.data_source.filings_src.sec_filings.SECDocument") as mock:
        yield mock


@pytest.fixture
def mock_convert_to_isd() -> T.Generator[MagicMock, None, None]:
    with patch("finrobot.data_access.data_source.filings_src.sec_filings.convert_to_isd") as mock:
        yield mock


class TestTimeout:
    def test_timeout_context_manager(self) -> None:
        """Test that timeout context manager works correctly."""
        # Simple test to ensure it doesn't break basic flows
        # Simulating alarm signal is tricky in threads/some envs,
        # so we mostly check if it enters and exits without error.
        with patch("signal.signal"), patch("signal.alarm"):
            with timeout(seconds=1):
                pass


class TestSECExtractor:
    @pytest.fixture
    def extractor(self) -> SECExtractor:
        return SECExtractor(ticker="AAPL")

    def test_init(self, extractor: SECExtractor) -> None:
        assert extractor.ticker == "AAPL"
        assert extractor.sections == ["_ALL"]

    def test_get_year_10k(self, extractor: SECExtractor) -> None:
        extractor.filing_type = "10-K"
        details = "http://sec.gov/Archives/edgar/data/320193/000032019321000010/aapl-20210925.htm"
        assert extractor.get_year(details) == "2021"

    def test_get_year_10q(self, extractor: SECExtractor) -> None:
        extractor.filing_type = "10-Q"
        details = "http://sec.gov/Archives/edgar/data/320193/000032019321000065/aapl-20210626.htm"
        # 10-Q regex is 20\d{4}, so it captures YYYYMM
        assert extractor.get_year(details) == "202106"

    def test_get_year_no_match(self, extractor: SECExtractor) -> None:
        extractor.filing_type = "10-K"
        details = "invalid_url"
        assert extractor.get_year(details) is None

    def test_get_all_text(self, extractor: SECExtractor) -> None:
        all_narratives = {"Item 1": [{"text": "Part 1"}, {"other": "value"}, {"text": "Part 2"}]}
        text = extractor.get_all_text("Item 1", all_narratives)
        assert text == "Part 1 Part 2"

    def test_get_session_defaults(self, extractor: SECExtractor) -> None:
        with patch("os.environ.get") as mock_env:
            mock_env.return_value = "TestValue"
            session = extractor._get_session()
            assert isinstance(session, requests.Session)
            assert "TestValue" in session.headers["User-Agent"]

    def test_get_session_custom(self, extractor: SECExtractor) -> None:
        session = extractor._get_session(company="MyComp", email="me@test.com")
        assert "MyComp me@test.com" in session.headers["User-Agent"]

    @patch("requests.Session.get")
    def test_get_filing(self, mock_get: MagicMock, extractor: SECExtractor) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Filing Content"
        mock_get.return_value = mock_response

        content = extractor.get_filing("http://test.url", "Comp", "mail")
        assert content == "Filing Content"
        mock_get.assert_called_with("http://test.url")

    def test_pipeline_api_valid(
        self,
        extractor: SECExtractor,
        mock_sec_document: MagicMock,
        mock_convert_to_isd: MagicMock,
    ) -> None:
        # Setup mocks
        mock_doc_instance = MagicMock()
        mock_doc_instance.filing_type = "10-K"
        mock_sec_document.from_string.return_value = mock_doc_instance

        mock_section_enum = MagicMock()
        mock_doc_instance.get_section_narrative.return_value = ["Element1"]
        mock_convert_to_isd.return_value = [{"text": "Element1"}]

        # We need to ensure section_string_to_enum works or mock it
        # Since it's imported, mocking generic dictionary might be needed if values are strict
        # For now assume "Item 1" maps to something if we mock validate_section_names

        with (
            patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names"),
            patch(
                "finrobot.data_access.data_source.filings_src.sec_filings.section_string_to_enum",
                {"Item 1": "ENUM_VAL"},
            ),
        ):
            result, filing_type = extractor.pipeline_api("Raw Text", m_section=["Item 1"])

            assert filing_type == "10-K"
            assert "Item 1" in result
            assert result["Item 1"] == [{"text": "Element1"}]

    def test_pipeline_api_invalid_type(self, extractor: SECExtractor, mock_sec_document: MagicMock) -> None:
        mock_doc_instance = MagicMock()
        mock_doc_instance.filing_type = "INVALID"
        mock_sec_document.from_string.return_value = mock_doc_instance

        with patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names"):
            with pytest.raises(ValueError, match="is not supported"):
                extractor.pipeline_api("Raw Text")

    def test_pipeline_api_all_sections_10k(
        self,
        extractor: SECExtractor,
        mock_sec_document: MagicMock,
        mock_convert_to_isd: MagicMock,
    ) -> None:
        mock_doc_instance = MagicMock()
        mock_doc_instance.filing_type = "10-K"
        mock_sec_document.from_string.return_value = mock_doc_instance
        # Mock get_section_narrative to return empty list
        mock_doc_instance.get_section_narrative.return_value = []
        mock_convert_to_isd.return_value = []

        with patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names"):
            # Mock ALL_SECTIONS constant if needed, but it's imported
            # We rely on ALL_SECTIONS being in m_section
            from finrobot.data_access.data_source.filings_src.prepline_sec_filings.sections import ALL_SECTIONS

            result, f_type = extractor.pipeline_api("Text", m_section=[ALL_SECTIONS])
            assert f_type == "10-K"
            # Should have keys for all 10k sections
            # We check if SECTIONS_10K enum names are in result
            for sec in SECTIONS_10K:
                assert sec.name in result

    def test_pipeline_api_regex(
        self,
        extractor: SECExtractor,
        mock_sec_document: MagicMock,
        mock_convert_to_isd: MagicMock,
    ) -> None:
        mock_doc_instance = MagicMock()
        mock_doc_instance.filing_type = "10-K"
        mock_sec_document.from_string.return_value = mock_doc_instance
        mock_doc_instance.get_section_narrative.return_value = ["RegexMatch"]
        mock_convert_to_isd.return_value = [{"text": "RegexMatch"}]

        with patch("finrobot.data_access.data_source.filings_src.sec_filings.validate_section_names"):
            with patch(
                "finrobot.data_access.data_source.filings_src.sec_filings.timeout"
            ):  # Mock timeout to avoid signal issues
                result, f_type = extractor.pipeline_api("Text", m_section_regex=["TestPattern"])
                assert "REGEX_0" in result
