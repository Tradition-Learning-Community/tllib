"""Stable, serializable errors for domain and application boundaries."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .identifiers import FeatureId


@dataclass(frozen=True, slots=True)
class TLCError(Exception):
    """Base error with a stable code, optional TLC-FC identity, and context."""

    code: str
    message: str
    context: Mapping[str, object] = field(default_factory=dict)
    feature_id: FeatureId | None = None

    def __post_init__(self) -> None:
        if not self.code or not isinstance(self.code, str):
            raise ValueError("Error code must be a non-empty string")
        if not isinstance(self.message, str):
            raise ValueError("Error message must be a string")
        object.__setattr__(self, "context", dict(self.context))
        Exception.__init__(self, self.message)

    def to_dict(self) -> dict[str, object]:
        """Return stable error data suitable for canonical serialization."""
        value: dict[str, object] = {
            "code": self.code,
            "message": self.message,
            "context": dict(self.context),
        }
        if self.feature_id is not None:
            value["feature_id"] = str(self.feature_id)
        return value


TllibError = TLCError


class ValidationError(TLCError):
    """Input failed a domain validation rule."""

    def __init__(
        self,
        message: str,
        context: Mapping[str, object] | None = None,
        *,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "validation_error", message, context or {}, feature_id=feature_id
        )


class NotFoundError(TLCError):
    """A requested domain entity does not exist."""

    def __init__(
        self,
        message: str,
        context: Mapping[str, object] | None = None,
        *,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__("not_found", message, context or {}, feature_id=feature_id)


class ConflictError(TLCError):
    """An operation conflicts with current domain state."""

    def __init__(
        self,
        message: str,
        context: Mapping[str, object] | None = None,
        *,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__("conflict", message, context or {}, feature_id=feature_id)


class ProviderRequiredError(TLCError):
    """A conditional capability was requested without a provider."""

    def __init__(
        self,
        capability: str,
        *,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "provider_required",
            f"A provider is required for capability {capability}",
            {"capability": capability},
            feature_id=feature_id,
        )


class FeatureNotExecutableError(TLCError):
    """A structural or unsupported feature was requested as executable."""

    def __init__(self, feature_id: FeatureId, execution_status: str) -> None:
        super().__init__(
            "feature_not_executable",
            f"Feature {feature_id} is not executable",
            {"execution_status": execution_status},
            feature_id=feature_id,
        )


class VersionIncompatibleError(TLCError):
    """The runtime and specification versions are incompatible."""

    def __init__(
        self,
        expected: str,
        observed: str,
        *,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "version_incompatible",
            f"Incompatible version: expected {expected}, observed {observed}",
            {"expected": expected, "observed": observed},
            feature_id=feature_id,
        )


class InvariantViolationError(TLCError):
    """A published runtime invariant was violated."""

    def __init__(
        self,
        feature_id: FeatureId,
        message: str,
        context: Mapping[str, object] | None = None,
    ) -> None:
        super().__init__(
            "invariant_violation",
            message,
            context or {},
            feature_id=feature_id,
        )
