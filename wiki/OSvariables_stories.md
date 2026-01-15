# OS Variables Stories

This document describes the environment variable management for FinRobot.

## Overview

The `Env` class provides a singleton interface for accessing environment variables used across the application.

## Location

```
src/finrobot/infrastructure/io/
└── osvariables.py           # Environment variable singleton
```

## Env Class

```python
from finrobot.infrastructure.io.osvariables import Env

env = Env()  # Singleton - same instance everywhere

# MLflow configuration
print(env.mlflow_tracking_uri)
print(env.mlflow_registry_uri)
print(env.mlflow_experiment_name)
print(env.mlflow_registered_model_name)

# AWS/S3 configuration
print(env.aws_access_key_id)
print(env.aws_secret_access_key)
print(env.mlflow_s3_endpoint_url)
print(env.mlflow_s3_ignore_tls)
```

## Required Environment Variables

### Core

| Variable                 | Purpose             |
| ------------------------ | ------------------- |
| `MLFLOW_TRACKING_URI`    | MLflow server URL   |
| `MLFLOW_EXPERIMENT_NAME` | Experiment name     |
| `LITELLM_API_KEY`        | LiteLLM gateway key |

### Data Sources

| Variable               | Purpose                 |
| ---------------------- | ----------------------- |
| `FINNHUB_API_KEY`      | Finnhub market data     |
| `FMP_API_KEY`          | Financial Modeling Prep |
| `SEC_API_KEY`          | SEC EDGAR API           |
| `REDDIT_CLIENT_ID`     | Reddit API client       |
| `REDDIT_CLIENT_SECRET` | Reddit API secret       |

### S3/MinIO

| Variable                 | Purpose               |
| ------------------------ | --------------------- |
| `AWS_ACCESS_KEY_ID`      | S3 access key         |
| `AWS_SECRET_ACCESS_KEY`  | S3 secret key         |
| `MLFLOW_S3_ENDPOINT_URL` | S3 endpoint           |
| `MLFLOW_S3_IGNORE_TLS`   | Skip TLS verification |

## .env File Example

```bash
# MLflow
MLFLOW_TRACKING_URI=http://mlflow.monitoring.svc.cluster.local:5000
MLFLOW_EXPERIMENT_NAME=fin_team_experiment

# Data Sources
FINNHUB_API_KEY=your_key
FMP_API_KEY=your_key
SEC_API_KEY=your_key

# S3
AWS_ACCESS_KEY_ID=minio_user
AWS_SECRET_ACCESS_KEY=minio_password
MLFLOW_S3_ENDPOINT_URL=https://minio.storage.svc.cluster.local:443
```
