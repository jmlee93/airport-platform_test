from __future__ import annotations

import json
import pathlib
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import yaml


@dataclass
class Branding:
    """Branding configuration for the exported reports."""

    company_name: str = "Example Corp"
    logo_path: Optional[pathlib.Path] = None
    primary_color: str = "#003366"
    secondary_color: str = "#4F81BD"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Branding":
        return cls(
            company_name=data.get("company_name", cls.company_name),
            logo_path=pathlib.Path(data["logo_path"]) if data.get("logo_path") else None,
            primary_color=data.get("primary_color", cls.primary_color),
            secondary_color=data.get("secondary_color", cls.secondary_color),
        )


@dataclass
class TemplateOptions:
    """Template selection and output configuration."""

    markdown_template: pathlib.Path
    output_format: str = "pdf"
    enrich_summary_via_llm: bool = False
    output_directory: pathlib.Path = pathlib.Path("output")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateOptions":
        template_path = pathlib.Path(data.get("markdown_template", "templates/report.md.j2"))
        output_format = data.get("output_format", cls.output_format)
        enrich_summary_via_llm = bool(data.get("enrich_summary_via_llm", False))
        output_directory = pathlib.Path(data.get("output_directory", cls.output_directory))
        return cls(
            markdown_template=template_path,
            output_format=output_format,
            enrich_summary_via_llm=enrich_summary_via_llm,
            output_directory=output_directory,
        )


@dataclass
class ReportConfig:
    """Top level configuration container."""

    branding: Branding = field(default_factory=Branding)
    template: TemplateOptions = field(
        default_factory=lambda: TemplateOptions(markdown_template=pathlib.Path("templates/report.md.j2"))
    )
    summary_template: pathlib.Path = pathlib.Path("templates/summary_template.txt")

    @classmethod
    def from_mapping(cls, data: Dict[str, Any]) -> "ReportConfig":
        branding = Branding.from_dict(data.get("branding", {}))
        template = TemplateOptions.from_dict(data.get("template", {}))
        summary_template = pathlib.Path(data.get("summary_template", "templates/summary_template.txt"))
        return cls(branding=branding, template=template, summary_template=summary_template)


def load_config(config_path: pathlib.Path) -> ReportConfig:
    """Load the configuration from a YAML or JSON file."""

    with config_path.open("r", encoding="utf-8") as handle:
        if config_path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(handle) or {}
        else:
            data = json.load(handle)

    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a mapping at the top level.")

    config = ReportConfig.from_mapping(data)

    config.template.output_directory.mkdir(parents=True, exist_ok=True)
    return config
