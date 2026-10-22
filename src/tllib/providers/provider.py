"""Contracts for explicitly injected external providers."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

from tllib.core.errors import ProviderRequiredError, TLCError
from tllib.core.identifiers import FeatureId, Identifier

InputT = TypeVar("InputT", contravariant=True)
OutputT = TypeVar("OutputT", covariant=True)
RegistryInputT = TypeVar("RegistryInputT")
RegistryOutputT = TypeVar("RegistryOutputT")


@dataclass(frozen=True, slots=True)
class CapabilityId:
    """Stable identifier for an operation a provider can perform."""

    value: str

    def __post_init__(self) -> None:
        Identifier(self.value)

    def __str__(self) -> str:
        return self.value


class CancellationToken(Protocol):
    """Cooperative cancellation state supplied by the application."""

    @property
    def cancelled(self) -> bool:
        """Return whether the caller has cancelled the operation."""


@dataclass(frozen=True, slots=True)
class ProviderCallContext:
    """Explicit runtime context passed to an external provider."""

    timeout_seconds: float
    feature_id: FeatureId | None = None
    cancellation: CancellationToken | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.timeout_seconds, (int, float))
            or isinstance(self.timeout_seconds, bool)
            or self.timeout_seconds <= 0
        ):
            raise ValueError("timeout_seconds must be a positive number")


class Provider(Protocol[InputT, OutputT]):
    """Port implemented by an externally supplied capability provider."""

    @property
    def capabilities(self) -> Collection[CapabilityId]:
        """Return the capabilities this provider explicitly supports."""

    def provide(
        self,
        capability: CapabilityId,
        value: InputT,
        *,
        context: ProviderCallContext,
    ) -> OutputT:
        """Produce a validated result for an explicitly requested capability."""


class ProviderIncompatibleError(TLCError):
    """Raised when a provider does not declare the requested capability."""

    def __init__(
        self, capability: CapabilityId, feature_id: FeatureId | None = None
    ) -> None:
        super().__init__(
            "provider_incompatible",
            f"Provider does not support capability {capability}",
            {"capability": str(capability)},
            feature_id=feature_id,
        )


class ProviderInputError(TLCError):
    """Raised when a provider input does not match the declared runtime type."""

    def __init__(
        self,
        capability: CapabilityId,
        expected: type[object],
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "provider_input_invalid",
            f"Input for capability {capability} must be {expected.__name__}",
            {"capability": str(capability), "expected_type": expected.__name__},
            feature_id=feature_id,
        )


class ProviderTimeoutError(TLCError):
    """Raised when a provider reports that its deadline elapsed."""

    def __init__(
        self,
        capability: CapabilityId,
        timeout_seconds: float,
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "provider_timeout",
            f"Provider timed out for capability {capability}",
            {"capability": str(capability), "timeout_seconds": timeout_seconds},
            feature_id=feature_id,
        )


class ProviderCancelledError(TLCError):
    """Raised when cooperative cancellation is observed."""

    def __init__(
        self, capability: CapabilityId, feature_id: FeatureId | None = None
    ) -> None:
        super().__init__(
            "provider_cancelled",
            f"Provider call cancelled for capability {capability}",
            {"capability": str(capability)},
            feature_id=feature_id,
        )


class ProviderInvalidResultError(TLCError):
    """Raised when a provider result does not match the declared runtime type."""

    def __init__(
        self,
        capability: CapabilityId,
        expected: type[object],
        feature_id: FeatureId | None = None,
    ) -> None:
        super().__init__(
            "provider_result_invalid",
            f"Result for capability {capability} must be {expected.__name__}",
            {"capability": str(capability), "expected_type": expected.__name__},
            feature_id=feature_id,
        )


class ProviderExecutionError(TLCError):
    """Raised when a provider fails for a reason other than timeout/cancellation."""

    def __init__(
        self, capability: CapabilityId, feature_id: FeatureId | None = None
    ) -> None:
        super().__init__(
            "provider_execution_failed",
            f"Provider failed for capability {capability}",
            {"capability": str(capability)},
            feature_id=feature_id,
        )


class ProviderRegistry(Generic[RegistryInputT, RegistryOutputT]):
    """Explicit capability-to-provider registry with no discovery side effects."""

    def __init__(self) -> None:
        self._providers: dict[
            CapabilityId, Provider[RegistryInputT, RegistryOutputT]
        ] = {}

    def register(
        self, provider: Provider[RegistryInputT, RegistryOutputT]
    ) -> None:
        """Register all capabilities declared by one provider."""
        capabilities = tuple(provider.capabilities)
        if not capabilities:
            raise ValueError("Provider must declare at least one capability")
        duplicate = next(
            (capability for capability in capabilities if capability in self._providers),
            None,
        )
        if duplicate is not None:
            raise ValueError(f"Capability already registered: {duplicate}")
        for capability in capabilities:
            self._providers[capability] = provider

    def provider_for(
        self, capability: CapabilityId
    ) -> Provider[RegistryInputT, RegistryOutputT] | None:
        """Return the explicitly registered provider or None."""
        return self._providers.get(capability)


def _cancelled(context: ProviderCallContext) -> bool:
    return context.cancellation is not None and context.cancellation.cancelled


def invoke_provider(
    provider: Provider[InputT, OutputT] | None,
    capability: CapabilityId,
    value: object,
    *,
    input_type: type[InputT],
    result_type: type[OutputT],
    timeout_seconds: float,
    feature_id: FeatureId | None = None,
    cancellation: CancellationToken | None = None,
) -> OutputT:
    """Invoke one explicitly supplied provider with validated boundaries."""
    context = ProviderCallContext(
        timeout_seconds=float(timeout_seconds),
        feature_id=feature_id,
        cancellation=cancellation,
    )
    if provider is None:
        raise ProviderRequiredError(str(capability), feature_id=feature_id)
    if capability not in provider.capabilities:
        raise ProviderIncompatibleError(capability, feature_id)
    if not isinstance(value, input_type):
        raise ProviderInputError(capability, input_type, feature_id)
    if _cancelled(context):
        raise ProviderCancelledError(capability, feature_id)

    try:
        result = provider.provide(capability, value, context=context)
    except ProviderCancelledError:
        raise
    except TimeoutError as exc:
        raise ProviderTimeoutError(
            capability, context.timeout_seconds, feature_id
        ) from exc
    except Exception as exc:
        raise ProviderExecutionError(capability, feature_id) from exc

    if _cancelled(context):
        raise ProviderCancelledError(capability, feature_id)
    if not isinstance(result, result_type):
        raise ProviderInvalidResultError(capability, result_type, feature_id)
    return result
