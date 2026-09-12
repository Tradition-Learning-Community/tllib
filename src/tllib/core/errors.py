"""Stable, serializable errors for domain and application boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class TLCError(Exception):
    """Base error with a stable code and JSON-compatible context."""

    code: str
    message: str
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.code or not isinstance(self.code, str):
            raise ValueError("Error code must be a non-empty string")
        if not isinstance(self.message, str):
            raise ValueError("Error message must be a string")
        object.__setattr__(self, "context", dict(self.context))
        Exception.__init__(self, self.message)

    def to_dict(self) -> dict[str, object]:
        """Return stable error data suitable for canonical serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "context": dict(self.context),
        }


class ValidationError(TLCError):
    """Input failed a domain validation rule."""

    def __init__(
        self, message: str, context: Mapping[str, object] | None = None
    ) -> None:
        super().__init__("validation_error", message, context or {})


class NotFoundError(TLCError):
    """A requested domain entity does not exist."""

    def __init__(
        self, message: str, context: Mapping[str, object] | None = None
    ) -> None:
        super().__init__("not_found", message, context or {})


class ConflictError(TLCError):
    """An operation conflicts with current domain state."""

    def __init__(
        self, message: str, context: Mapping[str, object] | None = None
    ) -> None:
        super().__init__("conflict", message, context or {})
