"""Batch scheduler for recurring workbook analysis."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import List, Optional

from .analysis import AnalysisResult, analyze_workbook
from .config import AnalysisConfig


def _load_previous_state(path: Path) -> Optional[dict]:
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _save_state(path: Path, result: AnalysisResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(result.to_dict(), handle, indent=2)


def _compare_results(previous: Optional[dict], current: AnalysisResult) -> List[str]:
    messages: List[str] = []
    current_sheets = current.to_dict()["sheets"]
    previous_sheets = previous.get("sheets", {}) if previous else {}

    for sheet_name, metrics in current_sheets.items():
        if sheet_name not in previous_sheets:
            messages.append(f"New sheet detected: {sheet_name}")
            continue
        prev_metrics = previous_sheets[sheet_name]
        for field in ("formula_cells", "error_cells", "empty_cells"):
            current_value = metrics.get(field)
            previous_value = prev_metrics.get(field)
            if current_value != previous_value:
                messages.append(
                    f"{sheet_name}: {field} changed from {previous_value} to {current_value}"
                )
    for sheet_name in previous_sheets:
        if sheet_name not in current_sheets:
            messages.append(f"Sheet removed: {sheet_name}")
    return messages


def run_batch_scheduler(
    config: AnalysisConfig,
    logger,
    iterations: int = 0,
) -> None:
    """Run the batch scheduler.

    Parameters
    ----------
    config:
        Loaded application configuration containing a :class:`~analyze_model.config.BatchConfig`.
    logger:
        Audit logger used for feedback.
    iterations:
        Number of iterations to run. ``0`` means run indefinitely.
    """

    if config.batch is None:
        raise ValueError("Batch configuration missing")

    interval = max(1, config.batch.interval_minutes) * 60
    counter = 0

    while True:
        counter += 1
        logger.info("Batch iteration %d started", counter)

        for workbook_path in sorted(config.batch.input_dir.glob("*.xlsx")):
            logger.info("Processing %s", workbook_path)
            try:
                result = analyze_workbook(workbook_path, config, audit_logger=logger)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("Failed to analyze %s: %s", workbook_path, exc)
                continue

            state_path = config.batch.state_dir / f"{workbook_path.stem}.json"
            previous = _load_previous_state(state_path)
            deltas = _compare_results(previous, result)
            for message in deltas:
                logger.info("%s | %s", workbook_path.name, message)
            if not deltas:
                logger.info("%s | No material changes detected", workbook_path.name)

            if result.missing_sheets:
                for sheet in result.missing_sheets:
                    logger.error("%s | Missing expected sheet: %s", workbook_path.name, sheet)

            _save_state(state_path, result)

        logger.info("Batch iteration %d completed", counter)

        if iterations and counter >= iterations:
            break

        time.sleep(interval)


__all__ = ["run_batch_scheduler"]
