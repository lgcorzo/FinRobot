from unittest.mock import MagicMock, call, patch

import pytest

try:
    from tenacity import RetryError
except ImportError:

    class RetryError(Exception):  # type: ignore[no-redef]
        pass


from finrobot.data_access.data_source.earnings_calls_src.main_earningsData import (
    clean_speakers,
    get_earnings_all_docs,
    get_earnings_all_quarters_data,
)


# Mock Document to have attributes
@pytest.fixture
def mock_document() -> None:
    with patch("finrobot.data_access.data_source.earnings_calls_src.main_earningsData.Document") as mock:

        def side_effect(page_content, metadata) -> None:
            m = MagicMock()
            m.page_content = page_content
            m.metadata = metadata
            return m

        mock.side_effect = side_effect
        yield mock


@patch("finrobot.data_access.data_source.earnings_calls_src.main_earningsData.get_earnings_transcript")
def test_get_earnings_all_quarters_data(mock_get_transcript, mock_document) -> None:
    # Setup mock return from transcript
    # Content pattern: \nSpeaker Name: Speech content
    content = "Intro text.\nSpeaker 1: Hello world.\nSpeaker 2: Hi there."
    mock_get_transcript.return_value = {"content": content}

    docs, speakers = get_earnings_all_quarters_data("Q1", "AAPL", 2023)

    assert len(speakers) == 2
    assert "Speaker 1" in speakers
    assert len(docs) == 2
    # Check parsed content
    assert "Hello world." in docs[0].page_content
    # Clean speakers strips \n and :
    assert docs[0].metadata["speaker"] == "Speaker 1"
    assert docs[0].metadata["quarter"] == "Q1"


@patch("finrobot.data_access.data_source.earnings_calls_src.main_earningsData.get_earnings_all_quarters_data")
def test_get_earnings_all_docs(mock_get_quarters) -> None:
    # Mock successful returns for Q1, Q2
    # Mock RetryError for Q3, Q4

    def side_effect(quarter, ticker, year) -> None:
        if quarter in ["Q1", "Q2"]:
            # Returns docs, speakers_list
            doc = MagicMock()
            doc.page_content = f"Content {quarter}"
            return [doc], [f"Speaker {quarter}"]
        else:
            raise RetryError(last_attempt=MagicMock())

    mock_get_quarters.side_effect = side_effect

    (earnings_docs, quarters, s1, s2, s3, s4) = get_earnings_all_docs("AAPL", 2023)

    assert len(earnings_docs) == 2
    assert quarters == ["Q1", "Q2"]
    assert s1 == ["Speaker Q1"]
    assert s2 == ["Speaker Q2"]
    assert s3 == []
    assert s4 == []


def test_clean_speakers() -> None:
    raw = "\nSpeaker Name:"
    cleaned = clean_speakers(raw)
    assert cleaned == "Speaker Name"
