"""Result storage abstractions for sensitivity analysis runs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Tuple


class ResultRepository(ABC):
    """Interface for persisting calculation outcomes."""

    @abstractmethod
    def save_result(
        self,
        scenario_id: str,
        parameters: Mapping[str, Any],
        result: MutableMapping[str, Any],
    ) -> None:
        """Persist the result of a calculation."""


class InMemoryResultRepository(ResultRepository):
    """Simple in-memory repository useful for testing."""

    def __init__(self) -> None:
        self._storage: list[Tuple[str, Mapping[str, Any], MutableMapping[str, Any]]] = []

    def save_result(
        self,
        scenario_id: str,
        parameters: Mapping[str, Any],
        result: MutableMapping[str, Any],
    ) -> None:
        self._storage.append((scenario_id, dict(parameters), dict(result)))

    def __iter__(self) -> Iterable[Tuple[str, Mapping[str, Any], MutableMapping[str, Any]]]:
        return iter(self._storage)
