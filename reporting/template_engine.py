"""Lightweight template engine for rendering natural language summaries."""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Callable, Dict, Mapping


Expression = re.compile(r"{{\s*(.*?)\s*}}")


def _format_decimal(value: float | int, decimals: int, signed: bool) -> str:
    quant = Decimal("1").scaleb(-decimals)
    rounded = Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP)
    if signed:
        return format(rounded, f"+.{decimals}f")
    return format(rounded, f".{decimals}f")


def _signed_percentage(value: float | int | None, decimals: int = 1, unit: str = "%") -> str:
    if value is None:
        return "N/A"
    formatted = _format_decimal(value, decimals, signed=True)
    return f"{formatted}{unit}"


def _percentage(value: float | int | None, decimals: int = 1, unit: str = "%") -> str:
    if value is None:
        return "N/A"
    formatted = _format_decimal(value, decimals, signed=False)
    return f"{formatted}{unit}"


def _signed_value(value: float | int | None, decimals: int = 1, unit: str = "") -> str:
    if value is None:
        return "N/A"
    formatted = _format_decimal(value, decimals, signed=True)
    return f"{formatted}{unit}" if unit else formatted


def _direction_phrase(
    value: float | int | None,
    increase: str = "증가했습니다",
    decrease: str = "감소했습니다",
    no_change: str = "변동이 없었습니다",
) -> str:
    if value is None:
        return "정보가 충분하지 않습니다"
    if value > 0:
        return increase
    if value < 0:
        return decrease
    return no_change


@dataclass
class TemplateEngine:
    """A very small templating engine with filter support."""

    filters: Dict[str, Callable[..., Any]] | None = None
    _filters: Dict[str, Callable[..., Any]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        defaults: Dict[str, Callable[..., Any]] = {
            "signed_percentage": _signed_percentage,
            "percentage": _percentage,
            "direction_phrase": _direction_phrase,
            "signed_value": _signed_value,
        }
        self._filters = {**defaults, **(self.filters or {})}

    def render(self, template: str, context: Mapping[str, Any]) -> str:
        def _replace(match: re.Match[str]) -> str:
            expression = match.group(1)
            return str(self._evaluate_expression(expression, context))

        rendered = Expression.sub(_replace, template)
        return " ".join(rendered.split())

    def _evaluate_expression(self, expression: str, context: Mapping[str, Any]) -> Any:
        parts = [part.strip() for part in expression.split("|")]
        if not parts:
            return ""
        value = self._resolve_name(parts[0], context)
        for part in parts[1:]:
            value = self._apply_filter(part, value)
        return value

    @staticmethod
    def _resolve_name(name: str, context: Mapping[str, Any]) -> Any:
        if name in context:
            return context[name]
        raise KeyError(f"Unknown template variable '{name}'")

    def _apply_filter(self, filter_expression: str, value: Any) -> Any:
        filter_expression = filter_expression.strip()
        if not filter_expression:
            return value
        if "(" not in filter_expression:
            func_name = filter_expression
            args: tuple[Any, ...] = ()
            kwargs: Dict[str, Any] = {}
        else:
            call = ast.parse(filter_expression, mode="eval").body
            if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name):
                raise ValueError(f"Unsupported filter expression: {filter_expression}")
            func_name = call.func.id
            args = tuple(ast.literal_eval(arg) for arg in call.args)
            kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
        func = self._filters.get(func_name)
        if func is None:
            raise KeyError(f"Unknown filter '{func_name}'")
        return func(value, *args, **kwargs)
