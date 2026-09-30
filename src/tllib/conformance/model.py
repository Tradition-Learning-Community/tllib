"""Immutable models for Feature Handoff acceptance scenarios."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TypeAlias

FrozenValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | tuple["FrozenValue", ...]
    | Mapping[str, "FrozenValue"]
)


def freeze_json(value: object) -> FrozenValue:
    """Recursively make a JSON-compatible value immutable."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, list):
        return tuple(freeze_json(item) for item in value)
    if isinstance(value, dict) and all(isinstance(key, str) for key in value):
        return MappingProxyType({key: freeze_json(item) for key, item in value.items()})
    raise ValueError("Acceptance values must be JSON-compatible")


@dataclass(frozen=True, slots=True)
class AcceptanceScenario:
    """One immutable acceptance scenario published by a Feature Handoff Package."""

    feature_id: str
    scenario_id: str
    operation_id: str
    category: str
    given: FrozenValue
    when: FrozenValue
    expect: FrozenValue
    source_basis: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureHandoff:
    """Validated feature handoff metadata and its acceptance scenarios."""

    feature_id: str
    execution_status: str
    scenarios: tuple[AcceptanceScenario, ...]


@dataclass(frozen=True, slots=True)
class ImplementationBinding:
    """Explicit association between one TLC-FC feature and runtime coverage."""

    feature_id: str
    target: str
    covered_scenario_ids: frozenset[str] = frozenset()
    blocked_reason: str | None = None

    def __post_init__(self) -> None:
        if not self.feature_id or not self.target:
            raise ValueError("Implementation bindings require a feature ID and target")
        if self.blocked_reason == "":
            raise ValueError("blocked_reason must be meaningful when supplied")
