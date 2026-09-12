"""Opaque Value shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    reject_cycles,
    require_identifier,
    require_string,
)
from ..scientific_reference.models import ScientificReference


class OpaqueValue(ContractModel):
    contract_id = "TLC-HC-OPAQUE-VALUE@1.0.0"
    required_fields = frozenset({"semantic_type_id", "payload", "source_reference"})
    optional_fields = frozenset({"encoding"})

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "OpaqueValue":
        reject_cycles(value)
        super().from_mapping(value)
        require_identifier(value["semantic_type_id"], "semantic_type_id")
        if not isinstance(value["source_reference"], Mapping):
            raise ContractValidationError("source_reference must be an object")
        ScientificReference.from_mapping(value["source_reference"])
        if "encoding" in value:
            require_string(value["encoding"], "encoding")
        return cls(value)
