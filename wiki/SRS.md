# Software Requirements Specification (SRS)

## FinRobot - AI Agent Platform for Financial Analysis

**Version:** 1.0  
**Date:** January 2026  
**Status:** Approved

---

## 1. Introduction

### 1.1 Purpose

This document specifies the software requirements for FinRobot, an AI Agent Platform for Financial Analysis using Large Language Models. It defines functional and non-functional requirements for all system components.

### 1.2 Scope

FinRobot provides automated financial analysis capabilities including:

- SEC filing analysis
- Market data aggregation
- Financial statement analysis
- Equity research report generation
- Sentiment analysis from social media

### 1.3 System Overview

```mermaid
graph TB
    subgraph "External Systems"
        SEC[SEC EDGAR]
        FMP[Financial Modeling Prep]
        YF[Yahoo Finance]
        FH[Finnhub]
        RD[Reddit API]
        LLM[LiteLLM Gateway]
    end

    subgraph "FinRobot Platform"
        DA[Data Access Layer]
        FL[Functional Layer]
        ML[Models Layer]
        AL[Application Layer]
        IL[Infrastructure Layer]
    end

    subgraph "Outputs"
        PDF[PDF Reports]
        ML_FLOW[MLflow Artifacts]
        API[API Responses]
    end

    SEC --> DA
    FMP --> DA
    YF --> DA
    FH --> DA
    RD --> DA

    DA --> FL
    FL --> ML
    ML --> LLM
    ML --> AL

    AL --> PDF
    AL --> ML_FLOW
    AL --> API

    IL -.-> DA
    IL -.-> FL
    IL -.-> ML
    IL -.-> AL
```

---

## 2. Functional Requirements

### 2.1 Data Retrieval (FR-100)

#### FR-101: SEC Filing Retrieval

| ID              | FR-101                                                                             |
| --------------- | ---------------------------------------------------------------------------------- |
| **Name**        | SEC Filing Retrieval                                                               |
| **Priority**    | High                                                                               |
| **Description** | System shall retrieve SEC filings (10-K, 10-Q, 8-K, S-1) for any public US company |

**Execution Flow:**

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant SECAdapter
    participant SECAPI as SEC EDGAR API
    participant Cache

    User->>Agent: Request 10-K for AAPL
    Agent->>SECAdapter: get_filing("AAPL", "10-K")
    SECAdapter->>Cache: Check cache
    alt Cache Hit
        Cache-->>SECAdapter: Return cached filing
    else Cache Miss
        SECAdapter->>SECAPI: Fetch filing
        SECAPI-->>SECAdapter: Filing content
        SECAdapter->>Cache: Store in cache
    end
    SECAdapter-->>Agent: Parsed filing content
    Agent-->>User: Filing analysis
```

**Acceptance Criteria:**

- [ ] Retrieve filings by ticker symbol
- [ ] Support 10-K, 10-Q, 8-K, S-1 form types
- [ ] Extract specific sections (Risk Factors, MD&A, etc.)
- [ ] Handle rate limiting gracefully

---

#### FR-102: Market Data Retrieval

| ID              | FR-102                                                     |
| --------------- | ---------------------------------------------------------- |
| **Name**        | Market Data Retrieval                                      |
| **Priority**    | High                                                       |
| **Description** | System shall retrieve real-time and historical market data |

**Data Sources Interaction:**

```mermaid
graph LR
    subgraph "Market Data Adapters"
        FMP[FMP Adapter]
        YF[YFinance Adapter]
        FH[Finnhub Adapter]
    end

    subgraph "Data Types"
        FMP --> |Financials| FS[Financial Statements]
        FMP --> |Metrics| FM[Financial Metrics]
        YF --> |Historical| HP[Historical Prices]
        YF --> |Dividends| DIV[Dividends/Splits]
        FH --> |News| NEWS[Market News]
        FH --> |Ratings| RAT[Analyst Ratings]
    end
```

---

#### FR-103: Social Sentiment Retrieval

| ID              | FR-103                                                             |
| --------------- | ------------------------------------------------------------------ |
| **Name**        | Social Sentiment Retrieval                                         |
| **Priority**    | Medium                                                             |
| **Description** | System shall collect and analyze social media sentiment for stocks |

```mermaid
sequenceDiagram
    participant Agent
    participant RedditAdapter
    participant RedditAPI
    participant LLM

    Agent->>RedditAdapter: search_mentions("GME")
    RedditAdapter->>RedditAPI: Fetch posts from r/wallstreetbets
    RedditAPI-->>RedditAdapter: Posts & Comments
    RedditAdapter-->>Agent: Structured mentions
    Agent->>LLM: Analyze sentiment
    LLM-->>Agent: Sentiment scores
    Agent-->>Agent: Aggregate results
