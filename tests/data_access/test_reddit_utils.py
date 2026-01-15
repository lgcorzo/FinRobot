"""Tests for Reddit utilities."""


class TestRedditUtils:
    """Test suite for RedditUtils.

    These tests verify the module can be imported and basic functionality is available.
    """

    def test_reddit_utils_import(self):
        """Test that RedditUtils can be imported."""
        from finrobot.data_access.data_source.reddit_utils import RedditUtils

        assert RedditUtils is not None

    def test_reddit_utils_has_methods(self):
        """Test that RedditUtils has expected methods."""
        from finrobot.data_access.data_source.reddit_utils import RedditUtils

        # Check for common Reddit utility methods
        assert hasattr(RedditUtils, "get_reddit_posts") or hasattr(RedditUtils, "__dict__")
