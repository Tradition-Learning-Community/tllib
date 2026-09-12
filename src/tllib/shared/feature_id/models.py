"""Feature Identifier shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    reject_cycles,
    require_identifier,
)


class FeatureIdentifier(ContractModel):
    contract_id = "TLC-HC-FEATURE-ID@1.0.0"
    required_fields = frozenset({"value"})

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FeatureIdentifier":
        reject_cycles(value)
        super().from_mapping(value)
        require_identifier(value["value"], "value")
        return cls(value)


FeatureId = FeatureIdentifier
