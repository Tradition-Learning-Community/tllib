"""Internal structural support for published shared contracts."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, ClassVar, TypeVar, cast

_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    if isinstance(value, tuple):
        return tuple(freeze(item) for item in value)
    return value


def thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [thaw(item) for item in value]
    return value


class ContractValidationError(ValueError):
    """Raised when a shared contract value violates its published shape."""


ModelT = TypeVar("ModelT", bound="ContractModel")


@dataclass(frozen=True, slots=True)
class ContractModel:
    """Immutable structural carrier; it intentionally does not interpret payloads."""

    data: Mapping[str, Any]
    contract_id: ClassVar[str]
    required_fields: ClassVar[frozenset[str]] = frozenset()
    optional_fields: ClassVar[frozenset[str]] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.data, Mapping):
            raise ContractValidationError("contract value must be an object")
        object.__setattr__(self, "data", freeze(self.data))

    @classmethod
    def from_mapping(cls: type[ModelT], value: Mapping[str, Any]) -> ModelT:
        validate_fields(value, cls.required_fields, cls.optional_fields)
        return cls(value)

    def to_mapping(self) -> dict[str, Any]:
        return cast(dict[str, Any], thaw(self.data))

    def __hash__(self) -> int:
        return hash(canonical_json(self.to_mapping()))


def validate_fields(
    value: Mapping[str, Any], required: frozenset[str], optional: frozenset[str]
) -> None:
    if not isinstance(value, Mapping):
        raise ContractValidationError("contract value must be an object")
    keys = set(value)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        raise ContractValidationError(f"missing required fields: {sorted(missing)}")
    if unknown:
        raise ContractValidationError(f"unknown fields: {sorted(unknown)}")


def require_string(value: Any, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise ContractValidationError(f"{field} must be a non-empty string")


def require_identifier(value: Any, field: str) -> None:
    require_string(value, field)
    if _IDENTIFIER.fullmatch(value) is None:
        raise ContractValidationError(f"{field} is not a valid identifier")


def require_enum(value: Any, field: str, allowed: frozenset[str]) -> None:
    require_string(value, field)
    if value not in allowed:
        raise ContractValidationError(f"{field} must be one of {sorted(allowed)}")


def require_relative_path(value: Any, field: str) -> None:
    require_string(value, field)
    if value.startswith(("/", "\\")) or ":" in value or ".." in value.split("/"):
        raise ContractValidationError(f"{field} must be repository-relative")


def require_list(value: Any, field: str) -> None:
    if not isinstance(value, (list, tuple)):
        raise ContractValidationError(f"{field} must be an array")


def reject_cycles(value: Any) -> None:
    """Reject cycles in nested contract data while allowing repeated scalars."""
    active: set[int] = set()

    def visit(node: Any) -> None:
        if not isinstance(node, (Mapping, list, tuple)):
            return
        marker = id(node)
        if marker in active:
            raise ContractValidationError("cyclic contract data is not allowed")
        active.add(marker)
        values = node.values() if isinstance(node, Mapping) else node
        for child in values:
            visit(child)
        active.remove(marker)

    visit(value)


def canonical_json(value: Any) -> str:
    return json.dumps(
        thaw(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
