# System Architecture (Domain-Driven Design)

FinRobot follows a **Domain-Driven Design (DDD)** architecture, ensuring code is modular, scalable, and easy to test. The application is divided into distinct layers and domains aligned with financial analysis workflows.

## High-Level Structure

```
src/finrobot/
├── __init__.py
├── __main__.py
├── settings.py                     # Pydantic configuration
├── scripts.py                      # CLI entry point
│
├── core/                           # Shared Kernel
│   └── schemas.py                  # Validation schemas
│
├── models/                         # Domain Layer
│   └── agents/                     # AI Agents (Microsoft Agent Framework)
│       ├── workflow.py             # Agent orchestration
│       ├── services/               # Prompt, Workflow services
│       └── tools/                  # Agent capabilities
│
├── application/                    # Application Layer
│   ├── jobs/                       # Orchestration jobs (AnalysisJob)
│   └── reporting/                  # Report generation (PDF service)
│
├── infrastructure/                 # Infrastructure Layer
│   ├── io/                         # File operations (files.py)
│   ├── services/                   # Logging, Alerting, MLflow
│   └── utils/                      # Decorators, helpers
│
├── data_access/                    # Data Access / Interface Adapters
│   └── data_source/                # External Data Connectors
│       ├── domains/                # DDD-style adapters
│       │   ├── filings/            # SEC Adapter
│       │   ├── market/             # YFinance, FMP, Finnhub
│       │   └── social/             # Reddit Adapter
│       ├── filings_src/            # SEC filing parsers
│       ├── earnings_calls_src/     # Earnings transcripts
│       └── marker_sec_src/         # PDF to Markdown conversion
│
├── functional/                     # Functional Utilities
│   ├── analyzer.py                 # Financial statement analysis
│   ├── charting.py                 # Data visualization
│   ├── quantitative.py             # Quantitative metrics
│   ├── rag.py                      # RAG pipeline
│   └── ragquery.py                 # RAG query interface
│
└── evaluation/                     # Evaluation Domain
    └── metrics.py                  # Analysis quality metrics
```

## Layers Description

### 1. Application Layer (`src/finrobot/application`)

Coordinates the application's activities without containing business logic.

- **Jobs** (`jobs/`): Defines high-level workflows like `FinancialAnalysisJob`, `ReportGenerationJob`.
- **Reporting** (`reporting/`): PDF generation services using ReportLab.

### 2. Domain Layer (`src/finrobot/models`)

Contains the core business logic and AI agent definitions.

- **Agents** (`models/agents/`):
  - `workflow.py`: Agent orchestration using Microsoft Agent Framework.
  - `services/`: Prompt templates and workflow services.
  - `tools/`: Callable tools for agents (data retrieval, analysis).

### 3. Functional Layer (`src/finrobot/functional`)

Provides financial analysis utilities shared across the application.

- **Analyzer**: Financial statement analysis (income, balance sheet, cash flow).
- **Charting**: Visualization of market data and metrics.
- **Quantitative**: Ratio analysis, DCF models, peer comparisons.
- **RAG**: Retrieval-Augmented Generation for earnings call analysis.

### 4. Data Access Layer (`src/finrobot/data_access`)

Handles data retrieval from external sources.

- **SEC Adapter**: Fetch SEC filings (10-K, 10-Q, S-1) via `sec-api`.
- **FMP Adapter**: Financial Modeling Prep API for market data.
- **YFinance Adapter**: Yahoo Finance historical data.
- **Finnhub Adapter**: Real-time market news and sentiment.
- **Reddit Adapter**: Social sentiment from financial subreddits.

### 5. Infrastructure Layer (`src/finrobot/infrastructure`)

Technical concerns and cross-cutting services.

- **Services**: `LoggerService`, `AlertsService`, `MlflowService`.
- **IO**: File operations and path management.
- **Utils**: Decorators, helpers, and shared utilities.

## Dependency Rule

Dependencies point **inwards** towards the Domain layer:

```
[Presentation] → [Application] → [Domain] ← [Infrastructure]
                                    ↑
                              [Data Access]
```

Infrastructure and Data Access depend on Domain abstractions, not concrete implementations.

## Key Technologies

| Component           | Technology                              |
| ------------------- | --------------------------------------- |
| Agent Framework     | Microsoft Agent Framework               |
| LLM Gateway         | LiteLLM                                 |
| Experiment Tracking | MLflow                                  |
| Configuration       | Pydantic Settings                       |
| PDF Generation      | ReportLab                               |
| Data Sources        | SEC API, FMP, YFinance, Finnhub, Reddit |
