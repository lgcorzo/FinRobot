"""Tests for charting utils."""

from unittest.mock import patch

import pandas as pd
import pytest
from finrobot.functional.charting import MplFinanceUtils


@pytest.fixture
def mock_stock_data():
    dates = pd.date_range(start="2025-01-01", periods=5)
    df = pd.DataFrame(
        {
            "Open": [100, 101, 102, 103, 104],
            "High": [105, 106, 107, 108, 109],
            "Low": [95, 96, 97, 98, 99],
            "Close": [102, 103, 104, 105, 106],
            "Volume": [1000, 1100, 1200, 1300, 1400],
        },
        index=dates,
    )
    return df


@patch("finrobot.functional.charting.YFinanceUtils.get_stock_data")
@patch("finrobot.functional.charting.mpf.plot")
def test_plot_stock_price_chart(mock_plot, mock_get_stock, mock_stock_data, tmp_path):
    """Test plotting chart calls dependencies correctly."""

    mock_get_stock.return_value = mock_stock_data

    save_path = str(tmp_path / "chart.png")

    result = MplFinanceUtils.plot_stock_price_chart("AAPL", "2025-01-01", "2025-01-05", save_path)

    assert "saved to" in result
    mock_get_stock.assert_called()
    mock_plot.assert_called()

    args, kwargs = mock_plot.call_args
    assert kwargs["type"] == "candle"
    assert kwargs["savefig"] == save_path
