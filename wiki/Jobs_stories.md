# Jobs Stories

This document describes the Application Layer jobs that orchestrate high-level financial analysis workflows.

## Overview

Jobs in FinRobot coordinate the execution of financial analysis tasks. They manage the lifecycle of services (logging, MLflow, alerts) and delegate to domain objects for actual business logic.

## Location

```
src/finrobot/application/jobs/
├── __init__.py
├── base.py              # Base Job class with context manager
└── analysis.py          # Financial analysis job implementation
```

## Base Job

The `Job` base class provides:

- **Service Management**: Automatic start/stop of `LoggerService`, `AlertsService`, and `MlflowService`.
- **Context Manager**: Use with `with job:` syntax for clean resource management.
- **Frozen Model**: Pydantic-based immutable configuration.

```python
from finrobot.application.jobs import Job

class FinancialAnalysisJob(Job):
    KIND: str = "financial_analysis"
    company: str
    model: str

    def run(self) -> dict:
        # Analysis logic here
        return {"status": "complete"}
```

## Usage Pattern

```python
with FinancialAnalysisJob(company="AAPL", model="gpt-4") as job:
    result = job.run()
```

## Key Features

| Feature            | Description                                 |
| ------------------ | ------------------------------------------- |
| Auto-logging       | LoggerService started/stopped automatically |
| MLflow Integration | Experiments tracked via MlflowService       |
| Alerting           | Alerts sent via AlertsService on failures   |
| Type Safety        | Pydantic validation for all parameters      |
