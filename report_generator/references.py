from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from .data_models import Chart, Table


@dataclass
class ReferenceIndex:
    """Assigns sequential references for tables and figures."""

    table_counter: int = 0
    figure_counter: int = 0
    table_refs: Dict[str, str] = field(default_factory=dict)
    figure_refs: Dict[str, str] = field(default_factory=dict)

    def register_table(self, table: Table) -> str:
        self.table_counter += 1
        reference = f"Table {self.table_counter}"
        self.table_refs[table.title] = reference
        return reference

    def register_figure(self, chart: Chart) -> str:
        self.figure_counter += 1
        reference = f"Figure {self.figure_counter}"
        self.figure_refs[chart.title] = reference
        return reference

    def get_table_reference(self, title: str) -> str:
        return self.table_refs[title]

    def get_figure_reference(self, title: str) -> str:
        return self.figure_refs[title]
