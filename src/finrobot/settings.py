from __future__ import annotations

from typing import Optional

import pydantic as pdt
import pydantic_settings as pdts

from finrobot.application import jobs
from finrobot.infrastructure.io.osvariables import Env

# %% SETTINGS


class Settings(pdts.BaseSettings, strict=True, frozen=True, extra="forbid"):
    """Base class for application settings."""


class FinRobotSettings(Settings):
    """Main settings of the FinRobot application."""

    # Core environment
    env: Env = Env()

    # OpenAI / LLM Configuration
    openai_api_key: Optional[str] = pdt.Field(default=None, description="OpenAI API Key")
    openai_model: str = pdt.Field(default="gpt-4", description="Model to use")

    # External API Keys (Finnhub, FMP, etc)
    finnhub_api_key: Optional[str] = pdt.Field(default=None)
    fmp_api_key: Optional[str] = pdt.Field(default=None)

    # Job/Task configuration
    work_dir: str = "coding"

    # Execution Job
    job: Optional[jobs.JobKind] = pdt.Field(default=None, discriminator="KIND")

    class Config:
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"
