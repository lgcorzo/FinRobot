"""FMP Filings Adapter - SEC report data from Financial Modeling Prep."""

import os
import requests
from typing import Annotated
from functools import wraps

from finrobot.infrastructure.utils import decorate_all_methods


def init_fmp_api(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global fmp_api_key
        if os.environ.get("FMP_API_KEY") is None:
            print("Please set the environment variable FMP_API_KEY to use the FMP API.")
            return None
        else:
            fmp_api_key = os.environ["FMP_API_KEY"]
            print("FMP api key found successfully.")
            return func(*args, **kwargs)

    return wrapper


@decorate_all_methods(init_fmp_api)
class FMPFilingsAdapter:
    """FMP implementation for SEC filings data."""

    def get_sec_report(
        ticker_symbol: Annotated[str, "ticker symbol"],
        fyear: Annotated[str, "year of the 10-K report, 'yyyy' or 'latest'"] = "latest",
    ) -> str:
        """Get the url and filing date of the 10-K report for a given stock and year."""

        url = f"https://financialmodelingprep.com/api/v3/sec_filings/{ticker_symbol}?type=10-k&page=0&apikey={fmp_api_key}"

        filing_url = None
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if fyear == "latest":
                filing_url = data[0]["finalLink"]
                filing_date = data[0]["fillingDate"]
            else:
                for filing in data:
                    if filing["fillingDate"].split("-")[0] == fyear:
                        filing_url = filing["finalLink"]
                        filing_date = filing["fillingDate"]
                        break

            return f"Link: {filing_url}\nFiling Date: {filing_date}"
        else:
            return f"Failed to retrieve data: {response.status_code}"
