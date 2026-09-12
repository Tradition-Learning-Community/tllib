"""Traceability shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import ContractModel, ContractValidationError, reject_cycles, require_list

_FIELDS = frozenset(
    {
        "scientific_sources",
        "mathematical_contracts",
        "source_irs",
        "finalized_irs",
        "algorithm_specifications",
        "test_plans",
        "acceptance_oracles",
        "scientific_decisions",
    }
)


class Traceability(ContractModel):
    contract_id = "TLC-HC-TRACEABILITY@1.0.0"
    required_fields = _FIELDS

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Traceability":
        reject_cycles(value)
        super().from_mapping(value)
        for field in _FIELDS:
            require_list(value[field], field)
            if len(value[field]) != len({repr(item) for item in value[field]}):
                raise ContractValidationError(f"{field} must not contain duplicates")
        return cls(value)
