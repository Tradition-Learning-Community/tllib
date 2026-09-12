"""Reference Collection shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    reject_cycles,
    require_enum,
)

_KINDS = frozenset(
    {
        "scalar",
        "optional",
        "sequence",
        "set",
        "ordered_set",
        "multiset",
        "map",
        "ordered_map",
    }
)


class ReferenceCollection(ContractModel):
    contract_id = "TLC-HC-REFERENCE-COLLECTION@1.0.0"
    required_fields = frozenset(
        {
            "kind",
            "membership",
            "cardinality",
            "ordering",
            "duplicates",
            "key_contract",
            "value_contract",
        }
    )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ReferenceCollection":
        reject_cycles(value)
        super().from_mapping(value)
        require_enum(value["kind"], "kind", _KINDS)
        for field in ("membership", "ordering", "duplicates"):
            if not isinstance(value[field], str):
                raise ContractValidationError(f"{field} must be a string")
        if not isinstance(value["cardinality"], Mapping):
            raise ContractValidationError("cardinality must be an object")
        cardinality = value["cardinality"]
        if (
            set(cardinality) != {"minimum", "maximum"}
            or not isinstance(cardinality["minimum"], int)
            or cardinality["minimum"] < 0
        ):
            raise ContractValidationError(
                "cardinality must contain a non-negative minimum and maximum"
            )
        if cardinality["maximum"] is not None and (
            not isinstance(cardinality["maximum"], int)
            or cardinality["maximum"] < cardinality["minimum"]
        ):
            raise ContractValidationError(
                "cardinality maximum must be null or >= minimum"
            )
        return cls(value)
