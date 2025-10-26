"""Natural language templates for summarising metric changes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Mapping

from .template_engine import TemplateEngine


ContextBuilder = Callable[[Mapping[str, Any]], Dict[str, Any]]


@dataclass(frozen=True)
class TemplateDefinition:
    """Definition of a single natural language template."""

    key: str
    template: str
    description: str
    context_builder: ContextBuilder
    metric_keys: Iterable[str]

    def build_context(self, aggregated: Mapping[str, Any]) -> Dict[str, Any]:
        return self.context_builder(aggregated)


def _capex_context(aggregated: Mapping[str, Any]) -> Dict[str, Any]:
    capex = aggregated.get("capex") or {}
    change_pct = capex.get("change_pct")
    return {
        "metric_label": "CAPEX",
        "change_pct": change_pct,
        "direction": change_pct,
    }


def _irr_context(aggregated: Mapping[str, Any]) -> Dict[str, Any]:
    irr = aggregated.get("irr") or {}
    return {
        "current": irr.get("current"),
        "previous": irr.get("previous"),
        "change_pct_point": irr.get("change_pct_point"),
        "direction": irr.get("change_pct_point"),
    }


def _opex_context(aggregated: Mapping[str, Any]) -> Dict[str, Any]:
    opex = aggregated.get("opex") or {}
    return {
        "metric_label": "OPEX",
        "change_pct": opex.get("change_pct"),
        "direction": opex.get("change_pct"),
    }


TEMPLATES: Dict[str, TemplateDefinition] = {
    "capex_change": TemplateDefinition(
        key="capex_change",
        template=(
            "{{ metric_label }}는 이전 기간 대비 "
            "{{ change_pct | signed_percentage(1) }} "
            "{{ direction | direction_phrase(increase='증가했습니다.', decrease='감소했습니다.', no_change='변동이 없었습니다.') }}"
        ),
        description="CAPEX 변화율 요약",
        context_builder=_capex_context,
        metric_keys=["capex"],
    ),
    "irr_change": TemplateDefinition(
        key="irr_change",
        template=(
            "프로젝트 IRR은 {{ previous | percentage(1) }}에서 "
            "{{ current | percentage(1) }}로 {{ change_pct_point | signed_percentage(1, unit='p') }} "
            "{{ direction | direction_phrase(increase='증가했습니다.', decrease='감소했습니다.', no_change='변동이 없었습니다.') }}"
        ),
        description="IRR 변화 요약",
        context_builder=_irr_context,
        metric_keys=["irr"],
    ),
    "opex_change": TemplateDefinition(
        key="opex_change",
        template=(
            "{{ metric_label }}는 전년 대비 "
            "{{ change_pct | signed_percentage(1) }} "
            "{{ direction | direction_phrase(increase='증가했습니다.', decrease='감소했습니다.', no_change='변동이 없었습니다.') }}"
        ),
        description="OPEX 변화율 요약",
        context_builder=_opex_context,
        metric_keys=["opex"],
    ),
}


SCENARIO_TEMPLATES: Dict[str, List[str]] = {
    "default": ["capex_change", "irr_change"],
    "cost_focus": ["capex_change", "opex_change"],
}


def render_sentence(engine: TemplateEngine, template_key: str, aggregated: Mapping[str, Any]) -> str:
    definition = TEMPLATES[template_key]
    if not all(metric in aggregated and aggregated.get(metric) is not None for metric in definition.metric_keys):
        raise KeyError(f"Missing required metrics for template '{template_key}'")
    context = definition.build_context(aggregated)
    return engine.render(definition.template, context)


def generate_summary(
    aggregated: Mapping[str, Any],
    scenario: str = "default",
    engine: TemplateEngine | None = None,
) -> str:
    engine = engine or TemplateEngine()
    template_keys = SCENARIO_TEMPLATES.get(scenario, SCENARIO_TEMPLATES["default"])
    sentences = []
    for key in template_keys:
        try:
            sentence = render_sentence(engine, key, aggregated)
        except KeyError:
            continue
        if sentence:
            sentences.append(sentence)
    return " ".join(sentences)
