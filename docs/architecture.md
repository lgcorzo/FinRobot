# FinRobot Architecture

FinRobot follows a **Domain-Driven Design (DDD)** architecture, organizing code into clear domain boundaries to ensure scalability, maintainability, and clear separation of concerns.

## Directory Structure

```
src/finrobot/
├── __init__.py
├── __main__.py
├── settings.py                     # Pydantic configuration & Global Settings
├── scripts.py                      # CLI entry points
│
├── core/                           # Shared Kernel & Domain Primitives
│   └── schemas.py                  # Validation schemas and common types
│
├── models/                         # Domain Layer (Core Business Logic)
│   └── agents/                     # AI Agents Implementation
│       ├── agent_library.py        # Agent Definitions
│       ├── workflow.py             # Agent Orchestration Workflows
│       └── tools/                  # Agent Tools
│
├── application/                    # Application Layer (Orchestration context)
│   ├── jobs/                       # Job definitions (e.g., AnalysisJob)
│   │   └── analysis.py
│   └── reporting/                  # Reporting logic
│       └── services/               # Reporting services (PDF generation)
│
├── infrastructure/                 # Infrastructure Layer (Technical capabilities)
│   ├── io/                         # Input/Output & Persistence
│   │   └── files.py                # File system operations
│   ├── services/                   # Infrastructure Services
│   │   ├── logger_service.py       # Logging
│   │   ├── alert_service.py        # Monitoring/Alerts
│   │   └── mlflow_service.py       # MLflow Integration
│   └── utils/                      # Cross-cutting utilities
│
├── data_access/                    # Interface Adapters / Data Infrastructure
│   └── data_source/                # External Data Connectors
│       ├── domains/
│       │   ├── market_data/        # Market Data Adapters (YFinance, FinnHub)
│       │   ├── filings/            # SEC Filings Adapters
│       │   ├── news/               # News Data Adapters
│       │   └── social/             # Social Media Adapters
│       └── ..._utils.py            # Utility helpers for data sources
│
├── evaluation/                     # Evaluation Domain
│   └── ...                         # Logic for evaluating agent performance
│
├── functional/                     # Functional Utilities (Legacy & Shared)
│   ├── charting.py                 # Charting utilities
│   ├── ragquery.py                 # RAG implementation utilities
│   └── ...
│
└── tools/                          # General Tools
```

## DDD Layers Explained

### 1. Domain Layer (`src/finrobot/models`, `src/finrobot/core`)

The heart of the system. It contains the business logic, entities, and rules that rely on nothing but themselves.

- **Agents**: complex entities capable of reasoning and executing tasks (`src/finrobot/models/agents`).
- **Core**: Shared schemas and basic types used across the system (`src/finrobot/core`).

### 2. Application Layer (`src/finrobot/application`)

Defines the jobs the software is supposed to do and directs the expressive domain objects to work out problems.

- **Jobs**: Encapsulate entire workflows like running a full financial analysis.
- **Reporting**: Orchestrates the creation of output artifacts (PDFs, reports) based on domain data.

### 3. Infrastructure Layer (`src/finrobot/infrastructure`, `src/finrobot/data_access`)

Provides generic technical capabilities that support the higher layers: message sending for the application, persistence for the domain, drawing widgets for the UI, etc.

- **Data Access**: Contains implementations for fetching data from external APIs (SEC, YFinance, FinnHub). In DDD terms, this implements the repositories defined in the domain (though strict repository interfaces might be implicit).
- **Services**: Logging, MLflow tracking, File I/O.

### 4. Interface/Presentation Layer

Currently represented by `scripts.py` (CLI), `tasks/` (Management Tasks), and notebooks (Demonstrations).

## Key Design Decisions

- **Separation of Concerns**: Data verification and fetching (`data_access`) is separated from the core logic of what to do with that data (`models` / `application`).
- **Dependency Rule**: Dependencies point inwards. `infrastructure` depends on `application` and `models`, but `models` should not depend on `infrastructure` details (typically achieved via interfaces/abstractions).
- **Agent Framework**: The project leverages Microsoft's Agent Framework, encapsulating agent behaviors within `models/agents`.
