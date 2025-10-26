"""Utilities for running sensitivity analyses across parameter combinations."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable, Iterator, List, Mapping, MutableMapping, Sequence, cast

from .results import ResultRepository
from .strategies import CalculationStrategy

ScenarioIdFactory = Callable[[int, Mapping[str, object]], str]


@dataclass(frozen=True)
class Scenario:
    """Container representing the execution context for a calculation."""

    id: str
    parameters: Mapping[str, object]


class SensitivityRunner:
    """Generate scenario combinations and trigger calculations for each one."""

    def __init__(
        self,
        calculation_strategy: CalculationStrategy,
        result_repository: ResultRepository,
        scenario_id_factory: ScenarioIdFactory | None = None,
    ) -> None:
        self._calculation_strategy = calculation_strategy
        self._result_repository = result_repository
        self._scenario_id_factory = scenario_id_factory or self._default_id_factory

    @staticmethod
    def _default_id_factory(index: int, parameters: Mapping[str, object]) -> str:
        return f"scenario_{index:04d}"

    def generate_parameter_combinations(
        self, parameter_grid: Mapping[str, Sequence[object]]
    ) -> Iterator[Mapping[str, object]]:
        """Yield every combination from the provided parameter grid."""

        if not parameter_grid:
            return iter(cast(List[Mapping[str, object]], []))

        names: List[str] = list(parameter_grid.keys())
        values_product = product(*(parameter_grid[name] for name in names))

        def generator() -> Iterator[Mapping[str, object]]:
            for combination in values_product:
                yield {name: value for name, value in zip(names, combination)}

        return generator()

    def run(self, parameter_grid: Mapping[str, Sequence[object]]) -> List[Scenario]:
        """Execute calculations for all parameter combinations."""

        scenarios: List[Scenario] = []
        for index, parameters in enumerate(
            self.generate_parameter_combinations(parameter_grid), start=1
        ):
            parameters_copy = dict(parameters)
            scenario_id = self._scenario_id_factory(index, parameters_copy)
            result: MutableMapping[str, object] = self._calculation_strategy.run(parameters_copy)
            self._result_repository.save_result(scenario_id, parameters_copy, result)
            scenarios.append(Scenario(id=scenario_id, parameters=parameters_copy))

        return scenarios
