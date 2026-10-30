"""Explicit Python callback adapters for the native tllib provider port.

The C++ frozen registry remains the sole authority for provider dispatch and errors.
No providers are discovered, and no scientific fallback is implemented here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, TypeAlias

from . import _native

TllibError = _native.TllibError
__version__: str = _native.native_version()

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
