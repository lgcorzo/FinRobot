from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("torch")

from finrobot.data_access.data_source.finance_data import get_data


class TestFinanceData:
    @patch("finrobot.data_access.data_source.finance_data.unstructured_sec_main")
    def test_get_data_unstructured(self, mock_unstructured) -> None:  # type: ignore[no-untyped-def]
        mock_unstructured.return_value = ({"data": "content"}, ["form1"])

        sec_data, sec_form_names = get_data("AAPL", "2023", data_source="unstructured")
        assert sec_data == {"data": "content"}
        assert sec_form_names == ["form1"]

    @patch("finrobot.data_access.data_source.finance_data.get_earnings_all_docs")
    def test_get_data_earnings_calls(self, mock_get_earnings) -> None:  # type: ignore[no-untyped-def]
        mock_get_earnings.return_value = (["doc1"], "Q1", ["s1"], ["s2"], ["s3"], ["s4"])

        result = get_data("AAPL", "2023", data_source="earnings_calls")
        assert result[0] == ["doc1"]
        assert result[1] == "Q1"

    @patch("finrobot.data_access.data_source.finance_data.sec_save_pdfs")
    @patch("finrobot.data_access.data_source.finance_data.run_marker_single")
    def test_get_data_marker_pdf(self, mock_run_marker, mock_save_pdfs) -> None:  # type: ignore[no-untyped-def]
        mock_save_pdfs.return_value = (["url1"], {"meta": "data"}, "path/to/meta", "path/to/input")

        # Test non-batch processing
        get_data("AAPL", "2023", data_source="marker_pdf", batch_processing=False, batch_multiplier=2)
        mock_run_marker.assert_called_once()
