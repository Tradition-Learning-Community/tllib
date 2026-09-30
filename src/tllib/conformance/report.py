"""Deterministic conformance report generation."""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping
from pathlib import Path

from .model import FeatureHandoff, ImplementationBinding

_STATUS_COVERED = "covered"
_STATUS_NOT_COVERED = "not_covered"
_STATUS_BLOCKED = "blocked"


def _bindings_by_feature(
    bindings: Iterable[ImplementationBinding], handoffs: tuple[FeatureHandoff, ...]
) -> Mapping[str, ImplementationBinding]:
    known_features = {handoff.feature_id for handoff in handoffs}
    result: dict[str, ImplementationBinding] = {}
    for binding in bindings:
        if binding.feature_id not in known_features:
            raise ValueError(
                "Implementation binding references unknown feature: "
                f"{binding.feature_id}"
            )
        if binding.feature_id in result:
            raise ValueError(f"Duplicate implementation binding: {binding.feature_id}")
        result[binding.feature_id] = binding
    return result


def build_report(
    handoffs: tuple[FeatureHandoff, ...],
    bindings: Iterable[ImplementationBinding] = (),
) -> dict[str, object]:
    """Build a stable report; coverage requires an explicit TLC-FC binding."""
    by_feature = _bindings_by_feature(bindings, handoffs)
    scenarios: list[dict[str, object]] = []
    counts: Counter[str] = Counter()
    for handoff in handoffs:
        binding = by_feature.get(handoff.feature_id)
        for scenario in handoff.scenarios:
            if binding is None:
                status = _STATUS_BLOCKED
                implementation: str | None = None
                justification = "No TLC-FC implementation is registered."
            elif binding.blocked_reason is not None:
                status = _STATUS_BLOCKED
                implementation = binding.target
                justification = binding.blocked_reason
            elif scenario.scenario_id in binding.covered_scenario_ids:
                status = _STATUS_COVERED
                implementation = binding.target
                justification = "Explicitly associated conformance test is registered."
            else:
                status = _STATUS_NOT_COVERED
                implementation = binding.target
                justification = (
                    "Implementation is registered but no conformance test covers "
                    "this scenario."
                )
            counts[status] += 1
            scenarios.append(
                {
                    "feature_id": scenario.feature_id,
                    "scenario_id": scenario.scenario_id,
                    "operation_id": scenario.operation_id,
                    "category": scenario.category,
                    "execution_status": handoff.execution_status,
                    "implementation": implementation,
                    "status": status,
                    "justification": justification,
                }
            )
    return {
        "schema_version": "1.0",
        "summary": {
            "covered": counts[_STATUS_COVERED],
            "not_covered": counts[_STATUS_NOT_COVERED],
            "blocked": counts[_STATUS_BLOCKED],
            "total": len(scenarios),
        },
        "scenarios": scenarios,
    }


def write_report(report: Mapping[str, object], report_path: Path) -> None:
    """Write a canonical JSON report with no volatile fields."""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
