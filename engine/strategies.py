"""Calculation strategy definitions for sensitivity analysis runs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping, MutableMapping


class CalculationStrategy(ABC):
    """Base strategy for executing a calculation for a parameter set."""

    @abstractmethod
    def run(self, parameters: Mapping[str, Any]) -> MutableMapping[str, Any]:
        """Execute a calculation for the provided parameters.

        Args:
            parameters: Parameter names and their values for the scenario being
                calculated.

        Returns:
            A mutable mapping containing the calculation outputs. Mutable
            mappings are used to ease serialization by callers.
        """


class ExcelCalculationStrategy(CalculationStrategy):
    """Strategy that executes a calculation by driving an Excel workbook.

    The concrete recalculation logic is delegated to ``workbook_runner`` to
    allow the caller to choose the engine (``openpyxl``, ``xlwings`` or any
    other integration).
    """

    def __init__(
        self,
        workbook_runner: Callable[[Mapping[str, Any]], MutableMapping[str, Any]],
    ) -> None:
        self._workbook_runner = workbook_runner

    def run(self, parameters: Mapping[str, Any]) -> MutableMapping[str, Any]:
        return self._workbook_runner(parameters)


class DAGCalculationStrategy(CalculationStrategy):
    """Strategy that executes a calculation by triggering a DAG runner."""

    def __init__(
        self,
        dag_runner: Callable[[Mapping[str, Any]], MutableMapping[str, Any]],
    ) -> None:
        self._dag_runner = dag_runner

    def run(self, parameters: Mapping[str, Any]) -> MutableMapping[str, Any]:
        return self._dag_runner(parameters)
