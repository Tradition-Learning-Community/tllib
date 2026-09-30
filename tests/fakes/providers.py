"""Provider doubles reserved for tests."""

from collections.abc import Collection
from typing import Generic, TypeVar

from tllib.providers.provider import CapabilityId

InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class FakeProvider(Generic[InputT, OutputT]):
    """Configurable in-memory provider double."""

    def __init__(
        self,
        capabilities: Collection[CapabilityId],
        result: OutputT | None = None,
        exception: Exception | None = None,
    ) -> None:
        self.capabilities = capabilities
        self.result = result
        self.exception = exception

    def provide(
        self, capability: CapabilityId, value: InputT, *, timeout_seconds: float
    ) -> OutputT | None:
        if self.exception is not None:
            raise self.exception
        return self.result
