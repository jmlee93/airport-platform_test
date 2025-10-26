"""Command line interface for the spreadsheet analysis toolkit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .analysis import analyze_workbook
from .batch import run_batch_scheduler
from .config import AnalysisConfig, load_config
from .logging_utils import configure_logging
from .report import write_report


def _add_common_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to a YAML configuration file.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        help="Optional path to write the JSON report.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging to the audit log.",
    )


def _load_config(path: Optional[Path]) -> AnalysisConfig:
    return load_config(path)


def _run_single_analysis(args: argparse.Namespace) -> int:
    if args.workbook is None:
        raise SystemExit("an Excel workbook path is required")

    config = _load_config(args.config)
    logger = configure_logging(config.log_dir, verbose=args.verbose)

    try:
        result = analyze_workbook(Path(args.workbook), config, audit_logger=logger)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Analysis failed: %s", exc)
        return 1

    report_path = write_report(result, args.report)

    summary = {
        "workbook": str(result.workbook),
        "generated_at": result.generated_at.isoformat(),
        "missing_sheets": result.missing_sheets,
        "issues": {
            sheet: metrics.issues for sheet, metrics in result.sheet_metrics.items() if metrics.issues
        },
        "report_path": str(report_path),
    }
    print(json.dumps(summary, indent=2))
    return 0


def _run_batch(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    logger = configure_logging(config.log_dir, verbose=args.verbose)
    if config.batch is None:
        raise SystemExit("Batch configuration is required to run the scheduler.")

    run_batch_scheduler(config, logger=logger, iterations=args.iterations)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze-model",
        description="Analyze Excel-based financial models and produce structured reports.",
    )
    parser.add_argument("workbook", nargs="?", help="Workbook to analyze (default command mode).")
    _add_common_arguments(parser)

    subparsers = parser.add_subparsers(dest="command")
    batch_parser = subparsers.add_parser(
        "batch", help="Run the batch scheduler defined in the configuration file."
    )
    _add_common_arguments(batch_parser)
    batch_parser.add_argument(
        "--iterations",
        type=int,
        default=0,
        help="Number of scheduler iterations to run (0 means infinite).",
    )

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "batch":
        return _run_batch(args)

    return _run_single_analysis(args)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    sys.exit(main())
