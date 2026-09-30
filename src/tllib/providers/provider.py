"""Contracts for explicitly injected external providers."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Protocol, TypeVar

from tllib.core.errors import TLCError
from tllib.core.identifiers import Identifier

InputT = TypeVar("InputT", contravariant=True)
OutputT = TypeVar("OutputT", covariant=True)


@dataclass(frozen=True, slots=True)
class CapabilityId:
    """Stable identifier for an operation a provider can perform."""

    value: str

    def __post_init__(self) -> None:
        Identifier(self.value)

    def __str__(self) -> str:
        return self.value


class Provider(Protocol[InputT, OutputT]):
    """Port implemented by an externally supplied capability provider."""

    @property
    def capabilities(self) -> Collection[CapabilityId]:
        """Return the capabilities this provider explicitly supports."""

    def provide(
        self, capability: CapabilityId, value: InputT, *, timeout_seconds: float
    ) -> OutputT:
        """Produce a result for ``capability`` within the supplied timeout."""


class ProviderRequiredError(TLCError):
    """Raised when an operation is invoked without an injected provider."""

    def __init__(self, capability: CapabilityId) -> None:
        super().__init__(
            "provider_required",
            f"A provider is required for capability {capability}",
            {"capability": str(capability)},
        )


class ProviderIncompatibleError(TLCError):
    """Raised when a provider does not declare the requested capability."""

    def __init__(self, capability: CapabilityId) -> None:
        super().__init__(
            "provider_incompatible",
            f"Provider does not support capability {capability}",
            {"capability": str(capability)},
        )


class ProviderInputError(TLCError):
    """Raised when a provider input does not match the declared runtime type."""

    def __init__(self, capability: CapabilityId, expected: type[object]) -> None:
        super().__init__(
            "provider_input_invalid",
            f"Input for capability {capability} must be {expected.__name__}",
            {"capability": str(capability), "expected_type": expected.__name__},
        )


class ProviderTimeoutError(TLCError):
    """Raised when a provider reports that its deadline elapsed."""

    def __init__(self, capability: CapabilityId, timeout_seconds: float) -> None:
        super().__init__(
            "provider_timeout",
            f"Provider timed out for capability {capability}",
            {"capability": str(capability), "timeout_seconds": timeout_seconds},
        )


class ProviderInvalidResultError(TLCError):
    """Raised when a provider result does not match the declared runtime type."""

    def __init__(self, capability: CapabilityId, expected: type[object]) -> None:
        super().__init__(
            "provider_result_invalid",
            f"Result for capability {capability} must be {expected.__name__}",
            {"capability": str(capability), "expected_type": expected.__name__},
        )


class ProviderExecutionError(TLCError):
    """Raised when a provider fails for a reason other than a timeout."""

    def __init__(self, capability: CapabilityId) -> None:
        super().__init__(
            "provider_execution_failed",
            f"Provider failed for capability {capability}",
            {"capability": str(capability)},
        )


def invoke_provider(
    provider: Provider[InputT, OutputT] | None,
    capability: CapabilityId,
    value: object,
    *,
    input_type: type[InputT],
    result_type: type[OutputT],
    timeout_seconds: float,
) -> OutputT:
    """Invoke one explicitly supplied provider with validated boundaries.

    No provider is selected, created, or substituted by this helper. Providers
    must cooperatively enforce ``timeout_seconds`` and raise ``TimeoutError``
    when their deadline expires.
    """
    if provider is None:
        raise ProviderRequiredError(capability)
    if not isinstance(timeout_seconds, (int, float)) or isinstance(
        timeout_seconds, bool
    ) or timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be a positive number")
    if capability not in provider.capabilities:
        raise ProviderIncompatibleError(capability)
    if not isinstance(value, input_type):
        raise ProviderInputError(capability, input_type)

    try:
        result = provider.provide(
            capability, value, timeout_seconds=float(timeout_seconds)
        )
    except TimeoutError as exc:
        raise ProviderTimeoutError(capability, float(timeout_seconds)) from exc
    except Exception as exc:
        raise ProviderExecutionError(capability) from exc

    if not isinstance(result, result_type):
        raise ProviderInvalidResultError(capability, result_type)
    return result
