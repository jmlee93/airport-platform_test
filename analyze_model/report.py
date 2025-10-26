"""Report generation utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .analysis import AnalysisResult


def write_report(result: AnalysisResult, output_path: Optional[Path] = None) -> Path:
    """Persist the analysis result to disk as JSON."""

    if output_path is None:
        output_dir = Path("reports")
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"analysis_{result.workbook.stem}.json"
        output_path = output_dir / filename

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2)

    return output_path


__all__ = ["write_report"]
