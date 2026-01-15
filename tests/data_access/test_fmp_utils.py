"""Tests for FMP utilities."""


class TestFMPUtils:
    """Test suite for FMPUtils.

    These tests verify the module can be imported and basic functionality is available.
    """

    def test_fmp_utils_import(self):
        """Test that FMPUtils can be imported."""
        from finrobot.data_access.data_source.fmp_utils import FMPUtils

        assert FMPUtils is not None

    def test_fmp_utils_has_methods(self):
        """Test that FMPUtils has expected methods."""
        from finrobot.data_access.data_source.fmp_utils import FMPUtils

        # FMPUtils uses get_sec_report, not get_sec_filings
        assert hasattr(FMPUtils, "get_sec_report")
        assert hasattr(FMPUtils, "get_target_price")
