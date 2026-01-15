"""Tests for Finnhub utilities."""


class TestFinnHubUtils:
    """Test suite for FinnHubUtils.

    These tests verify the module can be imported and basic functionality is available.
    """

    def test_finnhub_utils_import(self):
        """Test that FinnHubUtils can be imported."""
        from finrobot.data_access.data_source.finnhub_utils import FinnHubUtils

        assert FinnHubUtils is not None

    def test_finnhub_utils_has_methods(self):
        """Test that FinnHubUtils has expected methods."""
        from finrobot.data_access.data_source.finnhub_utils import FinnHubUtils

        assert hasattr(FinnHubUtils, "get_company_news")
        assert hasattr(FinnHubUtils, "get_basic_financials")
