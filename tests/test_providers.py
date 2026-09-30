"""Tests for the explicit provider boundary."""

import pytest

from tests.fakes.providers import FakeProvider
from tllib.providers.provider import (
    CapabilityId,
    ProviderExecutionError,
    ProviderIncompatibleError,
    ProviderInputError,
    ProviderInvalidResultError,
    ProviderRequiredError,
    ProviderTimeoutError,
    invoke_provider,
)

CAPABILITY = CapabilityId("master.lookup")
OTHER_CAPABILITY = CapabilityId("master.write")


def test_provider_is_required() -> None:
    with pytest.raises(ProviderRequiredError, match="provider is required"):
        invoke_provider(
            None,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
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
        )


def test_valid_provider_result_is_returned() -> None:
    provider = FakeProvider[str, str]([CAPABILITY], result="Ada")

    assert (
        invoke_provider(
            provider,
            CAPABILITY,
            "Ada",
            input_type=str,
            result_type=str,
            timeout_seconds=1,
        )
        == "Ada"
    )
