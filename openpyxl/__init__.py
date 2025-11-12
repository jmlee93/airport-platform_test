"""A lightweight subset of the :mod:`openpyxl` API used for testing purposes."""

from .workbook.workbook import Workbook
from .workbook.workbook import Worksheet
from .cell.cell import Cell
from .comments import Comment
from .styles import PatternFill
from .styles.colors import Color


def load_workbook(*args, **kwargs):  # pragma: no cover - stub functionality
    raise NotImplementedError(
        "This test-oriented stub does not support loading workbooks from disk."
    )


__all__ = [
    "Workbook",
    "Worksheet",
    "Cell",
    "Comment",
    "PatternFill",
    "Color",
    "load_workbook",
]
