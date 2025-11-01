from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass
class CellMetadata:
    """Metadata captured for a single cell within a worksheet."""

    sheet: str
    coordinate: str
    value: Any
    formula: Optional[str]
    dependencies: List[str] = field(default_factory=list)
    is_input: bool = True

    @property
    def id(self) -> str:
        """Return a workbook-unique identifier for the cell."""

        return f"{self.sheet}!{self.coordinate}"


@dataclass
class TableMetadata:
    """Structured information about an Excel table or tabular range."""

    sheet: str
    name: Optional[str]
    ref: str
    dataframe: "pd.DataFrame"
    has_merged_cells: bool


@dataclass
class SheetMetadata:
    """Metadata captured for an Excel worksheet."""

    name: str
    cells: Dict[str, CellMetadata] = field(default_factory=dict)
    tables: List[TableMetadata] = field(default_factory=list)
    merged_cells: List[str] = field(default_factory=list)


@dataclass
class NamedRangeMetadata:
    """Metadata captured for workbook-level named ranges."""

    name: str
    targets: List[str]


@dataclass
class WorkbookMetadata:
    """Top-level metadata for the Excel workbook."""

    path: str
    sheets: Dict[str, SheetMetadata]
    named_ranges: List[NamedRangeMetadata]


@dataclass
class FinancialMetric:
    """Represents a financial metric extracted from a formula."""

    sheet: str
    coordinate: str
    formula: str
    metric: str
    details: Dict[str, Any] = field(default_factory=dict)
