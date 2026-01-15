# System Architecture Review (SAR)

## FinRobot - AI Agent Platform for Financial Analysis

**Version:** 1.0  
**Date:** January 2026  
**Status:** Approved

---

## 1. Executive Summary

This document provides a comprehensive architectural review of FinRobot, detailing the system's structure, component interactions, deployment model, and design decisions.

---

## 2. System Context

### 2.1 Context Diagram

```mermaid
C4Context
    title System Context Diagram - FinRobot

    Person(analyst, "Financial Analyst", "Uses FinRobot for equity research")
    Person(trader, "Trader", "Uses predictions for trading decisions")

    System(finrobot, "FinRobot Platform", "AI-powered financial analysis platform")

    System_Ext(sec, "SEC EDGAR", "SEC filing database")
    System_Ext(fmp, "Financial Modeling Prep", "Financial data API")
    System_Ext(yf, "Yahoo Finance", "Historical price data")
    System_Ext(fh, "Finnhub", "Market news & sentiment")
    System_Ext(reddit, "Reddit", "Social sentiment data")
    System_Ext(litellm, "LiteLLM Gateway", "LLM API gateway")
    System_Ext(mlflow, "MLflow", "Experiment tracking")

    Rel(analyst, finrobot, "Requests analysis", "CLI/API")
    Rel(trader, finrobot, "Requests predictions", "CLI/API")

    Rel(finrobot, sec, "Fetches filings", "HTTPS")
    Rel(finrobot, fmp, "Fetches financials", "HTTPS")
    Rel(finrobot, yf, "Fetches prices", "HTTPS")
    Rel(finrobot, fh, "Fetches news", "HTTPS")
    Rel(finrobot, reddit, "Fetches posts", "HTTPS")
    Rel(finrobot, litellm, "LLM inference", "HTTPS")
    Rel(finrobot, mlflow, "Logs experiments", "HTTPS")
```

---

## 3. Container Architecture

### 3.1 Container Diagram

```mermaid
graph TB
    subgraph "FinRobot Platform"
        subgraph "Application Containers"
            CLI[CLI Entry Point<br/>scripts.py]
            JOBS[Job Orchestrator<br/>application/jobs/]
            REPORT[Report Generator<br/>application/reporting/]
        end

        subgraph "Domain Containers"
            AGENTS[AI Agents<br/>models/agents/]
            TOOLS[Agent Tools<br/>models/agents/tools/]
            WORKFLOW[Workflow Engine<br/>models/agents/workflow.py]
        end

        subgraph "Functional Containers"
            ANALYZER[Financial Analyzer<br/>functional/analyzer.py]
            QUANT[Quantitative Module<br/>functional/quantitative.py]
            RAG[RAG Pipeline<br/>functional/rag.py]
            CHART[Charting Module<br/>functional/charting.py]
        end

        subgraph "Data Access Containers"
            SEC[SEC Adapter]
            FMP[FMP Adapter]
            YF[YFinance Adapter]
            FH[Finnhub Adapter]
            REDDIT[Reddit Adapter]
        end

        subgraph "Infrastructure Containers"
            LOGGER[Logger Service]
            ALERTS[Alerts Service]
            MLFLOW_SVC[MLflow Service]
            ENV[Environment Config]
        end
    end

    CLI --> JOBS
    JOBS --> AGENTS
    JOBS --> REPORT

    AGENTS --> TOOLS
    AGENTS --> WORKFLOW

    TOOLS --> ANALYZER
    TOOLS --> QUANT
    TOOLS --> RAG
    TOOLS --> CHART

    ANALYZER --> SEC
    ANALYZER --> FMP
    QUANT --> FMP
    RAG --> SEC
    CHART --> YF

    JOBS --> LOGGER
    JOBS --> ALERTS
    JOBS --> MLFLOW_SVC
```

---

## 4. Component Architecture

### 4.1 Domain Layer Components

```mermaid
classDiagram
    class Agent {
        <<interface>>
        +name: str
        +llm_config: dict
        +run(task: str) Response
        +chat(message: str) Response
    }

    class FinRobot {
        +name: str
        +tools: List~Tool~
        +run(task: str) Response
    }

    class SingleAssistant {
        +human_input_mode: str
        +chat(message: str) Response
    }

    class SingleAssistantRAG {
        +documents: List~Document~
        +vector_store: VectorStore
        +query(question: str) Response
    }

    class Tool {
        <<interface>>
        +name: str
        +description: str
        +invoke(**kwargs) dict
    }

    class WorkflowService {
        +agent: Agent
        +execute(task: str) Response
    }

    Agent <|-- FinRobot
    Agent <|-- SingleAssistant
    SingleAssistant <|-- SingleAssistantRAG

    FinRobot --> Tool : uses
    WorkflowService --> Agent : orchestrates
```

