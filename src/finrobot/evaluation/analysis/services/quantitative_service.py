import importlib
import json
import os
import typing as T
from pprint import pformat

import backtrader as bt
import yfinance as yf
from backtrader.strategies import SMA_CrossOver
from matplotlib import pyplot as plt


class DeployedCapitalAnalyzer(bt.Analyzer):
    def start(self) -> None:
        self.deployed_capital: T.List[float] = []
        self.initial_cash = self.strategy.broker.get_cash()  # Initial cash in account

    def notify_order(self, order: T.Any) -> None:
        if order.status in [order.Completed]:
            if order.isbuy():
                price = getattr(order.executed, "price", 0.0)
                size = getattr(order.executed, "size", 0.0)
                self.deployed_capital.append(price * size)
            elif order.issell():
                price = getattr(order.executed, "price", 0.0)
                size = getattr(order.executed, "size", 0.0)
                self.deployed_capital.append(price * size)

    def stop(self) -> None:
        total_deployed = sum(self.deployed_capital)
        final_cash = self.strategy.broker.get_value()
        net_profit = final_cash - self.initial_cash
        if total_deployed > 0:
            self.retn = net_profit / total_deployed
        else:
            self.retn = 0.0

    def get_analysis(self) -> T.Dict[str, float]:
        return {"return_on_deployed_capital": self.retn}


class BackTraderUtils:
    @staticmethod
    def back_test(
        ticker_symbol: str,
        start_date: str,
        end_date: str,
        strategy: str,
        strategy_params: str = "",
        sizer: T.Optional[T.Union[int, str]] = None,
        sizer_params: str = "",
        indicator: T.Optional[str] = None,
        indicator_params: str = "",
        cash: float = 10000.0,
        save_fig: T.Optional[str] = None,
    ) -> str:
        """
        Use the Backtrader library to backtest a trading strategy on historical stock data.
        """
        cerebro = bt.Cerebro()

        if strategy == "SMA_CrossOver":
            strategy_class = SMA_CrossOver
        else:
            assert ":" in strategy, "Custom strategy should be module path and class name separated by a colon."
            module_path, class_name = strategy.split(":")
            module = importlib.import_module(module_path)
            strategy_class = getattr(module, class_name)

        if isinstance(strategy_params, str):
            parsed_strategy_params: T.Dict[str, T.Any] = json.loads(strategy_params) if strategy_params else {}
        else:
            parsed_strategy_params = strategy_params
        cerebro.addstrategy(strategy_class, **parsed_strategy_params)
        dataname_yf = yf.download(ticker_symbol, start_date, end_date, auto_adjust=True)
        dataname_yf.columns = [col[0] if isinstance(col, tuple) else col for col in dataname_yf.columns.values]
        # Create a data feed
        data = bt.feeds.PandasData(dataname=dataname_yf)
        cerebro.adddata(data)  # Add the data feed
        # Set our desired cash start
        cerebro.broker.setcash(cash)

        # Set the size of the trades
        if sizer is not None:
            if isinstance(sizer, int):
                cerebro.addsizer(bt.sizers.FixedSize, stake=sizer)
            else:
                assert ":" in sizer, "Custom sizer should be module path and class name separated by a colon."
                module_path, class_name = sizer.split(":")
                module = importlib.import_module(module_path)
                sizer_class = getattr(module, class_name)
                parsed_sizer_params: T.Dict[str, T.Any] = json.loads(sizer_params) if sizer_params else {}
                cerebro.addsizer(sizer_class, **parsed_sizer_params)

        # Set additional indicator
        if indicator is not None:
            assert ":" in indicator, "Custom indicator should be module path and class name separated by a colon."
            module_path, class_name = indicator.split(":")
            module = importlib.import_module(module_path)
            indicator_class = getattr(module, class_name)
            parsed_indicator_params: T.Dict[str, T.Any] = json.loads(indicator_params) if indicator_params else {}
            cerebro.addindicator(indicator_class, **parsed_indicator_params)

        # Attach analyzers
        cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe_ratio")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="draw_down")
        cerebro.addanalyzer(bt.analyzers.Returns, _name="returns")
        cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trade_analyzer")
        # cerebro.addanalyzer(DeployedCapitalAnalyzer, _name="deployed_capital")

        stats_dict = {"Starting Portfolio Value:": cerebro.broker.getvalue()}

        results = cerebro.run()  # run it all
        first_strategy = results[0]

        # Access analysis results
        stats_dict["Final Portfolio Value"] = cerebro.broker.getvalue()
        # stats_dict["Deployed Capital"] = pformat(
        #     first_strategy.analyzers.deployed_capital.get_analysis(), indent=4
        # )
        stats_dict["Sharpe Ratio"] = first_strategy.analyzers.sharpe_ratio.get_analysis()
        stats_dict["Drawdown"] = first_strategy.analyzers.draw_down.get_analysis()
        stats_dict["Returns"] = first_strategy.analyzers.returns.get_analysis()
        stats_dict["Trade Analysis"] = first_strategy.analyzers.trade_analyzer.get_analysis()

        if save_fig:
            directory = os.path.dirname(save_fig)
            if directory:
                os.makedirs(directory, exist_ok=True)
            plt.figure(figsize=(12, 8))
            cerebro.plot()
            plt.savefig(save_fig)
            plt.close()

        return "Back Test Finished. Results: \n" + pformat(stats_dict, indent=2)


if __name__ == "__main__":
    # Example usage:
    start_date = "2011-01-01"
    end_date = "2012-12-31"
    ticker = "MSFT"
    # BackTraderUtils.back_test(
    #     ticker, start_date, end_date, "SMA_CrossOver", {"fast": 10, "slow": 30}
    # )
    BackTraderUtils.back_test(
        ticker,
        start_date,
        end_date,
        "test_module:TestStrategy",
        '{"exitbars": 5}',
    )
