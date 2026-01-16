import os
import tempfile
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from finrobot.application.reporting.services.pdf_service import ReportLabUtils
from PIL import Image


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


@patch("finrobot.application.reporting.services.pdf_service.YFinanceUtils")
@patch("finrobot.application.reporting.services.pdf_service.FMPUtils")
@patch("finrobot.application.reporting.services.pdf_service.ReportAnalysisUtils")
def test_pdf_service_build_report_success(mock_analyzer, mock_fmp, mock_yf, dummy_image) -> None:  # type: ignore[no-untyped-def]
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
