import os
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finrobot.data_access.data_source.domains.social.reddit_adapter import RedditAdapter


@pytest.fixture
def reddit_creds():
    with patch.dict(os.environ, {"REDDIT_CLIENT_ID": "test_id", "REDDIT_CLIENT_SECRET": "test_secret"}):
        yield


class TestRedditAdapter:
    @patch("finrobot.data_access.data_source.domains.social.reddit_adapter.praw.Reddit")
    def test_get_reddit_posts(self, mock_reddit_cls, reddit_creds):
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

        mock_subreddit.search.return_value = [mock_post1]

        df = RedditAdapter.get_reddit_posts(
            query="AAPL",
            start_date="2023-01-01",
            end_date="2023-01-31",
            selected_columns=["created_utc", "id", "title", "score", "num_comments"],
        )

        assert len(df) == 3  # 3 subreddits
        assert "Title 1" in df["title"].values
        assert "id1" in df["id"].values
