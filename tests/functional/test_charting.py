import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finrobot.functional.charting import MplFinanceUtils, ReportChartUtils


@patch("finrobot.functional.charting.YFinanceUtils")
@patch("finrobot.functional.charting.mpf.plot")
def test_plot_stock_price_chart(mock_mpf_plot, mock_yf) -> None:  # type: ignore[no-untyped-def]
    mock_yf.get_stock_data.return_value = pd.DataFrame({"Close": [100]})

    # Test with verbose=True
    result = MplFinanceUtils.plot_stock_price_chart(
        ticker_symbol="AAPL", start_date="2023-01-01", end_date="2023-02-01", save_path="chart.png", verbose=True
    )
    assert "chart saved" in result
    mock_mpf_plot.assert_called_once()


@patch("finrobot.functional.charting.YFinanceUtils")
@patch("finrobot.functional.charting.plt")
@patch("os.path.isdir")
def test_get_share_performance(mock_isdir, mock_plt, mock_yf) -> None:  # type: ignore[no-untyped-def]
    mock_plt.subplots.return_value = (MagicMock(), MagicMock())
    mock_plt.figure.return_value = MagicMock()

    mock_isdir.return_value = True  # Test directory path
    data = pd.DataFrame({"Close": [100, 110]}, index=[pd.Timestamp("2023-01-01"), pd.Timestamp("2023-02-01")])
    mock_yf.get_stock_data.return_value = data
    mock_yf.get_stock_info.return_value = {"shortName": "Apple", "currency": "USD"}

    # Pass datetime object to cover that branch if applicable, or rely on str parsing coverage
    result = ReportChartUtils.get_share_performance("AAPL", pd.Timestamp("2023-01-01"), "save_dir")
    assert "stock performance chart saved" in result
    mock_plt.savefig.assert_called_once()
    assert "stock_performance.png" in str(mock_plt.savefig.call_args)


@patch("finrobot.functional.charting.YFinanceUtils")
@patch("finrobot.functional.charting.plt")
@patch("os.path.isdir")
def test_get_pe_eps_performance(mock_isdir, mock_plt, mock_yf) -> None:  # type: ignore[no-untyped-def]
    mock_plt.subplots.return_value = (MagicMock(), MagicMock())

    mock_isdir.return_value = False
    # Mock income stmt for EPS
    mock_yf.get_income_stmt.return_value = pd.DataFrame(
        {"2023-01-01": [5.0], "2022-01-01": [4.5]}, index=["Diluted EPS"]
    )

    # Mock stock data with missing date to trigger asof logic
    # Dates needed: 2023-01-01 (Sunday) -> Should find 2022-12-30 or similar
    # asof requires sorted (ascending) index.
    idx = pd.to_datetime(["2022-12-30", "2023-01-01"], utc=True).sort_values()
    historical_data = pd.DataFrame({"Close": [135.0, 150.0]}, index=idx)
    mock_yf.get_stock_data.return_value = historical_data

    mock_yf.get_stock_info.return_value = {"shortName": "Apple"}

    # Test with datetime object
    result = ReportChartUtils.get_pe_eps_performance("AAPL", pd.Timestamp("2023-01-01"), years=1, save_path="pe.png")
    assert "pe performance chart saved" in result
    mock_plt.savefig.assert_called_once()
