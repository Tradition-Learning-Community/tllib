"""Tests for the explicit provider boundary."""

from dataclasses import dataclass

import pytest

from tests.fakes.providers import FakeProvider
from tllib.core import FeatureId
from tllib.providers.provider import (
    CapabilityId,
    ProviderCancelledError,
    ProviderExecutionError,
    ProviderIncompatibleError,
    ProviderInputError,
    ProviderInvalidResultError,
    ProviderRegistry,
    ProviderRequiredError,
    ProviderTimeoutError,
    invoke_provider,
)

CAPABILITY = CapabilityId("master.lookup")
OTHER_CAPABILITY = CapabilityId("master.write")
FEATURE = FeatureId("TLC-FC-00-MASTER-001")


@dataclass
class FakeCancellation:
    cancelled: bool = False


def test_provider_is_required() -> None:
    with pytest.raises(ProviderRequiredError, match="provider is required"):
        invoke_provider(
            None,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_incompatible_provider_is_rejected() -> None:
    provider = FakeProvider[str, str]([OTHER_CAPABILITY], result="Ada")

    with pytest.raises(ProviderIncompatibleError, match="does not support"):
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_invalid_provider_input_is_rejected() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], result="Ada")

    with pytest.raises(ProviderInputError, match="must be str"):
        invoke_provider(
            provider,
            CAPABILITY,
            42,
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_provider_exception_is_wrapped() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], exception=RuntimeError("down"))

    with pytest.raises(ProviderExecutionError, match="Provider failed"):
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_provider_timeout_is_wrapped() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], exception=TimeoutError())

    with pytest.raises(ProviderTimeoutError, match="timed out"):
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_invalid_provider_result_is_rejected() -> None:
    provider = FakeProvider[str, object]([CAPABILITY], result=42)

    with pytest.raises(ProviderInvalidResultError, match="must be str"):
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )


def test_valid_provider_result_receives_explicit_context() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], result="Ada")

    assert (
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
        )
        == "Ada"
    )
    assert provider.last_context is not None
    assert provider.last_context.feature_id == FEATURE
    assert provider.last_context.timeout_seconds == 1.0


def test_cancelled_call_never_invokes_provider() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], result="Ada")

    with pytest.raises(ProviderCancelledError, match="cancelled"):
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
            feature_id=FEATURE,
            cancellation=FakeCancellation(cancelled=True),
        )
    assert provider.last_context is None


def test_registry_requires_explicit_unique_capabilities() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], result="Ada")
    registry: ProviderRegistry[str, str] = ProviderRegistry()

    assert registry.provider_for(CAPABILITY) is None
    registry.register(provider)
    assert registry.provider_for(CAPABILITY) is provider

    with pytest.raises(ValueError, match="already registered"):
        registry.register(provider)