```

---

### 2.2 Analysis Functions (FR-200)

#### FR-201: Financial Statement Analysis

| ID              | FR-201                                                                 |
| --------------- | ---------------------------------------------------------------------- |
| **Name**        | Financial Statement Analysis                                           |
| **Priority**    | High                                                                   |
| **Description** | System shall analyze income statements, balance sheets, and cash flows |

**Analysis Pipeline:**

```mermaid
flowchart TD
    A[Input: Ticker Symbol] --> B{Fetch Data}
    B --> C[Income Statement]
    B --> D[Balance Sheet]
    B --> E[Cash Flow Statement]

    C --> F[Profitability Ratios]
    D --> G[Liquidity Ratios]
    D --> H[Solvency Ratios]
    E --> I[Cash Flow Metrics]

    F --> J[Analysis Summary]
    G --> J
    H --> J
    I --> J

    J --> K[LLM Interpretation]
    K --> L[Output: Analysis Report]
```

**Computed Metrics:**

| Category      | Metrics                                              |
| ------------- | ---------------------------------------------------- |
| Profitability | Gross Margin, Operating Margin, Net Margin, ROE, ROA |
| Liquidity     | Current Ratio, Quick Ratio, Cash Ratio               |
| Solvency      | Debt/Equity, Interest Coverage, Debt/EBITDA          |
| Valuation     | P/E, P/B, EV/EBITDA, PEG                             |

---

#### FR-202: Valuation Analysis

| ID              | FR-202                                                   |
| --------------- | -------------------------------------------------------- |
| **Name**        | Valuation Analysis                                       |
| **Priority**    | High                                                     |
| **Description** | System shall perform DCF and comparable company analysis |

```mermaid
flowchart LR
    subgraph "DCF Valuation"
        A[Free Cash Flow] --> B[Growth Projections]
        B --> C[Discount Rate]
        C --> D[Terminal Value]
        D --> E[Enterprise Value]
        E --> F[Equity Value per Share]
    end

    subgraph "Comparable Analysis"
        G[Peer Selection] --> H[Multiple Calculation]
        H --> I[Median Multiples]
        I --> J[Implied Valuation]
    end

    F --> K[Combined Valuation Range]
    J --> K
```

---

### 2.3 AI Agent Functions (FR-300)

#### FR-301: Agent Workflow Execution

| ID              | FR-301                                                             |
| --------------- | ------------------------------------------------------------------ |
| **Name**        | Agent Workflow Execution                                           |
| **Priority**    | High                                                               |
| **Description** | System shall execute multi-step analysis workflows using AI agents |

**Agent Execution Model:**

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Planning: Receive Task
    Planning --> ToolSelection: Analyze Task
    ToolSelection --> ToolExecution: Select Tool
    ToolExecution --> Reasoning: Get Result
    Reasoning --> ToolSelection: Need More Data
    Reasoning --> Synthesis: Data Complete
    Synthesis --> Response: Generate Output
    Response --> Idle: Complete

    ToolExecution --> ErrorHandling: Error
    ErrorHandling --> ToolSelection: Retry
    ErrorHandling --> Response: Max Retries
```

---

#### FR-302: Tool Invocation

| ID              | FR-302                                                                       |
| --------------- | ---------------------------------------------------------------------------- |
| **Name**        | Tool Invocation                                                              |
| **Priority**    | High                                                                         |
| **Description** | Agents shall invoke registered tools to access data and perform computations |

```mermaid
sequenceDiagram
    participant User
    participant Agent
    participant ToolRegistry
    participant Tool
    participant DataAdapter

    User->>Agent: "Analyze AAPL financials"
    Agent->>Agent: Parse intent
    Agent->>ToolRegistry: get_tool("get_financials")
    ToolRegistry-->>Agent: Tool reference
    Agent->>Tool: invoke(ticker="AAPL")
    Tool->>DataAdapter: fetch_data()
    DataAdapter-->>Tool: Raw data
    Tool-->>Agent: Structured result
    Agent->>Agent: Reason over result
    Agent-->>User: Analysis response
```

---

### 2.4 Report Generation (FR-400)

#### FR-401: PDF Report Generation

| ID              | FR-401                                                                   |
| --------------- | ------------------------------------------------------------------------ |
| **Name**        | PDF Report Generation                                                    |
| **Priority**    | High                                                                     |
| **Description** | System shall generate professional equity research reports in PDF format |

**Report Generation Flow:**

