from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Protocol, Sequence, Set

from openpyxl.formula import Tokenizer

from .models import FinancialMetric


class FormulaPlugin(Protocol):
    """Protocol for plugins that can inspect formula tokens and identify metrics."""

    def identify(self, sheet: str, coordinate: str, formula: str, tokens: Sequence[str]) -> Iterable[FinancialMetric]:
        ...


@dataclass
class FormulaRuleRegistry:
    """Registry maintaining the active formula plugins."""

    plugins: List[FormulaPlugin] = field(default_factory=list)

    def register(self, plugin: FormulaPlugin) -> None:
        self.plugins.append(plugin)

    def identify_metrics(self, sheet: str, coordinate: str, formula: str) -> List[FinancialMetric]:
        tokenizer = Tokenizer(formula)
        tokens = [token.value.upper() for token in tokenizer.items if token.type == "OPERAND" or token.type == "FUNCTION"]
        metrics: List[FinancialMetric] = []
        for plugin in self.plugins:
            metrics.extend(plugin.identify(sheet, coordinate, formula, tokens))
        return metrics


@dataclass
class FinancialFunctionPlugin:
    """Detects well-known financial Excel functions."""

    function_mapping: Dict[str, str] = field(
        default_factory=lambda: {
            "IRR": "Internal Rate of Return",
            "XIRR": "Extended Internal Rate of Return",
            "NPV": "Net Present Value",
            "XNPV": "Extended Net Present Value",
            "MIRR": "Modified Internal Rate of Return",
            "RATE": "Interest Rate",
            "PV": "Present Value",
            "FV": "Future Value",
            "PMT": "Payment Amount",
            "IPMT": "Interest Payment",
            "PPMT": "Principal Payment",
            "NPER": "Number of Periods",
            "DSCR": "Debt Service Coverage Ratio",
        }
    )

    def identify(self, sheet: str, coordinate: str, formula: str, tokens: Sequence[str]) -> Iterable[FinancialMetric]:
        present_tokens: Set[str] = set(tokens)
        for function, description in self.function_mapping.items():
            if function in present_tokens:
                yield FinancialMetric(
                    sheet=sheet,
                    coordinate=coordinate,
                    formula=formula,
                    metric=function,
                    details={"description": description},
                )


@dataclass
class KeywordPlugin:
    """Search for domain-specific keywords embedded within formulas."""

    keywords: Dict[str, str] = field(
        default_factory=lambda: {
            "DSCR": "Debt Service Coverage Ratio",
            "EBITDA": "Earnings Before Interest, Taxes, Depreciation, and Amortization",
        }
    )

    def identify(self, sheet: str, coordinate: str, formula: str, tokens: Sequence[str]) -> Iterable[FinancialMetric]:
        uppercase_formula = formula.upper()
        for keyword, description in self.keywords.items():
            if keyword in uppercase_formula:
                yield FinancialMetric(
                    sheet=sheet,
                    coordinate=coordinate,
                    formula=formula,
                    metric=keyword,
                    details={"description": description, "source": "keyword"},
                )


def default_registry() -> FormulaRuleRegistry:
    registry = FormulaRuleRegistry()
    registry.register(FinancialFunctionPlugin())
    registry.register(KeywordPlugin())
    return registry
