"""Utilities for generating natural language financial reports."""

from .nlg_templates import (  # noqa: F401
    SCENARIO_TEMPLATES,
    TEMPLATES,
    TemplateDefinition,
    generate_summary,
    render_sentence,
)
from .template_engine import TemplateEngine  # noqa: F401

__all__ = [
    "TemplateEngine",
    "TemplateDefinition",
    "TEMPLATES",
    "SCENARIO_TEMPLATES",
    "generate_summary",
    "render_sentence",
]