### 4.2 Data Access Layer Components

```mermaid
classDiagram
    class DataAdapter {
        <<interface>>
        +fetch(params: dict) DataFrame
    }

    class SECAdapter {
        +get_filings(ticker, form_type) List
        +get_section(ticker, section) str
        +download_filing(accession) bytes
    }

    class FMPAdapter {
        +get_company_profile(ticker) dict
        +get_financials(ticker, type) DataFrame
        +get_metrics(ticker) dict
    }

    class YFinanceAdapter {
        +get_historical_prices(ticker, period) DataFrame
        +get_company_info(ticker) dict
    }

    class FinnhubAdapter {
        +get_news(ticker, from_date, to_date) List
        +get_recommendations(ticker) List
    }

    class RedditAdapter {
        +search_mentions(ticker, subreddits) List
        +get_post_comments(post_id) List
    }

    DataAdapter <|-- SECAdapter
    DataAdapter <|-- FMPAdapter
    DataAdapter <|-- YFinanceAdapter
    DataAdapter <|-- FinnhubAdapter
    DataAdapter <|-- RedditAdapter
```

### 4.3 Application Layer Components

```mermaid
classDiagram
    class Job {
        <<abstract>>
        +KIND: str
        +logger_service: LoggerService
        +alerts_service: AlertsService
        +mlflow_service: MlflowService
        +__enter__() Self
        +__exit__() bool
        +run() dict
    }

    class FinancialAnalysisJob {
        +company: str
        +model: str
        +run() dict
    }

    class ReportGenerationJob {
        +ticker: str
        +output_path: str
        +run() dict
    }

    class PDFService {
        +generate(report: Report) bytes
        +save(content: bytes, path: str) None
    }

    class Report {
        +title: str
        +sections: List~Section~
        +charts: List~Path~
    }

    Job <|-- FinancialAnalysisJob
    Job <|-- ReportGenerationJob

    ReportGenerationJob --> PDFService : uses
    PDFService --> Report : renders
```

---

## 5. Interaction Diagrams

### 5.1 Full Analysis Workflow

```mermaid
sequenceDiagram
    participant User
    participant CLI as CLI (scripts.py)
    participant Job as AnalysisJob
    participant Logger as LoggerService
    participant MLflow as MlflowService
    participant Agent as FinRobot Agent
    participant Tools as Tool Registry
    participant SEC as SECAdapter
    participant FMP as FMPAdapter
    participant LLM as LiteLLM
    participant PDF as PDFService

    User->>CLI: finrobot --task analyze --company AAPL
    CLI->>Job: create AnalysisJob(company="AAPL")

    rect rgb(200, 220, 255)
        Note over Job,MLflow: Context Manager Entry
        Job->>Logger: start()
        Job->>MLflow: start()
        MLflow->>MLflow: create_experiment()
    end

    Job->>Agent: run("Analyze AAPL")

    rect rgb(220, 255, 220)
        Note over Agent,LLM: Agent Reasoning Loop
        Agent->>LLM: Plan analysis steps
        LLM-->>Agent: Step 1: Get 10-K filing

        Agent->>Tools: invoke("get_sec_filing")
        Tools->>SEC: get_filing("AAPL", "10-K")
        SEC-->>Tools: Filing content
        Tools-->>Agent: Parsed filing

        Agent->>LLM: Analyze filing content
        LLM-->>Agent: Step 2: Get financials

        Agent->>Tools: invoke("get_financials")
        Tools->>FMP: get_income_statement("AAPL")
        FMP-->>Tools: Financial data
        Tools-->>Agent: Structured financials

        Agent->>LLM: Generate analysis
        LLM-->>Agent: Analysis sections
    end

    Agent-->>Job: Analysis result

    Job->>PDF: generate(analysis_result)
    PDF-->>Job: PDF bytes

    Job->>MLflow: log_artifact("report.pdf")

    rect rgb(255, 220, 220)
        Note over Job,MLflow: Context Manager Exit
        Job->>MLflow: stop()
        Job->>Logger: stop()
    end

    Job-->>CLI: {"status": "complete"}
    CLI-->>User: Report generated: report.pdf
```

### 5.2 RAG Query Workflow

