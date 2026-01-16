import os
import typing as T
from datetime import datetime, timezone
from functools import wraps

import pandas as pd
import praw

from finrobot.infrastructure.io.files import SavePathType, save_output
from finrobot.infrastructure.utils import decorate_all_methods

reddit_client: T.Any = None


def init_reddit_client(func: T.Callable[..., T.Any]) -> T.Callable[..., T.Any]:
    @wraps(func)
    def wrapper(*args: T.Any, **kwargs: T.Any) -> T.Any:
        global reddit_client
        if not all([os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")]):
            print("Please set the environment variables for Reddit API credentials.")
            return None
        else:
            reddit_client = praw.Reddit(
                client_id=os.environ["REDDIT_CLIENT_ID"],
                client_secret=os.environ["REDDIT_CLIENT_SECRET"],
                user_agent="python:finrobot:v0.1 (by /u/finrobot)",
            )
            print("Reddit client initialized")
            return func(*args, **kwargs)

    return wrapper


@decorate_all_methods(init_reddit_client)
class RedditAdapter:
    """Reddit implementation of SocialRepository."""

    def get_reddit_posts(
        query: str,
        start_date: str,
        end_date: str,
        limit: int = 1000,
        selected_columns: T.List[str] = ["created_utc", "title", "score", "num_comments"],
        save_path: SavePathType = None,
    ) -> pd.DataFrame:
        """
        Get Reddit posts from r/wallstreetbets & r/stocks & r/investing based on the search query and date range.
        """

        post_data = []

        start_timestamp = int(datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
        end_timestamp = int(datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())

        for subreddit_name in ["wallstreetbets", "stocks", "investing"]:
            print("Searching in subreddit:", subreddit_name)
            subreddit = reddit_client.subreddit(subreddit_name)
            posts = subreddit.search(query, limit=limit)

            for post in posts:
                if start_timestamp <= post.created_utc <= end_timestamp:
                    post_data.append(
                        [
                            datetime.fromtimestamp(post.created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                            post.id,
                            post.title,
                            post.selftext,
                            post.score,
                            post.num_comments,
                            post.url,
                        ]
                    )

        output = pd.DataFrame(
            post_data,
            columns=[
                "created_utc",
                "id",
                "title",
                "selftext",
                "score",
                "num_comments",
                "url",
            ],
        )
        output = output[selected_columns]

        save_output(output, f"reddit posts related to {query}", save_path=save_path)

        return output


# Example usage
if __name__ == "__main__":
    from finrobot.infrastructure.io.files import register_keys_from_json

    register_keys_from_json("../../config_api_keys")

    # df = RedditAdapter.get_reddit_posts(query="AAPL OR Apple Inc OR #AAPL OR (Apple AND stock)", start_date="2023-05-01", end_date="2023-06-01", limit=1000)
    df = RedditAdapter.get_reddit_posts(query="NVDA", start_date="2023-05-01", end_date="2023-06-01", limit=1000)
    print(df.head())
    df.to_csv("reddit_posts.csv", index=False)
