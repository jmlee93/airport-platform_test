from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .data_models import ReportData
from .references import ReferenceIndex


def create_environment(template_dir: str) -> Environment:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=("html", "xml", "md")),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["format_currency"] = lambda value: f"{value:,.2f}"
    return env


def render_markdown(template_path: str, report_data: ReportData, branding: Dict[str, Any]) -> str:
    env = create_environment(template_dir=str(Path(template_path).parent))
    template = env.get_template(Path(template_path).name)

    refs = ReferenceIndex()
    for table in report_data.tables:
        refs.register_table(table)
    for chart in report_data.charts:
        refs.register_figure(chart)

    context: Dict[str, Any] = {
        "report": report_data,
        "branding": branding,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "references": refs,
    }
    return template.render(**context)