```mermaid
sequenceDiagram
    participant User
    participant Agent as RAG Agent
    participant RAG as RAG Pipeline
    participant Embeddings as Embedding Model
    participant VectorStore as Vector Store
    participant LLM as LiteLLM

    User->>Agent: "What did CEO say about AI strategy?"

    Agent->>RAG: query(question, documents=earnings_calls)

    rect rgb(255, 245, 200)
        Note over RAG,VectorStore: Retrieval Phase
        RAG->>Embeddings: embed(question)
        Embeddings-->>RAG: Question embedding
        RAG->>VectorStore: similarity_search(embedding, k=5)
        VectorStore-->>RAG: Top 5 relevant chunks
    end

    rect rgb(200, 255, 245)
        Note over RAG,LLM: Generation Phase
        RAG->>RAG: Build context from chunks
        RAG->>LLM: generate(question + context)
        LLM-->>RAG: Generated answer
    end

    RAG-->>Agent: Answer with sources
    Agent-->>User: "The CEO mentioned three AI initiatives..."
```

### 5.3 Multi-Agent Collaboration (Future)

```mermaid
sequenceDiagram
    participant User
    participant Director as Director Agent
    participant Researcher as Research Agent
    participant Analyst as Analysis Agent
    participant Writer as Report Writer

    User->>Director: Complex analysis request

    Director->>Director: Decompose task

    par Parallel Research
        Director->>Researcher: Gather SEC filings
        Director->>Researcher: Gather market data
        Director->>Researcher: Gather news
    end

    Researcher-->>Director: Research complete

    Director->>Analyst: Analyze data
    Analyst->>Analyst: Financial analysis
    Analyst->>Analyst: Valuation
    Analyst->>Analyst: Risk assessment
    Analyst-->>Director: Analysis complete

    Director->>Writer: Generate report
    Writer->>Writer: Synthesize findings
    Writer->>Writer: Format PDF
    Writer-->>Director: Report complete

    Director-->>User: Final deliverable
```

---

## 6. Deployment Architecture

### 6.1 Kubernetes Deployment

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "llm-apps Namespace"
            DEPLOY[FinRobot Deployment]
            SVC[ClusterIP Service]
            SECRET[Sealed Secrets]
            CM[ConfigMap]
        end

        subgraph "monitoring Namespace"
            MLFLOW[MLflow Server]
        end

        subgraph "storage Namespace"
            MINIO[MinIO S3]
        end

        subgraph "orchestrators Namespace"
            KAFKA[Kafka Cluster]
        end
    end

    subgraph "External"
        INGRESS[Ingress Controller]
        CERT[Cert Manager]
    end

    INGRESS --> SVC
    SVC --> DEPLOY
    DEPLOY --> SECRET
    DEPLOY --> CM
    DEPLOY --> MLFLOW
    DEPLOY --> MINIO
    DEPLOY --> KAFKA
```

### 6.2 Pod Specification

```mermaid
graph LR
    subgraph "FinRobot Pod"
        CONTAINER[finrobot container<br/>python:3.12]

        subgraph "Volumes"
            SECRET_VOL[sealed-secrets volume]
            CONFIG_VOL[configmap volume]
        end

        subgraph "Environment"
            ENV1[MLFLOW_TRACKING_URI]
            ENV2[LITELLM_API_KEY]
            ENV3[SEC_API_KEY]
            ENV4[FMP_API_KEY]
        end
    end

    SECRET_VOL --> CONTAINER
    CONFIG_VOL --> CONTAINER
    ENV1 --> CONTAINER
    ENV2 --> CONTAINER
    ENV3 --> CONTAINER
    ENV4 --> CONTAINER
