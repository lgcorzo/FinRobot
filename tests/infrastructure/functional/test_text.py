"""Tests for functional.text."""

from finrobot.functional.text import TextUtils


def test_check_text_length():
    """Test text length utility."""
    text = "one two three"
    # Length is 3 words

    assert "within the expected range" in TextUtils.check_text_length(text, min_length=1, max_length=5)
    assert "exceeds" in TextUtils.check_text_length(text, max_length=1)
    assert "less than" in TextUtils.check_text_length(text, min_length=10)
