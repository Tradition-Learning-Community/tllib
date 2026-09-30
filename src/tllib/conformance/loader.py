"""Safe loader for Feature Handoff Package acceptance files."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from .model import AcceptanceScenario, FeatureHandoff, freeze_json

_MAX_FILE_BYTES = 1_000_000
_REQUIRED_SCENARIO_FIELDS = {
    "test_id",
    "applies_to",
    "category",
    "given",
    "when",
    "expect",
}


class HandoffLoadError(ValueError):
    """Raised when a handoff input is unsafe or does not have the required shape."""


def _safe_child(root: Path, child: Path) -> Path:
    """Resolve a direct child without permitting link or traversal escapes."""
    if child.is_symlink():
        raise HandoffLoadError(f"Symbolic links are not allowed: {child}")
    try:
        resolved = child.resolve(strict=True)
        resolved.relative_to(root)
    except (FileNotFoundError, ValueError) as exc:
        raise HandoffLoadError(f"Unsafe handoff path: {child}") from exc
    return resolved


def _read_json(path: Path, root: Path) -> object:
    safe_path = _safe_child(root, path)
    if not safe_path.is_file():
        raise HandoffLoadError(f"Expected a regular file: {path}")
    try:
        raw = safe_path.read_bytes()
    except OSError as exc:
        raise HandoffLoadError(f"Unable to read handoff file: {path}") from exc
    if len(raw) > _MAX_FILE_BYTES:
        raise HandoffLoadError(f"Handoff file exceeds {_MAX_FILE_BYTES} bytes: {path}")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HandoffLoadError(f"Invalid JSON in handoff file: {path}") from exc


def _object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise HandoffLoadError(f"{label} must be a JSON object")
    return value


def _string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise HandoffLoadError(f"{label} must be a non-empty string")
    return value


def _scenario(feature_id: str, value: object, path: Path) -> AcceptanceScenario:
    data = _object(value, f"Scenario in {path}")
    if not _REQUIRED_SCENARIO_FIELDS.issubset(data):
        missing = sorted(_REQUIRED_SCENARIO_FIELDS - set(data))
        raise HandoffLoadError(f"Scenario in {path} is missing fields: {missing}")
    basis = data.get("source_basis", [])
    if not isinstance(basis, list) or not all(
        isinstance(item, str) and item for item in basis
    ):
        raise HandoffLoadError(f"Scenario source_basis in {path} must be a string list")
    try:
        frozen_given = freeze_json(data["given"])
        frozen_when = freeze_json(data["when"])
        frozen_expect = freeze_json(data["expect"])
    except ValueError as exc:
        raise HandoffLoadError(
            f"Scenario data in {path} is not JSON-compatible"
        ) from exc
    return AcceptanceScenario(
        feature_id=feature_id,
        scenario_id=_string(data["test_id"], f"Scenario test_id in {path}"),
        operation_id=_string(data["applies_to"], f"Scenario applies_to in {path}"),
        category=_string(data["category"], f"Scenario category in {path}"),
        given=frozen_given,
        when=frozen_when,
        expect=frozen_expect,
        source_basis=tuple(basis),
    )


def load_handoffs(handoff_root: Path) -> tuple[FeatureHandoff, ...]:
    """Load direct feature packages from a trusted handoff root safely."""
    if handoff_root.is_symlink():
        raise HandoffLoadError(f"Symbolic links are not allowed: {handoff_root}")
    try:
        root = handoff_root.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HandoffLoadError(f"Handoff root does not exist: {handoff_root}") from exc
    features = root / "features"
    features = _safe_child(root, features)
    if not features.is_dir():
        raise HandoffLoadError(f"Handoff features directory is missing: {features}")

    handoffs: list[FeatureHandoff] = []
    seen_scenarios: set[str] = set()
    for package in sorted(features.iterdir(), key=lambda item: item.name):
        package = _safe_child(root, package)
        if not package.is_dir():
            raise HandoffLoadError(f"Feature package must be a directory: {package}")
        acceptance_path = package / "acceptance.json"
        manifest_path = package / "manifest.json"
        acceptance = _object(_read_json(acceptance_path, root), str(acceptance_path))
        manifest = _object(_read_json(manifest_path, root), str(manifest_path))
        feature_id = package.name
        if _string(acceptance.get("applies_to"), str(acceptance_path)) != feature_id:
            raise HandoffLoadError(
                f"Acceptance feature identity mismatch: {acceptance_path}"
            )
        if _string(manifest.get("feature_id"), str(manifest_path)) != feature_id:
            raise HandoffLoadError(
                f"Manifest feature identity mismatch: {manifest_path}"
            )
        statuses = _object(manifest.get("statuses"), str(manifest_path))
        execution_status = _string(statuses.get("execution"), str(manifest_path))
        tests = acceptance.get("tests")
        if not isinstance(tests, list):
            raise HandoffLoadError(
                f"Acceptance tests must be a list: {acceptance_path}"
            )
        scenarios = tuple(
            _scenario(feature_id, test, acceptance_path) for test in tests
        )
        for scenario in scenarios:
            if scenario.scenario_id in seen_scenarios:
                raise HandoffLoadError(
                    f"Duplicate acceptance scenario ID: {scenario.scenario_id}"
                )
            seen_scenarios.add(scenario.scenario_id)
        handoffs.append(FeatureHandoff(feature_id, execution_status, scenarios))
    return tuple(handoffs)
