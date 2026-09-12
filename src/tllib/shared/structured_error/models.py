"""Structured Error shared contract."""

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

_RECOVERABILITY = frozenset(
    {
        "recoverable",
        "retryable",
        "non_retryable",
        "implementation_defined",
        "not_applicable",
    }
)
_PUBLIC_RESULT = frozenset(
    {
        "error_only",
        "no_partial_result",
        "partial_result_allowed",
        "implementation_defined",
    }
)
_ATOMICITY = frozenset(
    {
        "no_observable_partial_result",
        "basic",
        "not_constrained",
        "implementation_defined",
        "not_applicable",
    }
)


class StructuredError(ContractModel):
    contract_id = "TLC-HC-STRUCTURED-ERROR@1.0.0"
    required_fields = frozenset(
        {
            "code",
            "category",
            "condition",
            "recoverability",
            "public_result",
            "failure_atomicity",
            "context",
            "transport",
        }
    )
    optional_fields = frozenset({"feature_id"})

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "StructuredError":
        reject_cycles(value)
        super().from_mapping(value)
        require_identifier(value["code"], "code")
        for field in ("category", "condition"):
            require_string(value[field], field)
        if "feature_id" in value:
            require_identifier(value["feature_id"], "feature_id")
        require_enum(value["recoverability"], "recoverability", _RECOVERABILITY)
        require_enum(value["public_result"], "public_result", _PUBLIC_RESULT)
        require_enum(value["failure_atomicity"], "failure_atomicity", _ATOMICITY)
        if not isinstance(value["context"], Mapping):
            raise ContractValidationError("context must be an object")
        require_enum(
            value["transport"], "transport", frozenset({"implementation_defined"})
        )
        return cls(value)
