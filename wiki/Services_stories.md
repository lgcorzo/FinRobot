# Services Stories

This document describes the infrastructure services for logging, alerting, and MLflow integration.

## Overview

The services module provides cross-cutting infrastructure concerns used throughout the application.

## Location

```
src/finrobot/infrastructure/services/
├── __init__.py
├── logger_service.py    # Logging with Loguru
├── alert_service.py     # Alerting (email, Slack, etc.)
└── mlflow_service.py    # MLflow experiment tracking
```

## LoggerService

Provides structured logging via Loguru:

```python
from finrobot.infrastructure.services import LoggerService

logger_service = LoggerService()
logger_service.start()

logger = logger_service.logger()
logger.info("Starting analysis for {}", ticker)
logger.warning("Data incomplete for {}", symbol)
logger.error("Failed to fetch {}: {}", url, error)

logger_service.stop()
```

## AlertsService

Sends alerts on critical events:

```python
from finrobot.infrastructure.services import AlertsService

alerts = AlertsService()
alerts.start()

# Send alert
alerts.send_alert(
    severity="critical",
    message="Analysis job failed for AAPL",
    context={"error": str(e)}
)

alerts.stop()
```

## MlflowService

Manages MLflow experiment tracking:

```python
from finrobot.infrastructure.services import MlflowService

mlflow_service = MlflowService()
mlflow_service.start()

# Log parameters, metrics, artifacts
mlflow_service.log_param("ticker", "AAPL")
mlflow_service.log_metric("analysis_time", 12.5)
mlflow_service.log_artifact("report.pdf")

mlflow_service.stop()
```

## Environment Variables

```bash
MLFLOW_TRACKING_URI=http://mlflow.monitoring.svc.cluster.local:5000
MLFLOW_EXPERIMENT_NAME=fin_team_experiment
```
