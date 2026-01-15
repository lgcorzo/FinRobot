"""Application Jobs."""

from .analysis import FinancialAnalysisJob
from .base import Job

# %% TYPES

JobKind = FinancialAnalysisJob

# %% EXPORTS

__all__ = ["Job", "FinancialAnalysisJob", "JobKind"]
