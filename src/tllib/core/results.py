"""Immutable success and failure results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .errors import TLCError
from .statuses import ResultStatus

ValueT = TypeVar("ValueT")


@dataclass(frozen=True, slots=True)
class Result(Generic[ValueT]):
    """An explicit outcome carrying either a value or a stable error."""

    status: ResultStatus
    value: ValueT | None = None
    error: TLCError | None = None

    def __post_init__(self) -> None:
        if self.status is ResultStatus.OK and self.error is not None:
            raise ValueError("Successful results cannot contain an error")
        if self.status is ResultStatus.ERROR and self.error is None:
            raise ValueError("Error results must contain an error")

    @classmethod
    def ok(cls, value: ValueT) -> Result[ValueT]:
        """Build a successful result."""
        return cls(ResultStatus.OK, value=value)

    @classmethod
    def failure(cls, error: TLCError) -> Result[ValueT]:
        """Build a failed result with a serializable domain error."""
        return cls(ResultStatus.ERROR, error=error)

    @property
    def is_ok(self) -> bool:
        return self.status is ResultStatus.OK

    def unwrap(self) -> ValueT:
        """Return the value or raise the contained error."""
        if not self.is_ok:
            assert self.error is not None
            raise self.error
        return self.value  # type: ignore[return-value]
