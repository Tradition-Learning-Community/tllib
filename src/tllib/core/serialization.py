"""Canonical JSON serialization for shared tllib primitives."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from typing import Any, cast


def _to_json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_dict"):
        return _to_json_value(value.to_dict())
    if is_dataclass(value):
        return _to_json_value(asdict(cast(Any, value)))
    if isinstance(value, dict):
        return {
            str(key): _to_json_value(item)
            for key, item in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_to_json_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    raise TypeError(f"Unsupported value for JSON serialization: {type(value)!r}")


def to_canonical_json(value: Any) -> str:
    """Serialize a supported value deterministically as UTF-8 JSON text."""
    return json.dumps(
        _to_json_value(value),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def from_json(text: str) -> Any:
    """Decode JSON text; callers choose the domain type to reconstruct."""
    return json.loads(text)
