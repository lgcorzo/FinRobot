# SEC Adapter Stories

This document describes the SEC filings data adapter for fetching and parsing EDGAR documents.

## Overview

The SEC Adapter connects to SEC EDGAR and third-party SEC APIs to retrieve company filings (10-K, 10-Q, 8-K, S-1) and extract structured content.

## Location

```
src/finrobot/data_access/data_source/
├── domains/filings/
│   └── sec_adapter.py       # DDD-style SEC adapter
├── filings_src/
│   ├── prepline_sec_filings/
│   │   ├── sec_document.py  # Document parsing
│   │   ├── fetch.py         # EDGAR fetching
│   │   └── sections.py      # Section definitions
│   ├── sec_filings.py       # SECExtractor class
│   └── sec_utils.py         # Utility functions
└── sec_utils.py             # Top-level utilities
```

## Key Components

### SECAdapter

The main adapter class for SEC data retrieval:

```python
from finrobot.data_access.data_source.domains.filings import SECAdapter

adapter = SECAdapter()

# Get filing metadata
filings = adapter.get_filings(ticker="AAPL", form_type="10-K", count=5)

# Download filing content
content = adapter.get_filing_content(accession_number="0000320193-23-000077")

# Extract specific section
section = adapter.get_section(
    ticker="AAPL",
    form_type="10-K",
    section="Risk Factors"
)
```

### SECExtractor

Lower-level extractor for pipeline operations:

```python
from finrobot.data_access.data_source.filings_src import SECExtractor

extractor = SECExtractor(ticker="AAPL")

# Get available filing years
years = extractor.get_filing_years()

# Extract and process filing
text, filing_type = extractor.pipeline_api(filing_text, m_section=["RISK_FACTORS"])
```

## Supported Filing Types

| Form Type | Description            |
| --------- | ---------------------- |
| 10-K      | Annual report          |
| 10-Q      | Quarterly report       |
| 8-K       | Current report         |
| S-1       | Registration statement |

## Environment Variables

```bash
SEC_API_KEY=your_sec_api_key
SEC_API_ORGANIZATION=your_org
SEC_API_EMAIL=your_email@example.com
```
