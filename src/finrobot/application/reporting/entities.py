"""Reporting Domain Entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Any


@dataclass
class Section:
    """Represents a report section."""

    title: str
    content: str
    section_type: str = "text"  # "text", "table", "chart", "key_metrics"
    order: int = 0


@dataclass
class Report:
    """Represents a complete report."""

    title: str
    symbol: str
    created_at: datetime
    sections: List[Section] = field(default_factory=list)
    author: Optional[str] = None
    summary: Optional[str] = None


@dataclass
class PDFDocument:
    """Represents a PDF document for generation."""

    filename: str
    report: Report
    template: Optional[str] = None
    output_path: Optional[str] = None
