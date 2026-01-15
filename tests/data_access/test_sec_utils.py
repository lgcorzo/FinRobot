"""Tests for SEC utilities."""


class TestSECUtils:
    """Test suite for SECUtils.

    These tests verify the module can be imported and basic functionality is available.
    """

    def test_sec_utils_import(self):
        """Test that SECUtils can be imported."""
        from finrobot.data_access.data_source.sec_utils import SECUtils

        assert SECUtils is not None

    def test_sec_utils_has_methods(self):
        """Test that SECUtils has expected methods."""
        from finrobot.data_access.data_source.sec_utils import SECUtils

        # Check for common SEC utility methods
        assert hasattr(SECUtils, "get_10k_section") or hasattr(SECUtils, "get_10k_filings")