```

---

## 7. Data Flow Architecture

### 7.1 Data Flow Diagram

```mermaid
flowchart TD
    subgraph "External Data Sources"
        SEC_API[SEC EDGAR]
        FMP_API[Financial Modeling Prep]
        YF_API[Yahoo Finance]
        FH_API[Finnhub]
        RD_API[Reddit]
    end

    subgraph "Data Ingestion"
        SEC_ADAPTER[SEC Adapter]
        FMP_ADAPTER[FMP Adapter]
        YF_ADAPTER[YFinance Adapter]
        FH_ADAPTER[Finnhub Adapter]
        RD_ADAPTER[Reddit Adapter]
    end

    subgraph "Data Processing"
        PARSER[Document Parser]
        NORMALIZER[Data Normalizer]
        CACHE[Cache Layer]
    end

    subgraph "Analysis Engine"
        ANALYZER[Financial Analyzer]
        QUANT[Quantitative Engine]
        RAG[RAG Pipeline]
        LLM[LLM Inference]
    end

    subgraph "Output Generation"
        REPORT[Report Generator]
        CHART[Chart Generator]
        API_RESP[API Response]
    end

    subgraph "Persistence"
        MLFLOW_STORE[MLflow Artifacts]
        S3[MinIO S3]
    end

    SEC_API --> SEC_ADAPTER
    FMP_API --> FMP_ADAPTER
    YF_API --> YF_ADAPTER
    FH_API --> FH_ADAPTER
    RD_API --> RD_ADAPTER

    SEC_ADAPTER --> PARSER
    FMP_ADAPTER --> NORMALIZER
    YF_ADAPTER --> NORMALIZER
    FH_ADAPTER --> NORMALIZER
    RD_ADAPTER --> NORMALIZER

    PARSER --> CACHE
    NORMALIZER --> CACHE

    CACHE --> ANALYZER
    CACHE --> QUANT
    CACHE --> RAG

    ANALYZER --> LLM
    QUANT --> LLM
    RAG --> LLM

    LLM --> REPORT
    LLM --> CHART
    LLM --> API_RESP

    REPORT --> MLFLOW_STORE
    CHART --> MLFLOW_STORE
    MLFLOW_STORE --> S3
```

---

## 8. Security Architecture

### 8.1 Secrets Management

```mermaid
flowchart LR
    subgraph "Development"
        ENV_FILE[.env file]
    end

    subgraph "CI/CD"
        GH_SECRETS[GitHub Secrets]
    end

    subgraph "Kubernetes"
        KUBESEAL[kubeseal CLI]
        SEALED[SealedSecret]
        K8S_SECRET[Kubernetes Secret]
        POD[FinRobot Pod]
    end

    ENV_FILE -->|local dev| POD
    GH_SECRETS -->|CI pipeline| KUBESEAL
    KUBESEAL -->|encrypt| SEALED
    SEALED -->|Sealed Secrets Controller| K8S_SECRET
    K8S_SECRET -->|mount| POD
```

### 8.2 API Authentication Flow

```mermaid
sequenceDiagram
    participant Client
    participant Ingress as Ingress + OAuth2 Proxy
    participant Keycloak
    participant FinRobot

    Client->>Ingress: Request /api/analyze
    Ingress->>Ingress: Check auth cookie

    alt No valid session
        Ingress->>Client: Redirect to /oauth2/start
        Client->>Keycloak: Login page
        Keycloak-->>Client: Auth code
        Client->>Ingress: Callback with code
        Ingress->>Keycloak: Exchange code for token
        Keycloak-->>Ingress: Access token
        Ingress->>Client: Set auth cookie
    end

    Ingress->>FinRobot: Forward request with user info
    FinRobot-->>Ingress: Analysis result
    Ingress-->>Client: Response
```

---

## 9. Technology Stack

| Layer                   | Technology                | Purpose                      |
| ----------------------- | ------------------------- | ---------------------------- |
| **Runtime**             | Python 3.12               | Core language                |
| **Agent Framework**     | Microsoft Agent Framework | AI agent orchestration       |
| **LLM Gateway**         | LiteLLM                   | Multi-provider LLM routing   |
| **Configuration**       | Pydantic Settings         | Type-safe config             |
| **Experiment Tracking** | MLflow                    | Model versioning, artifacts  |
| **PDF Generation**      | ReportLab                 | Professional reports         |
| **Charting**            | Matplotlib, mplfinance    | Financial visualizations     |
| **Testing**             | pytest, coverage          | 94%+ test coverage           |
| **Container**           | Docker, Kubernetes        | Deployment                   |
| **Secrets**             | Bitnami Sealed Secrets    | Secure credential management |
| **Storage**             | MinIO S3                  | Artifact storage             |

---

## 10. Design Decisions

### DD-001: DDD Architecture

**Decision:** Adopt Domain-Driven Design with clear layer separation.

**Rationale:**

- Clear boundaries between business logic and infrastructure
- Easier testing with dependency inversion
- Scalable team organization

### DD-002: Microsoft Agent Framework

**Decision:** Migrate from AutoGen to Microsoft Agent Framework.

**Rationale:**

- Better type safety and Pydantic integration
- Cleaner async patterns
- More flexible tool registration

### DD-003: Sealed Secrets for Kubernetes

**Decision:** Use Bitnami Sealed Secrets instead of plain Kubernetes Secrets.

**Rationale:**

- Secrets can be safely committed to Git
- Encryption at rest with cluster-specific keys
- GitOps-compatible workflow
