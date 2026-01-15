"""FinnHub Adapter - Market Data Repository Implementation."""

import os
import finnhub
import pandas as pd
import json
from typing import Annotated
from collections import defaultdict
from functools import wraps
from datetime import datetime

from finrobot.infrastructure.utils import decorate_all_methods
from finrobot.infrastructure.io.files import save_output, SavePathType


def init_finnhub_client(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
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
class FinnHubMarketAdapter:
    """FinnHub implementation for market data (company profiles, financials)."""

    def get_company_profile(symbol: Annotated[str, "ticker symbol"]) -> str:
        """Get a company's profile information."""
        profile = finnhub_client.company_profile2(symbol=symbol)
        if not profile:
            return f"Failed to find company profile for symbol {symbol} from finnhub!"

        formatted_str = (
            "[Company Introduction]:\n\n{name} is a leading entity in the {finnhubIndustry} sector. "
            "Incorporated and publicly traded since {ipo}, the company has established its reputation as "
            "one of the key players in the market. As of today, {name} has a market capitalization "
            "of {marketCapitalization:.2f} in {currency}, with {shareOutstanding:.2f} shares outstanding."
            "\n\n{name} operates primarily in the {country}, trading under the ticker {ticker} on the {exchange}. "
            "As a dominant force in the {finnhubIndustry} space, the company continues to innovate and drive "
            "progress within the industry."
        ).format(**profile)

        return formatted_str

    def get_basic_financials_history(
        symbol: Annotated[str, "ticker symbol"],
        freq: Annotated[str, "reporting frequency: annual / quarterly"],
        start_date: Annotated[str, "start date yyyy-mm-dd"],
        end_date: Annotated[str, "end date yyyy-mm-dd"],
        selected_columns: Annotated[list[str] | None, "columns to return"] = None,
        save_path: SavePathType = None,
    ) -> pd.DataFrame:
        """Get historical basic financials."""
        if freq not in ["annual", "quarterly"]:
            return f"Invalid reporting frequency {freq}."

        basic_financials = finnhub_client.company_basic_financials(symbol, "all")
        if not basic_financials["series"]:
            return f"Failed to find basic financials for symbol {symbol}!"

        output_dict = defaultdict(dict)
        for metric, value_list in basic_financials["series"][freq].items():
            if selected_columns and metric not in selected_columns:
                continue
            for value in value_list:
                if value["period"] >= start_date and value["period"] <= end_date:
                    output_dict[metric].update({value["period"]: value["v"]})

        financials_output = pd.DataFrame(output_dict)
        financials_output = financials_output.rename_axis(index="date")
        save_output(financials_output, "basic financials", save_path=save_path)

        return financials_output

    def get_basic_financials(
        symbol: Annotated[str, "ticker symbol"],
        selected_columns: Annotated[list[str] | None, "columns to return"] = None,
    ) -> str:
        """Get latest basic financials."""
        basic_financials = finnhub_client.company_basic_financials(symbol, "all")
        if not basic_financials["series"]:
            return f"Failed to find basic financials for symbol {symbol}!"

        output_dict = basic_financials["metric"]
        for metric, value_list in basic_financials["series"]["quarterly"].items():
            value = value_list[0]
            output_dict.update({metric: value["v"]})

        for k in list(output_dict.keys()):
            if selected_columns and k not in selected_columns:
                output_dict.pop(k)

        return json.dumps(output_dict, indent=2)
