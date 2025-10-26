from .colors import Color


class PatternFill:
    """Simplified pattern fill supporting a foreground color."""

    def __init__(self, fill_type: str | None = None, fgColor: str | None = None):
        self.fill_type = fill_type
        self.fgColor = Color(fgColor) if fgColor is not None else None

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"PatternFill(fill_type={self.fill_type!r}, fgColor={self.fgColor!r})"
