from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Sequence

from .config import ReportConfig, load_config
from .data_models import Chart, Metric, ReportData, Summary, Table
from .renderer import export
from .summarizer import build_summary
from .templating import render_markdown


def load_tables(table_data: Sequence[Dict[str, Any]]) -> Sequence[Table]:
    tables = []
    for item in table_data:
        tables.append(
            Table(
                title=item["title"],
                headers=item["headers"],
                rows=item["rows"],
            )
        )
    return tables


def load_charts(chart_data: Sequence[Dict[str, Any]]) -> Sequence[Chart]:
    charts = []
    for item in chart_data:
        charts.append(
            Chart(
                title=item["title"],
                image_path=item["image_path"],
                description=item.get("description"),
            )
        )
    return charts


def parse_input(payload_path: Path) -> Dict[str, Any]:
    return json.loads(payload_path.read_text(encoding="utf-8"))


def build_report_data(payload: Dict[str, Any], config: ReportConfig) -> ReportData:
    metrics = [Metric(**metric) for metric in payload["summary"]["metrics"]]
    summary_text = build_summary(
        metrics=metrics,
        template_path=config.summary_template,
        enrich=config.template.enrich_summary_via_llm,
    )
    summary = Summary(metrics=metrics, narrative=summary_text)

    tables = load_tables(payload.get("tables", []))
    charts = load_charts(payload.get("charts", []))

    return ReportData(summary=summary, tables=tables, charts=charts)


def run(config_path: Path, data_path: Path) -> Path:
    config = load_config(config_path)
    payload = parse_input(data_path)
    report_data = build_report_data(payload, config)

    markdown_text = render_markdown(
        template_path=str(config.template.markdown_template),
        report_data=report_data,
        branding={
            "company_name": config.branding.company_name,
            "logo_path": str(config.branding.logo_path) if config.branding.logo_path else None,
            "primary_color": config.branding.primary_color,
            "secondary_color": config.branding.secondary_color,
        },
    )

    output_name = data_path.stem + "." + config.template.output_format
    destination = config.template.output_directory / output_name
    return export(markdown_text, config.template.output_format, destination)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render financial reports from structured data.")
    parser.add_argument("config", type=Path, help="Path to the YAML/JSON configuration file.")
    parser.add_argument("payload", type=Path, help="Path to the JSON payload containing report data.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    output_path = run(args.config, args.payload)
    print(f"Report generated at {output_path}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
