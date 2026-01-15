# Reporting Stories

This document covers the PDF report generation capabilities in FinRobot.

## Overview

The reporting module handles the generation of professional equity research reports in PDF format. It uses ReportLab for PDF generation and integrates with the functional layer for financial data.

## Location

```
src/finrobot/application/reporting/
├── __init__.py
├── pdf_service.py       # PDF generation orchestration
├── entities.py          # Report domain entities
└── reportlab/
    └── reportlab.py     # ReportLab template implementation
```

## Key Components

### Report Entities

```python
from finrobot.application.reporting.entities import Report, Section

report = Report(
    title="AAPL Equity Research",
    sections=[
        Section(title="Executive Summary", content="..."),
        Section(title="Financial Analysis", content="..."),
    ]
)
```

### PDF Service

The `PDFService` orchestrates report generation:

```python
from finrobot.application.reporting import PDFService

service = PDFService()
pdf_bytes = service.generate(report)
service.save(pdf_bytes, "AAPL_report.pdf")
```

## Report Structure

A typical equity research report includes:

1. **Executive Summary**: Key findings and recommendations
2. **Company Overview**: Business description and segments
3. **Financial Analysis**: Income statement, balance sheet, cash flow
4. **Valuation Analysis**: DCF, peer comparison, multiples
5. **Risk Assessment**: Key risks and mitigants
6. **Investment Thesis**: Buy/Sell/Hold recommendation

## Integration with Agents

Agents can generate reports using the reporting tools:

```python
# Agent workflow for report generation
result = agent.run(
    f"Generate an equity research report for {company} based on the latest 10-K filing"
)
```
