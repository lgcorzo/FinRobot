from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from finrobot.functional.quantitative import BackTraderUtils, DeployedCapitalAnalyzer


@patch("finrobot.functional.quantitative.yf.download")
@patch("finrobot.functional.quantitative.bt.Cerebro")
def test_back_test_sma_crossover(mock_cerebro_cls, mock_yf_download) -> None:  # type: ignore[no-untyped-def]
    # Mock yfinance data
    data = pd.DataFrame(
        {"Open": [100, 101], "High": [102, 103], "Low": [98, 99], "Close": [101, 102], "Volume": [1000, 1100]},
        index=pd.to_datetime(["2023-01-01", "2023-01-02"]),
    )
    mock_yf_download.return_value = data

    # Mock Cerebro
    mock_cerebro = MagicMock()
    mock_cerebro_cls.return_value = mock_cerebro
    mock_strategy = MagicMock()
    mock_cerebro.run.return_value = [mock_strategy]

    # Add analyzers to strategy mock
    mock_analyzer = MagicMock()
    mock_analyzer.get_analysis.return_value = {"value": 1.0}
    mock_strategy.analyzers.sharpe_ratio = mock_analyzer
    mock_strategy.analyzers.draw_down = mock_analyzer
    mock_strategy.analyzers.returns = mock_analyzer
    mock_strategy.analyzers.trade_analyzer = mock_analyzer

    result = BackTraderUtils.back_test(
        ticker_symbol="AAPL",
        start_date="2023-01-01",
        end_date="2023-01-02",
        strategy="SMA_CrossOver",
        strategy_params='{"fast": 10, "slow": 30}',
        cash=5000.0,
        sizer=10,
    )

    assert "Back Test Finished" in result
    mock_cerebro.addstrategy.assert_called()
    mock_cerebro.broker.setcash.assert_called_with(5000.0)


@patch("finrobot.functional.quantitative.importlib.import_module")
@patch("finrobot.functional.quantitative.yf.download")
@patch("finrobot.functional.quantitative.bt.Cerebro")
def test_back_test_custom_components(mock_cerebro_cls, mock_yf_download, mock_import) -> None:  # type: ignore[no-untyped-def]
    # Mock custom module
    mock_module = MagicMock()
    mock_import.return_value = mock_module

    mock_strategy_class = MagicMock()
    setattr(mock_module, "CustomStrategy", mock_strategy_class)

    mock_sizer_class = MagicMock()
    setattr(mock_module, "CustomSizer", mock_sizer_class)

    mock_indicator_class = MagicMock()
    setattr(mock_module, "CustomIndicator", mock_indicator_class)

    mock_yf_download.return_value = pd.DataFrame({"Close": [100]})
    mock_cerebro = MagicMock()
    mock_cerebro_cls.return_value = mock_cerebro
    mock_cerebro.run.return_value = [MagicMock()]

    BackTraderUtils.back_test(
        ticker_symbol="AAPL",
        start_date="2023-01-01",
        end_date="2023-01-02",
        strategy="my_module:CustomStrategy",
        sizer="my_module:CustomSizer",
        indicator="my_module:CustomIndicator",
    )

    assert mock_import.call_count == 3
    mock_cerebro.addstrategy.assert_called()
    mock_cerebro.addsizer.assert_called()
    mock_cerebro.addindicator.assert_called()


def test_deployed_capital_analyzer() -> None:
    analyzer = DeployedCapitalAnalyzer()
    analyzer.strategy = MagicMock()
    analyzer.strategy.broker.get_cash.return_value = 10000.0
    analyzer.strategy.broker.get_value.return_value = 10500.0

    analyzer.start()

    # Buy order
    order = MagicMock()
    order.status = order.Completed
    order.isbuy.return_value = True
    order.issell.return_value = False
    order.executed.price = 100.0
    order.executed.size = 10
    analyzer.notify_order(order)

    # Sell order
    sell_order = MagicMock()
    sell_order.status = sell_order.Completed
    sell_order.isbuy.return_value = False
    sell_order.issell.return_value = True
    sell_order.executed.price = 110.0
    sell_order.executed.size = 10
    analyzer.notify_order(sell_order)

    analyzer.stop()
    analysis = analyzer.get_analysis()

    # Initial cash: 10000, final value: 10500 -> net profit: 500
    # Total deployed: 100*10 + 110*10 = 1000 + 1100 = 2100
    # Return: 500 / 2100 = 0.238...
    assert analysis["return_on_deployed_capital"] == pytest.approx(500 / 2100)


def test_deployed_capital_analyzer_no_deployment() -> None:
    analyzer = DeployedCapitalAnalyzer()
    analyzer.strategy = MagicMock()
    analyzer.strategy.broker.get_cash.return_value = 10000.0
    analyzer.strategy.broker.get_value.return_value = 10000.0
    analyzer.start()
    analyzer.stop()
    assert analyzer.get_analysis()["return_on_deployed_capital"] == 0
