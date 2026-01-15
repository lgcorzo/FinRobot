# Settings Stories

This document describes the Pydantic-based configuration management.

## Overview

FinRobot uses Pydantic Settings for type-safe configuration management, loading values from environment variables and `.env` files.

## Location

```
src/finrobot/
├── settings.py              # Main settings class
└── infrastructure/io/
    └── osvariables.py       # Environment variable definitions
```

## FinRobotSettings

The main settings class:

```python
from finrobot.settings import FinRobotSettings

settings = FinRobotSettings()

# Access configuration
print(settings.openai_model)
print(settings.mlflow_tracking_uri)
```

## Configuration Sources

Settings are loaded in priority order:

1. **Environment Variables**: `FINROBOT_OPENAI_MODEL=gpt-4`
2. **.env File**: Automatically loaded from project root
3. **Defaults**: Defined in the settings class

## Key Settings

| Setting                  | Environment Variable     | Default    |
| ------------------------ | ------------------------ | ---------- |
| `openai_model`           | `OPENAI_MODEL`           | `gpt-4`    |
| `mlflow_tracking_uri`    | `MLFLOW_TRACKING_URI`    | `./mlruns` |
| `mlflow_experiment_name` | `MLFLOW_EXPERIMENT_NAME` | `finrobot` |
| `litellm_api_key`        | `LITELLM_API_KEY`        | -          |

## Env Class

For infrastructure-level environment variables:

```python
from finrobot.infrastructure.io.osvariables import Env

env = Env()  # Singleton
print(env.mlflow_tracking_uri)
print(env.aws_access_key_id)
```

## Type Safety

All settings are validated at load time:

```python
class FinRobotSettings(BaseSettings):
    openai_model: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4096

    model_config = {"env_prefix": "FINROBOT_"}
```
