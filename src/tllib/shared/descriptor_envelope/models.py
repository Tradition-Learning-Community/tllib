"""Descriptor Envelope shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    reject_cycles,
    require_feature_id,
    require_list,
    require_string,
)
from ..unresolved_item.models import UnresolvedItem


class DescriptorEnvelope(ContractModel):
    contract_id = "TLC-HC-DESCRIPTOR-ENVELOPE@1.0.0"
    required_fields = frozenset(
        {
            "feature_id",
            "representation",
            "references",
            "unresolved",
            "dependencies",
            "provenance",
            "status",
        }
    )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "DescriptorEnvelope":
        reject_cycles(value)
        super().from_mapping(value)
        require_feature_id(value["feature_id"], "feature_id")
        require_string(value["representation"], "representation")
        if not isinstance(value["references"], (Mapping, list, tuple)):
            raise ContractValidationError(
                "references must preserve a collection carrier"
            )
        require_list(value["unresolved"], "unresolved")
        for item in value["unresolved"]:
            if not isinstance(item, Mapping):
                raise ContractValidationError("unresolved entries must be objects")
            UnresolvedItem.from_mapping(item)
        require_list(value["dependencies"], "dependencies")
        if not isinstance(value["provenance"], Mapping):
            raise ContractValidationError("provenance must be an object")
        if not isinstance(value["status"], Mapping):
            raise ContractValidationError("status must be an object")
        return cls(value)
