from datetime import datetime

from finrobot.application.reporting.entities import PDFDocument, Report, Section


def test_section_creation() -> None:
    section = Section(title="Business Overview", content="Overview content", section_type="text", order=1)
    assert section.title == "Business Overview"
    assert section.content == "Overview content"
    assert section.section_type == "text"
    assert section.order == 1


def test_report_creation() -> None:
    now = datetime.now()
    section = Section(title="Test Section", content="Test Content")
    report = Report(
        title="Annual Report", symbol="AAPL", created_at=now, sections=[section], author="FinRobot", summary="Summary"
    )
    assert report.title == "Annual Report"
    assert report.symbol == "AAPL"
    assert report.created_at == now
    assert len(report.sections) == 1
    assert report.author == "FinRobot"
    assert report.summary == "Summary"


def test_pdf_document_creation() -> None:
    now = datetime.now()
    report = Report(title="Test Report", symbol="TSLA", created_at=now)
    pdf = PDFDocument(filename="tsla_report.pdf", report=report, template="standard", output_path="/tmp/")
    assert pdf.filename == "tsla_report.pdf"
    assert pdf.report == report
    assert pdf.template == "standard"
    assert pdf.output_path == "/tmp/"
