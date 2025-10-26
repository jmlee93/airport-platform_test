"""Configuration utilities for the spreadsheet analysis tooling."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class BatchConfig:
    """Configuration settings for the batch scheduler."""

    input_dir: Path
    state_dir: Path
    interval_minutes: int = 60

    def ensure_directories(self) -> None:
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)


@dataclass
class AnalysisConfig:
    """Top-level configuration for a single analysis run."""

    expected_sheets: List[str] = field(default_factory=list)
    report_dir: Path = Path("reports")
    log_dir: Path = Path("logs")
    batch: Optional[BatchConfig] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def ensure_directories(self) -> None:
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        if self.batch:
            self.batch.ensure_directories()


def _parse_batch_config(raw: Optional[dict]) -> Optional[BatchConfig]:
    if not raw:
        return None
    input_dir = Path(raw.get("input_dir", "batch_inputs"))
    state_dir = Path(raw.get("state_dir", "batch_state"))
    interval = int(raw.get("interval_minutes", 60))
    return BatchConfig(input_dir=input_dir, state_dir=state_dir, interval_minutes=interval)


def load_config(path: Optional[Path]) -> AnalysisConfig:
    """Load configuration from a YAML file.

    If ``path`` is ``None`` the default configuration is returned.
    """

    if path is None:
        return AnalysisConfig()

    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    config = AnalysisConfig(
        expected_sheets=list(data.get("expected_sheets", [])),
        report_dir=Path(data.get("report_dir", "reports")),
        log_dir=Path(data.get("log_dir", "logs")),
        batch=_parse_batch_config(data.get("batch")),
        metadata={str(k): str(v) for k, v in (data.get("metadata") or {}).items()},
    )
    config.ensure_directories()
    return config


__all__ = ["AnalysisConfig", "BatchConfig", "load_config"]
