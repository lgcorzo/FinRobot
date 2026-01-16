"""FinnHub News Adapter - News Repository Implementation."""

import os
import random
import typing as T
from datetime import datetime
from functools import wraps
from typing import Annotated, Any, Callable, Optional

import finnhub
import pandas as pd

from finrobot.infrastructure.io.files import SavePathType, save_output
from finrobot.infrastructure.utils import decorate_all_methods

finnhub_client: T.Any = None


def init_finnhub_client(func: T.Callable[..., T.Any]) -> T.Callable[..., T.Any]:
    @wraps(func)
    def wrapper(*args: T.Any, **kwargs: T.Any) -> T.Any:
        global finnhub_client
        if os.environ.get("FINNHUB_API_KEY") is None:
            print("Please set the environment variable FINNHUB_API_KEY to use the Finnhub API.")
            return None
        else:
            finnhub_client = finnhub.Client(api_key=os.environ["FINNHUB_API_KEY"])
            print("Finnhub client initialized")
            return func(*args, **kwargs)

    return wrapper


@decorate_all_methods(init_finnhub_client)
class FinnHubNewsAdapter:
    """FinnHub implementation for news data."""

    def get_company_news(
        symbol: Annotated[str, "ticker symbol"],
        start_date: Annotated[str, "start date yyyy-mm-dd"],
        end_date: Annotated[str, "end date yyyy-mm-dd"],
        max_news_num: Annotated[int, "maximum number of news to return"] = 10,
        save_path: SavePathType = None,
    ) -> pd.DataFrame:
        """Retrieve market news related to designated company."""
        news = finnhub_client.company_news(symbol, _from=start_date, to=end_date)
        if len(news) == 0:
            print(f"No company news found for symbol {symbol} from finnhub!")
        news = [
            {
                "date": datetime.fromtimestamp(n["datetime"]).strftime("%Y%m%d%H%M%S"),
                "headline": n["headline"],
                "summary": n["summary"],
            }
            for n in news
        ]
        if len(news) > max_news_num:
            news = random.choices(news, k=max_news_num)
        news.sort(key=lambda x: x["date"])
        output = pd.DataFrame(news)
        save_output(output, f"company news of {symbol}", save_path=save_path)

        return output
