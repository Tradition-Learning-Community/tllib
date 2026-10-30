"""Explicit Python callback adapters for the native tllib provider port.

The C++ frozen registry remains the sole authority for provider dispatch and errors.
No providers are discovered, and no scientific fallback is implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, TypeAlias

from . import _native

TllibError = _native.TllibError
__version__: str = _native.native_version()


ValidationError = _native.ValidationError
FeatureUnavailableError = _native.FeatureUnavailableError
ProviderRequiredError = _native.ProviderRequiredError
ProviderExecutionError = _native.ProviderExecutionError
IncompatibleSpecsError = _native.IncompatibleSpecsError
CancelledError = _native.CancelledError
IndeterminateOutcomeError = _native.IndeterminateOutcomeError


@dataclass(frozen=True)
class FeatureId:
    """Immutable/hashable TLC-FC identity validated by the authoritative C++ parser."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _native.canonical_feature_id(self.value))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class DomainId:
    """Immutable/hashable domain identity validated by C++, without normalization."""

    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _native.canonical_domain_id(self.value))

    def __str__(self) -> str:
        return self.value


class ExecutionStatus(str, Enum):
    """Closed native execution-status vocabulary (not a compliance claim)."""

    STRUCTURAL_ONLY = "structural_only"
    EXECUTABLE = "executable"
    CONDITIONALLY_EXECUTABLE = "conditionally_executable"
    UNSUPPORTED = "unsupported"


def parse_execution_status(value: str) -> ExecutionStatus:
    """Validate with the C++ parser and return the matching Python enum."""
    return ExecutionStatus(_native.canonical_execution_status(value))


ProviderCallback: TypeAlias = Callable[[str, str, bytes, str, str], tuple[str, bytes]]
PayloadValidator: TypeAlias = Callable[[bytes], bool]


@dataclass(frozen=True)
class ProviderRegistration:
    """A caller-supplied capability and its owned Python callback.

    The interface contracts must refer to the consuming feature's published contract.
    """

    capability_id: str
    interface_version: str
    provider_id: str
    input_contract: str
    output_contract: str
    provenance: str
    callback: ProviderCallback
    validate_input: PayloadValidator
    validate_output: PayloadValidator
    concurrent_safe: bool = False


@dataclass(frozen=True)
class ProviderRequest:
    """Validated native request metadata and opaque bytes; no inferred capability."""

    feature_id: str
    capability_id: str
    operation_id: str
    input_contract: str
    payload: bytes
    specs_fingerprint: str
    correlation_id: str
    interface_version: str


@dataclass(frozen=True)
class ProviderResponse:
    """Bytes returned after the native output validator has accepted them."""

    output_contract: str
    payload: bytes



@dataclass(frozen=True)
class BufferInfo:
    """Metadata observed while a Python exporter was held through Py_buffer.

    The metadata does not retain the exporter or reveal its native address.
    """

    dtype: str
    shape: tuple[int, ...]
    strides: tuple[int, ...]
    layout: str
    readonly: bool
    nbytes: int
    zero_copy: bool


def inspect_buffer(value: object) -> BufferInfo:
    """Inspect a CPU contiguous int32/float64 exporter with no data copy.

    A non-contiguous, non-native-endian, unsupported dtype or unsafe layout is
    rejected with a structured TllibError. Create an explicit copy yourself if
    the original representation is not compatible.
    """
    return BufferInfo(**_native.inspect_buffer(value))

class CancellationSource:
    """Explicit C++ stop source; safe to request cancellation from another thread."""

    __slots__ = ("_source",)

    def __init__(self) -> None:
        self._source = _native.new_cancellation_source()

    def request_stop(self) -> bool:
        return bool(_native.request_stop(self._source))


class ProviderRegistry:
    """Immutable native registry owning supplied callbacks until its last reference dies.

    A Python callback receives (feature_id, operation_id, payload, correlation_id,
    specs_fingerprint) and must return (output_contract, payload: bytes).
    Input/output validators receive bytes and return exactly bool.
    """

    __slots__ = ("_handle",)

    def __init__(self, registrations: Iterable[ProviderRegistration]) -> None:
        data = []
        for entry in registrations:
            if not isinstance(entry, ProviderRegistration):
                raise TypeError("registrations must contain ProviderRegistration objects")
            data.append(
                {
                    "capability_id": entry.capability_id,
                    "interface_version": entry.interface_version,
                    "provider_id": entry.provider_id,
                    "input_contract": entry.input_contract,
                    "output_contract": entry.output_contract,
                    "provenance": entry.provenance,
                    "callback": entry.callback,
                    "validate_input": entry.validate_input,
                    "validate_output": entry.validate_output,
                    "concurrent_safe": entry.concurrent_safe,
                }
            )
        self._handle = _native.create_provider_registry(data)

    def invoke(
        self,
        request: ProviderRequest,
        *,
        cancellation: CancellationSource | None = None,
        timeout_ms: int | None = None,
    ) -> ProviderResponse:
        """Invoke synchronously; no false preemption of blocking callbacks.

        A cancellation/deadline after a callback began yields OUTCOME_INDETERMINATE
        and requires reconciliation before retrying.
        """
        if not isinstance(request, ProviderRequest):
            raise TypeError("request must be ProviderRequest")
        if cancellation is not None and not isinstance(cancellation, CancellationSource):
            raise TypeError("cancellation must be CancellationSource or None")
        result = _native.invoke_provider(
            self._handle,
            {
                "feature_id": request.feature_id,
                "capability_id": request.capability_id,
                "operation_id": request.operation_id,
                "input_contract": request.input_contract,
                "payload": request.payload,
                "specs_fingerprint": request.specs_fingerprint,
                "correlation_id": request.correlation_id,
                "interface_version": request.interface_version,
            },
            {"source": cancellation._source if cancellation is not None else None,
             "timeout_ms": timeout_ms},
        )
        return ProviderResponse(*result)


__all__ = [
    "BufferInfo",
    "FeatureId",
    "DomainId",
    "ExecutionStatus",
    "parse_execution_status",
    "ValidationError",
    "FeatureUnavailableError",
    "ProviderRequiredError",
    "ProviderExecutionError",
    "IncompatibleSpecsError",
    "CancelledError",
    "IndeterminateOutcomeError",
    "inspect_buffer",
    "CancellationSource",
    "PayloadValidator",
    "ProviderCallback",
    "ProviderRegistration",
    "ProviderRegistry",
    "ProviderRequest",
    "ProviderResponse",
    "TllibError",
    "__version__",
]
