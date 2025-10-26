from __future__ import annotations

import importlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from .data_models import Metric


@dataclass
class SummaryTemplate:
    """Utility for rendering narrative summaries."""

    template_text: str

    @classmethod
    def from_file(cls, path: Path) -> "SummaryTemplate":
        return cls(path.read_text(encoding="utf-8"))

    def render(self, metrics: Sequence[Metric]) -> str:
        """Render a baseline summary from the template."""

        bullet_lines = [f"- {metric.name}: {metric.value}" for metric in metrics]
        baseline = self.template_text.replace("{{ metrics }}", "\n".join(bullet_lines))
        return baseline


class SummaryEnricher:
    """Optional enrichment via an LLM provider."""

    def __init__(self, provider: str = "openai", model: str | None = None) -> None:
        self.provider = provider
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def enrich(self, baseline_summary: str) -> str:
        try:
            client_module = importlib.import_module(self.provider)
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "LLM enrichment requested but the provider is not installed."
            ) from exc

        if self.provider == "openai":  # pragma: no cover - network call avoided in tests
            client = client_module.OpenAI()
            response = client.responses.create(
                model=self.model,
                input=(
                    "You are a financial analyst. Rewrite the following bullet points into "
                    "a cohesive executive summary with concise prose, retaining all key metrics.\n\n"
                    f"{baseline_summary}"
                ),
            )
            return response.output[0].content[0].text

        # For other providers we simply return the baseline for now.
        return baseline_summary


def build_summary(metrics: Sequence[Metric], template_path: Path, enrich: bool) -> str:
    summary_template = SummaryTemplate.from_file(template_path)
    baseline = summary_template.render(metrics)
    if not enrich:
        return baseline
    enricher = SummaryEnricher()
    try:
        return enricher.enrich(baseline)
    except RuntimeError:
        return baseline
