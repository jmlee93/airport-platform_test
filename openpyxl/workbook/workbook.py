from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterator, Tuple

from ..cell.cell import Cell


@dataclass
class Worksheet:
    title: str = "Sheet"

    def __post_init__(self) -> None:
        self._cells: Dict[Tuple[int, int], Cell] = {}

    def __getitem__(self, coordinate: str) -> Cell:
        row, column = _coordinate_to_tuple(coordinate)
        return self._get_cell(row, column)

    def __setitem__(self, coordinate: str, value) -> None:
        cell = self[coordinate]
        cell.value = value

    @property
    def max_row(self) -> int:
        return max((row for row, _ in self._cells.keys()), default=0)

    @property
    def max_column(self) -> int:
        return max((column for _, column in self._cells.keys()), default=0)

    def iter_rows(self) -> Iterator[Tuple[Cell, ...]]:
        max_row = self.max_row
        max_col = self.max_column
        if max_row == 0 or max_col == 0:
            return iter(())

        rows = []
        for row in range(1, max_row + 1):
            row_cells = []
            for column in range(1, max_col + 1):
                row_cells.append(self._get_cell(row, column))
            rows.append(tuple(row_cells))
        return iter(rows)

    def _get_cell(self, row: int, column: int) -> Cell:
        key = (row, column)
        if key not in self._cells:
            self._cells[key] = Cell(self, row=row, column=column)
        return self._cells[key]


class Workbook:
    def __init__(self) -> None:
        self._worksheets = [Worksheet()]

    @property
    def worksheets(self) -> list[Worksheet]:
        return self._worksheets

    @property
    def active(self) -> Worksheet:
        return self._worksheets[0]


def _coordinate_to_tuple(coordinate: str) -> Tuple[int, int]:
    column_letters = ""
    row_digits = ""
    for ch in coordinate.upper():
        if ch.isalpha():
            column_letters += ch
        elif ch.isdigit():
            row_digits += ch
    if not column_letters or not row_digits:
        raise ValueError(f"Invalid cell coordinate: {coordinate!r}")
    row = int(row_digits)
    column = 0
    for char in column_letters:
        column = column * 26 + (ord(char) - ord("A") + 1)
    return row, column
