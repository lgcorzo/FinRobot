import os
from unittest.mock import MagicMock, patch

import pytest
from finrobot.data_access.data_source.domains.filings.sec_adapter import SECAdapter
from finrobot.data_access.data_source.filings_src.prepline_sec_filings import fetch


@pytest.fixture(autouse=True)
def setup_env():
    # Global environment patch for the entire test module
    with patch.dict(os.environ, {"SEC_API_KEY": "test", "SEC_API_ORGANIZATION": "Org", "SEC_API_EMAIL": "Email"}):
        yield


def test_sec_adapter_api_key_check():
    with patch.dict(os.environ, {}, clear=True):
        res = SECAdapter.get_10k_metadata("AAPL", "2023-01-01", "2023-12-31")
        assert res is None


def test_sec_adapter_no_filings():
    import finrobot.data_access.data_source.domains.filings.sec_adapter as sa

    with patch.object(sa, "QueryApi") as mock_q_class:
        mock_q = mock_q_class.return_value
        mock_q.get_filings.return_value = {"filings": []}
        sa.query_api = mock_q
        res = SECAdapter.get_10k_metadata("AAPL", "2023-01-01", "2023-12-31")
        assert res is None


def test_sec_adapter_download_errors():
    with patch.object(SECAdapter, "get_10k_metadata", return_value=None):
        res = SECAdapter.download_10k_filing("AAPL", "2023-01-01", "2023-12-31", "tmp")
        assert "No 2023 10-K filing found" in res


def test_sec_adapter_section_logic(tmp_path):
    import finrobot.data_access.data_source.domains.filings.sec_adapter as sa

    with patch.object(sa, "ExtractorApi") as mock_e_class:
        mock_e = mock_e_class.return_value
        mock_e.get_section.return_value = "Section text"
        sa.extractor_api = mock_e

        # Patch os.path.exists to avoid cache hits (Line 168)
        with patch(
            "finrobot.data_access.data_source.domains.filings.sec_adapter.os.path.exists", return_value=False
        ), patch("finrobot.data_access.data_source.domains.filings.sec_adapter.os.makedirs"), patch(
            "builtins.open", MagicMock()
        ):
            with patch("finrobot.data_access.data_source.fmp_utils.FMPUtils.get_sec_report", return_value="Error info"):
                res = sa.SECAdapter.get_10k_section("AAPL", "2023", 1)
                assert res == "Error info"

            with patch(
                "finrobot.data_access.data_source.fmp_utils.FMPUtils.get_sec_report", return_value="Link: http://link"
            ):
                save_path = tmp_path / "save.txt"
                res = sa.SECAdapter.get_10k_section("AAPL", "2023", 1, save_path=str(save_path))
                assert str(res).strip() == "Section text"


def test_fetch_extra_logic():
    s = fetch._get_session(company=None, email=None)
    assert s.headers["User-Agent"] == "Org Email"

    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.get_forms_by_cik"
    ) as mock_forms:
        mock_forms.return_value = {"acc1": "8-K"}
        session = MagicMock()
        with pytest.raises(ValueError, match="No filings found"):
            fetch._get_recent_acc_num_by_cik(session, "123", ["10-K"])

    assert fetch._form_types("10-K", allow_amended_filing=True) == ["10-K", "10-K/A"]

    with patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_recent_acc_num_by_cik",
        return_value=("acc1", "10-K"),
    ), patch(
        "finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_filing", return_value="Content"
    ):
        res = fetch.get_form_by_cik("123", "10-K")
        assert res == "Content"
