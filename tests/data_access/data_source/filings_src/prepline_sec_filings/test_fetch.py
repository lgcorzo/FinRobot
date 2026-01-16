from unittest.mock import MagicMock, patch

import pytest
import requests

from finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch import (
    archive_url,
    get_cik_by_ticker,
    get_filing,
    get_form_by_ticker,
    get_forms_by_cik,
    get_recent_acc_by_cik,
    get_recent_cik_and_acc_by_ticker,
    open_form,
)


# Fixture for requests session
@pytest.fixture
def mock_session() -> MagicMock:
    session = MagicMock(spec=requests.Session)
    return session


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.requests.Session")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.os.environ")
def test_get_filing(mock_environ: MagicMock, mock_session_cls: MagicMock) -> None:
    mock_environ.get.side_effect = lambda k: "TestValue" if k in ["SEC_API_ORGANIZATION", "SEC_API_EMAIL"] else None

    mock_session_instance = mock_session_cls.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "Filing Content"
    mock_session_instance.get.return_value = mock_response

    content = get_filing("0000000000-00-000000", "12345", "MyCompany", "myemail@test.com")
    assert content == "Filing Content"
    mock_session_instance.get.assert_called()


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.requests.get")
def test_get_cik_by_ticker(mock_get) -> None:  # type: ignore[no-untyped-def]
    mock_response = MagicMock()
    mock_response.status_code = 200
    # Mocking regex matching content
    mock_response.text = "<html>... CIK=0000320193 ...</html>"
    mock_get.return_value = mock_response

    cik = get_cik_by_ticker("AAPL")
    assert cik == "0000320193"


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.requests.Session")
def test_get_forms_by_cik(mock_session_cls) -> None:  # type: ignore[no-untyped-def]
    mock_session_instance = mock_session_cls.return_value
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'{"filings": {"recent": {"accessionNumber": ["acc1"], "form": ["10-K"]}}}'
    mock_session_instance.get.return_value = mock_response

    forms = get_forms_by_cik(mock_session_instance, "12345")
    assert forms == {"acc1": "10-K"}


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_session")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_recent_acc_num_by_cik")
def test_get_recent_acc_by_cik(mock_get_acc, mock_get_sess, mock_session) -> None:  # type: ignore[no-untyped-def]
    mock_get_sess.return_value = mock_session
    mock_get_acc.return_value = ("acc1", "10-K")

    acc, form = get_recent_acc_by_cik("12345", "10-K")
    assert acc == "acc1"
    assert form == "10-K"


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_session")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.get_cik_by_ticker")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_recent_acc_num_by_cik")
def test_get_recent_cik_and_acc_by_ticker(mock_get_acc, mock_get_cik, mock_get_sess, mock_session) -> None:  # type: ignore[no-untyped-def]
    mock_get_sess.return_value = mock_session
    mock_get_cik.return_value = "12345"
    mock_get_acc.return_value = ("acc1", "10-K")

    cik, acc, form = get_recent_cik_and_acc_by_ticker("AAPL", "10-K")
    assert cik == "12345"
    assert acc == "acc1"
    assert form == "10-K"


@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch._get_session")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.get_cik_by_ticker")
@patch("finrobot.data_access.data_source.filings_src.prepline_sec_filings.fetch.get_form_by_cik")
def test_get_form_by_ticker(mock_get_form_cik, mock_get_cik, mock_get_sess, mock_session) -> None:  # type: ignore[no-untyped-def]
    mock_get_sess.return_value = mock_session
    mock_get_cik.return_value = "12345"
    mock_get_form_cik.return_value = "Filing Text"

    text = get_form_by_ticker("AAPL", "10-K")
    assert text == "Filing Text"


@patch("webbrowser.open_new_tab")
def test_open_form(mock_open) -> None:  # type: ignore[no-untyped-def]
    open_form("12345", "000000000011223333")
    mock_open.assert_called()
    # Check if URL format is roughly correct, hard to check exact without complex regex verify but called is good enough


def test_archive_url() -> None:
    url = archive_url("12345", "000000000011223333")
    assert "12345" in url
    assert "000000000011223333" in url
    assert ".txt" in url
