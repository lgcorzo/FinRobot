"""Analysis Domain Entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd


@dataclass
class AnalysisResult:
    """Represents analysis output."""

    symbol: str
    analysis_type: str  # "technical", "fundamental", "sentiment"
    timestamp: datetime
    metrics: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None


@dataclass
class ChartData:
    """Represents chart data for visualization."""

    symbol: str
    data: pd.DataFrame
    chart_type: str  # "candlestick", "line", "bar"
    title: Optional[str] = None
    annotations: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class QuantitativeMetrics:
    """Represents quantitative analysis metrics."""

    symbol: str
    period: str
    returns: Optional[float] = None
    volatility: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    extra: Dict[str, Any] = field(default_factory=dict)
