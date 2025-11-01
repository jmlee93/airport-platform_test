from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .dependency import DependencyGraph
from .financial_rules import FormulaRuleRegistry, default_registry
from .models import FinancialMetric, SheetMetadata, WorkbookMetadata
from .parser import WorkbookParser


@dataclass
class AnalysisResult:
    """Container aggregating the outputs of the workbook analysis."""

    workbook: WorkbookMetadata
    dependency_graph: DependencyGraph
    financial_metrics: List[FinancialMetric]


class WorkbookAnalyzer:
    """High-level interface that orchestrates workbook analysis."""

    def __init__(self, rules: Optional[FormulaRuleRegistry] = None) -> None:
        self.rules = rules or default_registry()

    def analyze(self, path: Path | str) -> AnalysisResult:
        parser = WorkbookParser(Path(path))
        workbook_meta = parser.parse()
        graph = DependencyGraph.from_workbook(workbook_meta)
        metrics: List[FinancialMetric] = []
        for sheet_meta in workbook_meta.sheets.values():
            metrics.extend(self._collect_metrics(sheet_meta))
        return AnalysisResult(workbook=workbook_meta, dependency_graph=graph, financial_metrics=metrics)

    def _collect_metrics(self, sheet: SheetMetadata) -> List[FinancialMetric]:
        metrics: List[FinancialMetric] = []
        for cell in sheet.cells.values():
            if cell.formula:
                metrics.extend(self.rules.identify_metrics(sheet.name, cell.coordinate, cell.formula))
        return metrics
