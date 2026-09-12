"""Stable lifecycle statuses shared by domain operations."""

from enum import Enum


class Status(str, Enum):
    """Lifecycle state for an operation or resource."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ResultStatus(str, Enum):
    """Outcome state for a :class:`~tllib.core.results.Result`."""

    OK = "ok"
    ERROR = "error"
