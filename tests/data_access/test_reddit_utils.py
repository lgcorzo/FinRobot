import os
from datetime import datetime, timezone
from typing import Generator
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.data_access.data_source.reddit_utils import RedditUtils


@pytest.fixture
def reddit_creds() -> Generator[None, None, None]:
    with patch.dict(os.environ, {"REDDIT_CLIENT_ID": "test_id", "REDDIT_CLIENT_SECRET": "test_secret"}):
        yield


class TestRedditUtils:
    @patch("finrobot.data_access.data_source.reddit_utils.praw.Reddit")
    def test_get_reddit_posts(self, mock_reddit_cls: MagicMock, reddit_creds: None) -> None:
        mock_reddit = MagicMock()
        mock_reddit_cls.return_value = mock_reddit

        mock_subreddit = MagicMock()
        mock_reddit.subreddit.return_value = mock_subreddit

        # Create mock posts
        mock_post1 = MagicMock()
        mock_post1.created_utc = datetime.strptime("2023-01-02", "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()
        mock_post1.id = "id1"
        mock_post1.title = "Title 1"
        mock_post1.selftext = "Text 1"
        mock_post1.score = 100
        mock_post1.num_comments = 10
        mock_post1.url = "http://url1"

        mock_post2 = MagicMock()  # This one falls outside the range
        mock_post2.created_utc = datetime.strptime("2022-01-02", "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()

        mock_subreddit.search.return_value = [mock_post1, mock_post2]

        df = RedditUtils.get_reddit_posts(
            query="AAPL",
            start_date="2023-01-01",
            end_date="2023-01-31",
            selected_columns=["created_utc", "id", "title", "score", "num_comments"],
        )

        assert len(df) == 3  # 3 subreddits searched, each returns mock_post1 (falling in range)
        # Wait, for each subreddit it returns the same mock list.
        # subreddit list is ["wallstreetbets", "stocks", "investing"]
        # mock_post1 is in range for all 3.
        # so total 3 rows.
        assert "Title 1" in df["title"].values
        assert "id1" in df["id"].values
