"""Utilities for analyzing spreadsheet-based models.

This package bundles the core business logic shared between the CLI,
Streamlit dashboard, and batch scheduler.
"""

from .config import AnalysisConfig, load_config
from .analysis import analyze_workbook, AnalysisResult, SheetMetrics
from .report import write_report

__all__ = [
    "AnalysisConfig",
    "AnalysisResult",
    "SheetMetrics",
    "analyze_workbook",
    "load_config",
    "write_report",
]
