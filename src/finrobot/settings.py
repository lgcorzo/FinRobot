"""Define settings for the FinRobot application."""

# %% IMPORTS

import pydantic as pdt
import pydantic_settings as pdts
from typing import Optional

# %% SETTINGS


class Settings(pdts.BaseSettings, strict=True, frozen=True, extra="forbid"):
    """Base class for application settings."""


class FinRobotSettings(Settings):
    """Main settings of the FinRobot application."""

    # OpenAI / LLM Configuration
    openai_api_key: Optional[str] = pdt.Field(default=None, description="OpenAI API Key")
    openai_model: str = pdt.Field(default="gpt-4", description="Model to use")

    # External API Keys (Finnhub, FMP, etc)
    finnhub_api_key: Optional[str] = pdt.Field(default=None)
    fmp_api_key: Optional[str] = pdt.Field(default=None)

    # Job/Task configuration
    work_dir: str = "coding"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
