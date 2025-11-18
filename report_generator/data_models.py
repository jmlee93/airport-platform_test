from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass
class Metric:
    name: str
    value: str
    delta: str | None = None


@dataclass
class Summary:
    metrics: Sequence[Metric]
    narrative: str


@dataclass
class Table:
    title: str
    headers: Sequence[str]
    rows: Sequence[Sequence[str]]


@dataclass
class Chart:
    title: str
    image_path: str
    description: str | None = None


@dataclass
class ReportData:
    summary: Summary
    tables: Sequence[Table] = field(default_factory=list)
    charts: Sequence[Chart] = field(default_factory=list)

    @property
    def has_tables(self) -> bool:
        return bool(self.tables)

    @property
    def has_charts(self) -> bool:
        return bool(self.charts)
