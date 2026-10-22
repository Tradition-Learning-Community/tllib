"""Public API for tllib."""

from .core import (
    DomainId,
    ExecutionStatus,
    FeatureId,
    FeatureNotExecutableError,
    InvariantViolationError,
    ProviderRequiredError,
    Result,
    ScientificStatus,
    TLCError,
    TllibError,
    ValidationError,
    Version,
    VersionIncompatibleError,
)
from .specs.lock import load_lock


def specification_info() -> dict[str, str]:
    """Return validated metadata for the specification snapshot in use."""
    return load_lock().as_dict()


__all__ = [
    "DomainId",
    "ExecutionStatus",
    "FeatureId",
    "FeatureNotExecutableError",
    "InvariantViolationError",
    "ProviderRequiredError",
    "Result",
    "ScientificStatus",
    "TLCError",
    "TllibError",
    "ValidationError",
    "Version",
    "VersionIncompatibleError",
    "specification_info",
]
