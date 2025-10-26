class Color:
    """Minimal color container with an :attr:`rgb` attribute."""

    def __init__(self, rgb: str | None = None):
        self.rgb = None if rgb is None else rgb.upper()

    def __str__(self) -> str:  # pragma: no cover - debug helper
        return self.rgb or ""
