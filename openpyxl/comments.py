class Comment:
    """Simplified representation of an Excel cell comment."""

    def __init__(self, text: str, author: str | None = None):
        self.text = text
        self.author = author

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"Comment(text={self.text!r}, author={self.author!r})"
