from __future__ import annotations

from dataclasses import dataclass

from ..comments import Comment
from ..styles import PatternFill


@dataclass
class Cell:
    worksheet: "Worksheet"
    row: int
    column: int

    def __post_init__(self) -> None:
        self.value = None
        self.comment: Comment | None = None
        self.fill = PatternFill()

    @property
    def coordinate(self) -> str:
        return f"{_column_index_to_letter(self.column)}{self.row}"


def _column_index_to_letter(index: int) -> str:
    if index < 1:
        raise ValueError("Column index must be >= 1")
    letters = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        letters = chr(remainder + ord("A")) + letters
    return letters
