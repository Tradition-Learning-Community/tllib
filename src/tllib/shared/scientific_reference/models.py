"""Scientific Reference shared contract."""

from collections.abc import Mapping
from typing import Any

from .._base import (
    ContractModel,
    ContractValidationError,
    reject_cycles,
    require_identifier,
    require_relative_path,
    require_string,
)


class ScientificReference(ContractModel):
    contract_id = "TLC-HC-SCIENTIFIC-REFERENCE@1.0.0"
    required_fields = frozenset({"source_path"})
    optional_fields = frozenset(
        {"object_id", "section", "subsection", "line_range", "source_commit"}
    )

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "ScientificReference":
        reject_cycles(value)
        super().from_mapping(value)
        require_relative_path(value["source_path"], "source_path")
        if "object_id" in value:
            require_identifier(value["object_id"], "object_id")
        for field in ("section", "subsection", "source_commit"):
            if field in value:
                require_string(value[field], field)
        if "line_range" in value and not isinstance(value["line_range"], Mapping):
            raise ContractValidationError("line_range must be an object")
        return cls(value)
