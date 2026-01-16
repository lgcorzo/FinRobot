from unittest.mock import MagicMock, patch

import pytest

from finrobot.data_access.data_source.earnings_calls_src.main_earningsData import get_earnings_all_docs


def test_get_earnings_all_docs() -> None:
    mock_resp = {"content": "\nSpeaker 1: Hello\nSpeaker 2: Hi", "year": 2023, "date": "2023-01-01 00:00:00"}
    with patch(
        "finrobot.data_access.data_source.earnings_calls_src.main_earningsData.get_earnings_transcript",
        return_value=mock_resp,
    ):
        docs, quarters, s1, s2, s3, s4 = get_earnings_all_docs("AAPL", 2023)
        assert len(docs) > 0
        assert "Q1" in quarters
        assert s1 is not None
