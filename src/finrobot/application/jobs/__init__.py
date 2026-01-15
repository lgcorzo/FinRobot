"""Application Jobs."""

from .base import Job
from .analysis import FinancialAnalysisJob

# %% TYPES

JobKind = FinancialAnalysisJob

# %% EXPORTS

__all__ = ["Job", "FinancialAnalysisJob", "JobKind"]
