import os
import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from PIL import Image

from finrobot.functional.reportlab import ReportLabUtils


@pytest.fixture
def dummy_image() -> None:
    fd, path = tempfile.mkstemp(suffix=".png")
    try:
        with os.fdopen(fd, "wb") as tmp:
            img = Image.new("RGB", (100, 100), color="red")
            img.save(tmp, format="PNG")
        yield path
    finally:
        if os.path.exists(path):
            os.remove(path)


@patch("finrobot.functional.reportlab.YFinanceUtils")
@patch("finrobot.functional.reportlab.FMPUtils")
@patch("finrobot.functional.reportlab.ReportAnalysisUtils")
def test_build_annual_report_success(mock_analyzer, mock_fmp, mock_yf, dummy_image) -> None:  # type: ignore[no-untyped-def]
    mock_yf.get_stock_info.return_value = {"shortName": "Apple Inc.", "currency": "USD"}
    mock_fmp.get_financial_metrics.return_value = pd.DataFrame(
        {"Metric": ["Revenue", "Net Income"], "2023": [1000, 200], "2022": [900, 180]}
    ).set_index("Metric")
    mock_analyzer.get_key_data.return_value = {"Metric1": "Value1"}

    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "AAPL_Equity_Research_report.pdf")
        result = ReportLabUtils.build_annual_report(
            ticker_symbol="AAPL",
            save_path=save_path,
            operating_results="results",
            market_position="position",
            business_overview="overview",
            risk_assessment="risks",
            competitors_analysis="competitors",
            share_performance_image_path=dummy_image,
            pe_eps_performance_image_path=dummy_image,
            filing_date="2023-01-01",
        )
        assert "Annual report generated successfully." in result
        assert os.path.exists(save_path)


@patch("finrobot.functional.reportlab.YFinanceUtils")
def test_build_annual_report_failure(mock_yf) -> None:  # type: ignore[no-untyped-def]
    mock_yf.get_stock_info.side_effect = Exception("API Error")

    result = ReportLabUtils.build_annual_report(
        ticker_symbol="AAPL",
        save_path="/invalid/path/report.pdf",
        operating_results="results",
        market_position="position",
        business_overview="overview",
        risk_assessment="risks",
        competitors_analysis="competitors",
        share_performance_image_path="invalid.png",
        pe_eps_performance_image_path="invalid.png",
        filing_date="2023-01-01",
    )
    assert "Exception: API Error" in result or "Traceback" in result
