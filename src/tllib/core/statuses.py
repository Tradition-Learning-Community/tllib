"""Stable statuses used by tllib and the published handoff."""

from enum import Enum


class Status(str, Enum):
    """Lifecycle state for an operation or resource."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ResultStatus(str, Enum):
    """Outcome state for a Result."""

    OK = "ok"
    ERROR = "error"


class ScientificStatus(str, Enum):
    """Scientific status values published by tllib-specs."""

    DEFINED = "defined"
    PARTIALLY_DEFINED = "partially_defined"
    PRESERVED_UNRESOLVED = "preserved_unresolved"
    EXTERNAL_PROVIDER_REQUIRED = "external_provider_required"
    NOT_APPLICABLE = "not_applicable"


class ExecutionStatus(str, Enum):
    """Execution status values published by tllib-specs."""

    STRUCTURAL_ONLY = "structural_only"
    EXECUTABLE = "executable"
    CONDITIONALLY_EXECUTABLE = "conditionally_executable"
    UNSUPPORTED = "unsupported"
