from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set

from .models import CellMetadata, WorkbookMetadata


@dataclass
class DependencyGraph:
    """A lightweight representation of workbook cell dependencies."""

    edges: Dict[str, Set[str]] = field(default_factory=dict)

    def add_cell(self, cell: CellMetadata) -> None:
        self.edges.setdefault(cell.id, set()).update(cell.dependencies)
        for dependency in cell.dependencies:
            self.edges.setdefault(dependency, set())

    def downstream(self, node: str) -> Set[str]:
        """Return the direct dependencies for *node*."""

        return self.edges.get(node, set())

    def upstream(self, target: str) -> Set[str]:
        """Return all nodes that reference *target*."""

        return {node for node, deps in self.edges.items() if target in deps}

    def topological_sort(self) -> List[str]:
        """Return a topologically sorted list of nodes if the graph is acyclic."""

        in_degree: Dict[str, int] = {node: 0 for node in self.edges}
        for deps in self.edges.values():
            for dep in deps:
                if dep in in_degree:
                    in_degree[dep] += 1
                else:
                    in_degree[dep] = 1
        queue = [node for node, degree in in_degree.items() if degree == 0]
        ordered: List[str] = []
        idx = 0
        while idx < len(queue):
            node = queue[idx]
            idx += 1
            ordered.append(node)
            for dep in self.edges.get(node, set()):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)
        if len(ordered) != len(in_degree):
            raise ValueError("Dependency graph contains a cycle")
        return ordered

    @classmethod
    def from_workbook(cls, workbook: WorkbookMetadata) -> "DependencyGraph":
        graph = cls()
        for sheet in workbook.sheets.values():
            for cell in sheet.cells.values():
                graph.add_cell(cell)
        return graph

    def subgraph(self, nodes: Iterable[str]) -> "DependencyGraph":
        sub = DependencyGraph()
        for node in nodes:
            deps = self.edges.get(node, set())
            sub.edges[node] = set(deps) & set(nodes)
        return sub