```mermaid
flowchart TD
    A[Analysis Complete] --> B[Report Entity Creation]
    B --> C[Section Assembly]

    C --> D[Executive Summary]
    C --> E[Company Overview]
    C --> F[Financial Analysis]
    C --> G[Valuation]
    C --> H[Risk Assessment]

    D --> I[PDF Service]
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J[ReportLab Renderer]
    J --> K[Embed Charts]
    K --> L[Final PDF]
    L --> M[Save to MLflow]
```

---

## 3. Non-Functional Requirements

### 3.1 Performance (NFR-100)

| ID      | Requirement       | Target                            |
| ------- | ----------------- | --------------------------------- |
| NFR-101 | API response time | < 5 seconds for data retrieval    |
| NFR-102 | Report generation | < 30 seconds for full report      |
| NFR-103 | Agent response    | < 60 seconds for complex analysis |

### 3.2 Reliability (NFR-200)

| ID      | Requirement    | Target                            |
| ------- | -------------- | --------------------------------- |
| NFR-201 | Service uptime | 99.5% availability                |
| NFR-202 | Data accuracy  | 99.9% accuracy for financial data |
| NFR-203 | Error recovery | Automatic retry with backoff      |

### 3.3 Security (NFR-300)

| ID      | Requirement     | Target                        |
| ------- | --------------- | ----------------------------- |
| NFR-301 | API key storage | Kubernetes Sealed Secrets     |
| NFR-302 | Data encryption | TLS 1.3 for all external APIs |
| NFR-303 | Access control  | Role-based access via OAuth2  |

### 3.4 Scalability (NFR-400)

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        LB[Load Balancer]

        subgraph "Pod Replicas"
            P1[FinRobot Pod 1]
            P2[FinRobot Pod 2]
            P3[FinRobot Pod N]
        end

        subgraph "Shared Services"
            ML[MLflow]
            MINIO[MinIO S3]
            KAFKA[Kafka]
        end
    end

    LB --> P1
    LB --> P2
    LB --> P3

    P1 --> ML
    P2 --> ML
    P3 --> ML

    P1 --> MINIO
    P2 --> MINIO
    P3 --> MINIO
```

---

## 4. Use Cases

### UC-001: Generate Equity Research Report

```mermaid
sequenceDiagram
    actor Analyst
    participant FinRobot
    participant SECAdapter
    participant FMPAdapter
    participant Agent
    participant PDFService
    participant MLflow

    Analyst->>FinRobot: Request report for AAPL
    FinRobot->>SECAdapter: Fetch 10-K filing
    SECAdapter-->>FinRobot: Filing content
    FinRobot->>FMPAdapter: Fetch financial data
    FMPAdapter-->>FinRobot: Financial metrics
    FinRobot->>Agent: Analyze and synthesize
    Agent-->>FinRobot: Analysis sections
    FinRobot->>PDFService: Generate report
    PDFService-->>FinRobot: PDF document
    FinRobot->>MLflow: Log artifact
    FinRobot-->>Analyst: Return report
```

### UC-002: Predict Stock Movement

```mermaid
sequenceDiagram
    actor Trader
    participant FinRobot
    participant FinnhubAdapter
    participant RedditAdapter
    participant Agent

    Trader->>FinRobot: Predict NVDA next week
    FinRobot->>FinnhubAdapter: Get recent news
    FinnhubAdapter-->>FinRobot: News articles
    FinRobot->>RedditAdapter: Get social sentiment
    RedditAdapter-->>FinRobot: Reddit mentions
    FinRobot->>Agent: Analyze sentiment & fundamentals
    Agent->>Agent: Financial CoT reasoning
    Agent-->>FinRobot: Prediction with rationale
    FinRobot-->>Trader: "Up 2-3% based on..."
```

---

## 5. Traceability Matrix

| Requirement | Component                           | Test Coverage          |
| ----------- | ----------------------------------- | ---------------------- |
| FR-101      | `sec_adapter.py`                    | `test_sec_adapter.py`  |
| FR-102      | `fmp_utils.py`, `yfinance_utils.py` | `test_fmp_utils.py`    |
| FR-103      | `reddit_utils.py`                   | `test_reddit_utils.py` |
| FR-201      | `analyzer.py`, `quantitative.py`    | `test_analyzer.py`     |
| FR-202      | `quantitative.py`                   | `test_quantitative.py` |
| FR-301      | `workflow.py`                       | `test_workflow.py`     |
| FR-302      | `registry.py`                       | `test_tools.py`        |
| FR-401      | `pdf_service.py`                    | `test_pdf_service.py`  |
