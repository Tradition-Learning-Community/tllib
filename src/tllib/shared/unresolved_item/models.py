"""Unresolved Item shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    reject_cycles,
    require_enum,
    require_identifier,
    require_string,
)
from ..scientific_reference.models import ScientificReference


class UnresolvedItem(ContractModel):
    contract_id = "TLC-HC-UNRESOLVED-ITEM@1.0.0"
    required_fields = frozenset(
        {
            "unresolved_id",
            "classification",
            "source_reference",
            "blocking_scope",
            "status",
        }
    )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "UnresolvedItem":
        reject_cycles(value)
        super().from_mapping(value)
        require_identifier(value["unresolved_id"], "unresolved_id")
        for field in ("classification", "blocking_scope"):
            require_string(value[field], field)
        if not isinstance(value["source_reference"], Mapping):
            raise ContractValidationError("source_reference must be an object")
        ScientificReference.from_mapping(value["source_reference"])
        require_enum(
            value["status"],
            "status",
            frozenset({"preserved_unresolved", "external_provider_required"}),
        )
        return cls(value)
