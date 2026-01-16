from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from finrobot.functional.analyzer import ReportAnalysisUtils, combine_prompt, save_to_file


def test_combine_prompt() -> None:
    assert combine_prompt("instr", "res") == "Resource: res\n\nInstruction: instr"
    assert combine_prompt("instr", "res", "tab") == "tab\n\nResource: res\n\nInstruction: instr"


@patch("os.makedirs")
def test_save_to_file(mock_makedirs) -> None:
    m = mock_open()
    with patch("builtins.open", m):
        save_to_file("data", "path/to/file.txt")
    mock_makedirs.assert_called_once_with("path/to", exist_ok=True)
    m().write.assert_called_once_with("data")


@patch("finrobot.functional.analyzer.YFinanceUtils")
@patch("finrobot.functional.analyzer.SECUtils")
@patch("finrobot.functional.analyzer.save_to_file")
def test_analyze_statements(mock_save, mock_sec, mock_yf) -> None:
    mock_yf.get_income_stmt.return_value = pd.DataFrame({"test": [1]})
    mock_yf.get_balance_sheet.return_value = pd.DataFrame({"test": [1]})
    mock_yf.get_cash_flow.return_value = pd.DataFrame({"test": [1]})
    mock_sec.get_10k_section.return_value = "section text"

    # Test Income Stmt
    ReportAnalysisUtils.analyze_income_stmt("AAPL", "2023", "save_income.txt")
    mock_save.assert_called()

    # Test Balance Sheet
    ReportAnalysisUtils.analyze_balance_sheet("AAPL", "2023", "save_balance.txt")

    # Test Cash Flow
    ReportAnalysisUtils.analyze_cash_flow("AAPL", "2023", "save_cash.txt")

    # Test Segment Stmt
    ReportAnalysisUtils.analyze_segment_stmt("AAPL", "2023", "save_segment.txt")


@patch("finrobot.functional.analyzer.SECUtils")
@patch("finrobot.functional.analyzer.save_to_file")
def test_summarization_and_risks(mock_save, mock_sec) -> None:
    mock_sec.get_10k_section.return_value = "risk factors"

    ReportAnalysisUtils.income_summarization("AAPL", "2023", "income_analysis", "segment_analysis", "save_sum.txt")

    with patch("finrobot.functional.analyzer.YFinanceUtils") as mock_yf:
        mock_yf.get_stock_info.return_value = {"shortName": "Apple Inc."}
        ReportAnalysisUtils.get_risk_assessment("AAPL", "2023", "save_risk.txt")


@patch("finrobot.functional.analyzer.YFinanceUtils")
@patch("finrobot.functional.analyzer.FMPUtils")
def test_get_key_data(mock_fmp, mock_yf) -> None:
    # Mock stock data
    mock_yf.get_stock_data.return_value = pd.DataFrame(
        {"Close": [150.0], "High": [160.0], "Low": [140.0], "Volume": [10000000]}, index=[pd.Timestamp("2023-01-01")]
    )
    mock_yf.get_stock_info.return_value = {"currency": "USD"}
    mock_yf.get_analyst_recommendations.return_value = ("Buy", None)

    # Mock FMP data
    mock_fmp.get_target_price.return_value = 170.0
    mock_fmp.get_historical_market_cap.return_value = 2000000000000
    mock_fmp.get_historical_bvps.return_value = 5.0

    result = ReportAnalysisUtils.get_key_data("AAPL", "2023-01-01")
    assert result["Rating"] == "Buy"
    assert result["Closing Price (USD)"] == "150.00"


@patch("finrobot.functional.analyzer.FMPUtils")
@patch("finrobot.functional.analyzer.save_to_file")
def test_get_competitors_analysis(mock_save, mock_fmp) -> None:
    mock_fmp.get_competitor_financial_metrics.return_value = {
        "AAPL": pd.DataFrame({"2023": [1.0]}, index=["EBITDA Margin"]),
        "MSFT": pd.DataFrame({"2023": [0.9]}, index=["EBITDA Margin"]),
    }
    ReportAnalysisUtils.get_competitors_analysis("AAPL", ["MSFT"], "2023", "save_comp.txt")
    mock_save.assert_called()


@patch("finrobot.functional.analyzer.SECUtils")
@patch("finrobot.functional.analyzer.save_to_file")
def test_analyze_business_highlights(mock_save, mock_sec) -> None:
    mock_sec.get_10k_section.side_effect = ["Business Summary", "Management Discussion"]
    ReportAnalysisUtils.analyze_business_highlights("AAPL", "2023", "save_highlights.txt")
    mock_save.assert_called()


@patch("finrobot.functional.analyzer.YFinanceUtils")
@patch("finrobot.functional.analyzer.SECUtils")
@patch("finrobot.functional.analyzer.save_to_file")
def test_analyze_company_description(mock_save, mock_sec, mock_yf) -> None:
    mock_yf.get_stock_info.return_value = {"shortName": "Apple Inc."}
    mock_sec.get_10k_section.side_effect = ["Business Summary", "Management Discussion"]

    ReportAnalysisUtils.analyze_company_description("AAPL", "2023", "save_desc.txt")
    mock_save.assert_called()


@patch("finrobot.functional.analyzer.YFinanceUtils")
@patch("finrobot.functional.analyzer.FMPUtils")
def test_get_key_data_edge_cases(mock_fmp, mock_yf) -> None:
    # Test with string date and zero volume (or empty result logic if needed)
    # The code calculates mean of volume. If volume is 0, mean is 0.
    mock_yf.get_stock_data.return_value = pd.DataFrame(
        {"Close": [150.0], "High": [160.0], "Low": [140.0], "Volume": [0]}, index=[pd.Timestamp("2023-01-01")]
    )
    mock_yf.get_stock_info.return_value = {"currency": "USD"}
    mock_yf.get_analyst_recommendations.return_value = ("Buy", None)
    mock_fmp.get_target_price.return_value = 170.0
    mock_fmp.get_historical_market_cap.return_value = 2000000000000
    mock_fmp.get_historical_bvps.return_value = 5.0

    result = ReportAnalysisUtils.get_key_data("AAPL", "2023-01-01")
    assert result["6m avg daily vol (USDmn)"] == "0.00"
