"""Public helper functions shared by contract submodules."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any, TypeVar

from ._base import ContractModel, ContractValidationError, canonical_json

ModelT = TypeVar("ModelT", bound=ContractModel)


def validate(model_type: type[ModelT], value: Mapping[str, Any]) -> ModelT:
    """Validate and freeze a mapping as the requested published contract."""
    return model_type.from_mapping(value)


def to_json(model: ContractModel) -> str:
    """Serialize a contract deterministically without interpreting its values."""
    return canonical_json(model.to_mapping())


def from_json(model_type: type[ModelT], text: str) -> ModelT:
    """Decode and strictly validate one contract JSON object."""
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ContractValidationError("contract JSON is invalid") from exc
    if not isinstance(value, Mapping):
        raise ContractValidationError("contract JSON must contain an object")
    return validate(model_type, value)
