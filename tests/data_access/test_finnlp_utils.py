import os
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.data_access.data_source.finnlp_utils import FinNLPUtils


@pytest.fixture
def finnhub_api_key() -> None:
    with patch.dict(os.environ, {"FINNHUB_API_KEY": "test_key"}):
        yield "test_key"


class TestFinNLPUtils:
    @patch("finrobot.data_access.data_source.finnlp_utils.CNBC_Streaming")
    @patch("finrobot.data_access.data_source.finnlp_utils.streaming_download")
    def test_cnbc_news_download(self, mock_download, mock_streaming_cls) -> None:  # type: ignore[no-untyped-def]
        mock_streaming = MagicMock()
        mock_streaming_cls.return_value = mock_streaming
        mock_download.return_value = pd.DataFrame({"title": ["News 1"]})

        result = FinNLPUtils.cnbc_news_download("AAPL")
        assert not result.empty
        assert result.iloc[0]["title"] == "News 1"

    @patch("finrobot.data_access.data_source.finnlp_utils.Finnhub_Date_Range")
    @patch("finrobot.data_access.data_source.finnlp_utils.date_range_download")
    def test_finnhub_news_download(self, mock_download, mock_date_range_cls, finnhub_api_key) -> None:  # type: ignore[no-untyped-def]
        mock_date_range = MagicMock()
        mock_date_range_cls.return_value = mock_date_range
        mock_download.return_value = pd.DataFrame({"headline": ["Headline 1"]})

        result = FinNLPUtils.finnhub_news_download("2023-01-01", "2023-01-31", "AAPL")
        assert not result.empty
        assert result.iloc[0]["headline"] == "Headline 1"

    @patch("finrobot.data_access.data_source.finnlp_utils.Xueqiu_Streaming")
    @patch("finrobot.data_access.data_source.finnlp_utils.streaming_download")
    def test_xueqiu_social_media_download(self, mock_download, mock_streaming_cls) -> None:  # type: ignore[no-untyped-def]
        mock_streaming = MagicMock()
        mock_streaming_cls.return_value = mock_streaming
        mock_download.return_value = pd.DataFrame({"text": ["Social Post 1"]})

        result = FinNLPUtils.xueqiu_social_media_download("AAPL")
        assert not result.empty
        assert result.iloc[0]["text"] == "Social Post 1"

    @patch("finrobot.data_access.data_source.finnlp_utils.Yicai_Streaming")
    @patch("finrobot.data_access.data_source.finnlp_utils.streaming_download")
    def test_yicai_news_download(self, mock_download, mock_streaming_cls) -> None:  # type: ignore[no-untyped-def]
        # Mock class instantiation
        mock_streaming = MagicMock()
        mock_streaming_cls.return_value = mock_streaming

        # Mock streaming_download return
        expected_df = pd.DataFrame({"title": ["Yicai News"], "source": ["Yicai"]})
        mock_download.return_value = expected_df

        result = FinNLPUtils.yicai_news_download("Keyword")

        # Verify call args
        # Only verify download was called with class, as streaming_download calls the class
        mock_download.assert_called_once()
        args, _ = mock_download.call_args
        # Arg 0 is class, Arg 3 is keyword
        assert args[0] == mock_streaming_cls
        assert args[3] == "Keyword"
        assert result.iloc[0]["title"] == "Yicai News"

    @patch("finrobot.data_access.data_source.finnlp_utils.InvestorPlace_Streaming")
    @patch("finrobot.data_access.data_source.finnlp_utils.streaming_download")
    def test_investor_place_news_download(self, mock_download, mock_streaming_cls) -> None:  # type: ignore[no-untyped-def]
        mock_streaming = MagicMock()
        mock_streaming_cls.return_value = mock_streaming
        mock_download.return_value = pd.DataFrame({"title": ["InvestorPlace"]})

        result = FinNLPUtils.investor_place_news_download("Keyword")
        assert not result.empty
        assert result.iloc[0]["title"] == "InvestorPlace"

    @patch("finrobot.data_access.data_source.finnlp_utils.Sina_Finance_Date_Range")
    @patch("finrobot.data_access.data_source.finnlp_utils.date_range_download")
    def test_sina_finance_news_download(self, mock_download, mock_date_range_cls) -> None:  # type: ignore[no-untyped-def]
        mock_date_range = MagicMock()
        mock_date_range_cls.return_value = mock_date_range
        mock_download.return_value = pd.DataFrame({"title": ["Sina News"]})

        result = FinNLPUtils.sina_finance_news_download("2023-01-01", "2023-01-02")
        assert not result.empty
        mock_download.assert_called_once()
        args, _ = mock_download.call_args
        assert args[3] == "2023-01-01"  # start_date

    @patch("finrobot.data_access.data_source.finnlp_utils.Stocktwits_Streaming")
    @patch("finrobot.data_access.data_source.finnlp_utils.streaming_download")
    def test_stocktwits_social_media_download(self, mock_download, mock_streaming_cls) -> None:  # type: ignore[no-untyped-def]
        mock_streaming = MagicMock()
        mock_streaming_cls.return_value = mock_streaming
        mock_download.return_value = pd.DataFrame({"body": ["Tweet"]})

        result = FinNLPUtils.stocktwits_social_media_download("AAPL")
        assert not result.empty
        assert result.iloc[0]["body"] == "Tweet"

    # Test internal helper functions logic via imports
    def test_streaming_download_logic(self) -> None:
        from finrobot.data_access.data_source.finnlp_utils import streaming_download

        # Case 1: has download_streaming_search
        mock_cls_search = MagicMock()
        mock_inst_search = MagicMock()
        mock_cls_search.return_value = mock_inst_search
        mock_inst_search.download_streaming_search = MagicMock()
        mock_inst_search.dataframe = pd.DataFrame({"col1": [1]})

        streaming_download(mock_cls_search, {}, "Tag", "Key", 1, ["col1"], None)
        mock_inst_search.download_streaming_search.assert_called_with("Key", 1)

        # Case 2: has download_streaming_stock
        mock_cls_stock = MagicMock()
        mock_inst_stock = MagicMock()
        mock_cls_stock.return_value = mock_inst_stock
        # Ensure it doesn't have search
        del mock_inst_stock.download_streaming_search
        mock_inst_stock.download_streaming_stock = MagicMock()
        mock_inst_stock.dataframe = pd.DataFrame({"col1": [1]})

        streaming_download(mock_cls_stock, {}, "Tag", "Key", 1, ["col1"], None)
        mock_inst_stock.download_streaming_stock.assert_called_with("Key", 1)

        # Case 3: else (download_streaming_all)
        mock_cls_all = MagicMock()
        mock_inst_all = MagicMock()
        mock_cls_all.return_value = mock_inst_all
        del mock_inst_all.download_streaming_search
        del mock_inst_all.download_streaming_stock
        mock_inst_all.download_streaming_all = MagicMock()
        mock_inst_all.dataframe = pd.DataFrame({"col1": [1]})

        # When keyword is relevant or not for 'all', usually logic ignores it if calling 'all'
        streaming_download(mock_cls_all, {}, "Tag", "Key", 1, ["col1"], None)
        mock_inst_all.download_streaming_all.assert_called_with(1)

    def test_date_range_download_logic(self) -> None:
        from finrobot.data_access.data_source.finnlp_utils import date_range_download

        # Case 1: has download_date_range_stock
        mock_cls_stock = MagicMock()
        mock_inst_stock = MagicMock()
        mock_cls_stock.return_value = mock_inst_stock
        mock_inst_stock.download_date_range_stock = MagicMock()
        mock_inst_stock.dataframe = pd.DataFrame({"col1": [1]})

        date_range_download(mock_cls_stock, {}, "Tag", "2023-01-01", "2023-01-02", "AAPL", ["col1"], None)
        mock_inst_stock.download_date_range_stock.assert_called_with("2023-01-01", "2023-01-02", "AAPL")

        # Case 2: else (download_date_range_all) + gather_content
        mock_cls_all = MagicMock()
        mock_inst_all = MagicMock()
        mock_cls_all.return_value = mock_inst_all
        del mock_inst_all.download_date_range_stock
        mock_inst_all.download_date_range_all = MagicMock()
        mock_inst_all.gather_content = MagicMock()
        mock_inst_all.dataframe = pd.DataFrame({"col1": [1]})

        date_range_download(mock_cls_all, {}, "Tag", "2023-01-01", "2023-01-02", None, ["col1"], None)
        mock_inst_all.download_date_range_all.assert_called_with("2023-01-01", "2023-01-02")
        mock_inst_all.gather_content.assert_called()
