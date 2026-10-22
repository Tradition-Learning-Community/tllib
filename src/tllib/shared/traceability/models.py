"""Traceability shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    canonical_json,
    reject_cycles,
    require_identifier,
    require_list,
    require_relative_path,
    require_string,
)

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


def _validate_reference(value: Any, field: str) -> None:
    if not isinstance(value, Mapping):
        raise ContractValidationError(f"{field} entries must be objects")
    if "path" not in value or "role" not in value:
        raise ContractValidationError(f"{field} entries require path and role")
    require_relative_path(value["path"], f"{field}.path")
    require_string(value["role"], f"{field}.role")
    if "artifact_id" in value:
        require_identifier(value["artifact_id"], f"{field}.artifact_id")
    if "fingerprint" in value:
        fingerprint = value["fingerprint"]
        if not isinstance(fingerprint, Mapping):
            raise ContractValidationError(f"{field}.fingerprint must be an object")
        if set(fingerprint) != {"algorithm", "value"}:
            raise ContractValidationError(
                f"{field}.fingerprint requires algorithm and value"
            )
        require_string(fingerprint["algorithm"], f"{field}.fingerprint.algorithm")
        require_string(fingerprint["value"], f"{field}.fingerprint.value")


class Traceability(ContractModel):
    contract_id = "TLC-HC-TRACEABILITY@1.0.0"
    required_fields = _FIELDS

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "Traceability":
        reject_cycles(value)
        super().from_mapping(value)
        for field in _FIELDS:
            require_list(value[field], field)
            for item in value[field]:
                _validate_reference(item, field)
            serialized = [canonical_json(item) for item in value[field]]
            if len(serialized) != len(set(serialized)):
                raise ContractValidationError(f"{field} must not contain duplicates")
        return cls(value)
