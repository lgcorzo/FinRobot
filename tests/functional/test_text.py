import pytest

from finrobot.functional.text import TextUtils


def test_check_text_length() -> None:
    # Within range
    res = TextUtils.check_text_length("word " * 10, min_length=0, max_length=100)
    assert "within the expected range" in res

    # Exceeds max
    res = TextUtils.check_text_length("word " * 10, min_length=0, max_length=5)
    assert "exceeds" in res

    # Less than min
    res = TextUtils.check_text_length("word " * 2, min_length=5, max_length=100)
    assert "less than" in res
