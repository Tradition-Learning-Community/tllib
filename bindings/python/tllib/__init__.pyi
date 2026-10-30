from typing import Callable, Iterable, TypeAlias
from dataclasses import dataclass

__version__: str
class TllibError(Exception):
    code: str
    feature_id: str | None
    specs_provenance: str | None
    context: dict[str, str]
ProviderCallback: TypeAlias = Callable[[str, str, bytes, str, str], tuple[str, bytes]]
PayloadValidator: TypeAlias = Callable[[bytes], bool]

@dataclass(frozen=True)
class ProviderRegistration:
    capability_id: str
    interface_version: str
    provider_id: str
    input_contract: str
    output_contract: str
    provenance: str
    callback: ProviderCallback
    validate_input: PayloadValidator
    validate_output: PayloadValidator
    concurrent_safe: bool = ...

@dataclass(frozen=True)
class ProviderRequest:
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
    output_contract: str
    payload: bytes

@dataclass(frozen=True)
class BufferInfo:
    dtype: str
    shape: tuple[int, ...]
    strides: tuple[int, ...]
    layout: str
    readonly: bool
    nbytes: int
    zero_copy: bool

def inspect_buffer(value: object) -> BufferInfo: ...

class CancellationSource:
    def __init__(self) -> None: ...
    def request_stop(self) -> bool: ...

class ProviderRegistry:
    def __init__(self, registrations: Iterable[ProviderRegistration]) -> None: ...
    def invoke(
        self, request: ProviderRequest, *, cancellation: CancellationSource | None = ...,
        timeout_ms: int | None = ...
    ) -> ProviderResponse: ...
