"""Safe, catalog-driven loader for Feature Handoff Packages."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from .model import (
    AcceptanceScenario,
    FeatureHandoff,
    ImplementationBinding,
    freeze_json,
)

_MAX_FILE_BYTES = 2_000_000
_REQUIRED_PACKAGE_FILES = {
    "README.md",
    "manifest.json",
    "contract.json",
    "acceptance.json",
    "traceability.json",
}
_REQUIRED_SCENARIO_FIELDS = {
    "test_id",
    "applies_to",
    "category",
    "given",
    "when",
    "expect",
}


class HandoffLoadError(ValueError):
    """Raised when a handoff input is unsafe or inconsistent with the catalog."""


def _safe_child(root: Path, child: Path) -> Path:
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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _aggregate_package_hash(
    handoff_root: Path, package: Path, declared: tuple[str, ...]
) -> str:
    digest = hashlib.sha256()
    for name in sorted(declared):
        path = _safe_child(handoff_root, package / name)
        relative = (
            Path("handoff") / "features" / package.name / name
        ).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\n")
    return digest.hexdigest()


def _canonical_sha256(value: object) -> str:
    rendered = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(rendered).hexdigest()


def _declared_files(
    root: Path, package: Path, manifest: Mapping[str, object]
) -> tuple[str, ...]:
    value = manifest.get("files")
    if not isinstance(value, list) or not value or not all(
        isinstance(item, str) and item and "/" not in item and "\\" not in item
        for item in value
    ):
        raise HandoffLoadError(f"Invalid declared file list: {package}")
    declared = tuple(value)
    if len(declared) != len(set(declared)):
        raise HandoffLoadError(f"Duplicate declared file: {package}")
    if not _REQUIRED_PACKAGE_FILES.issubset(declared):
        raise HandoffLoadError(\n            f"Required handoff files are missing from manifest: {package}"\n        )
    actual: set[str] = set()
    for item in package.iterdir():
        safe = _safe_child(root, item)
        if safe.is_dir():
            raise HandoffLoadError(f"Feature package contains a directory: {item}")
        actual.add(item.name)
    if actual != set(declared):
        raise HandoffLoadError(
            f"Declared files differ from package files for {package.name}: "
            f"declared={sorted(declared)}, observed={sorted(actual)}"
        )
    return declared


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


def _catalog_entries(root: Path) -> tuple[Mapping[str, object], ...]:
    catalog_path = root / "catalog.json"
    catalog = _object(_read_json(catalog_path, root), str(catalog_path))
    if catalog.get("schema_version") != "1.0":
        raise HandoffLoadError("Unsupported global catalog schema_version")
    if catalog.get("model_version") != "1.0.0":
        raise HandoffLoadError("Unsupported global catalog model_version")
    features = catalog.get("features")
    if not isinstance(features, list) or not features:
        raise HandoffLoadError("Global catalog features must be a non-empty list")
    entries = tuple(_object(item, "Catalog feature") for item in features)
    ids = [_string(entry.get("feature_id"), "Catalog feature_id") for entry in entries]
    if len(ids) != len(set(ids)):
        raise HandoffLoadError("Global catalog contains duplicate feature identities")
    summary = _object(catalog.get("summary"), "Catalog summary")
    if summary.get("feature_count") != len(entries):
        raise HandoffLoadError("Catalog summary feature_count diverges")
    return entries


def load_handoffs(handoff_root: Path) -> tuple[FeatureHandoff, ...]:
    """Load exactly the feature population declared by handoff/catalog.json."""
    if handoff_root.is_symlink():
        raise HandoffLoadError(f"Symbolic links are not allowed: {handoff_root}")
    try:
        root = handoff_root.resolve(strict=True)
    except FileNotFoundError as exc:
        raise HandoffLoadError(f"Handoff root does not exist: {handoff_root}") from exc

    features_root = _safe_child(root, root / "features")
    if not features_root.is_dir():
        raise HandoffLoadError(\n            f"Handoff features directory is missing: {features_root}"\n        )

    entries = _catalog_entries(root)
    expected_ids = tuple(\n        _string(entry.get("feature_id"), "feature_id") for entry in entries\n    )
    observed_ids = tuple(
        sorted(
            item.name
            for item in features_root.iterdir()
            if _safe_child(root, item).is_dir()
        )
    )
    if set(observed_ids) != set(expected_ids):
        raise HandoffLoadError(
            "Catalog and physical feature population diverge: "
            f"catalog={sorted(expected_ids)}, observed={list(observed_ids)}"
        )

    handoffs: list[FeatureHandoff] = []
    seen_scenarios: set[str] = set()
    for entry in entries:
        feature_id = _string(entry.get("feature_id"), "Catalog feature_id")
        domain = _string(entry.get("domain"), f"Catalog domain for {feature_id}")
        expected_path = f"handoff/features/{feature_id}"
        if entry.get("path") != expected_path:
            raise HandoffLoadError(f"Unexpected package path for {feature_id}")
        if entry.get("manifest_path") != f"{expected_path}/manifest.json":
            raise HandoffLoadError(f"Unexpected manifest path for {feature_id}")

        package = _safe_child(root, features_root / feature_id)
        manifest_path = package / "manifest.json"
        contract_path = package / "contract.json"
        acceptance_path = package / "acceptance.json"
        traceability_path = package / "traceability.json"

        manifest = _object(_read_json(manifest_path, root), str(manifest_path))
        contract = _object(_read_json(contract_path, root), str(contract_path))
        acceptance = _object(_read_json(acceptance_path, root), str(acceptance_path))
        traceability = _object(
            _read_json(traceability_path, root), str(traceability_path)
        )

        if manifest.get("feature_id") != feature_id or manifest.get("domain") != domain:
            raise HandoffLoadError(f"Manifest identity mismatch: {feature_id}")
        package_version = _string(
            manifest.get("package_version"), f"Package version for {feature_id}"
        )
        if entry.get("package_version") != package_version:
            raise HandoffLoadError(f"Package version mismatch: {feature_id}")
        statuses = _object(manifest.get("statuses"), str(manifest_path))
        if entry.get("statuses") != statuses:
            raise HandoffLoadError(f"Catalog statuses diverge: {feature_id}")
        scientific_status = _string(statuses.get("scientific"), str(manifest_path))
        execution_status = _string(statuses.get("execution"), str(manifest_path))

        declared = _declared_files(root, package, manifest)
        package_hash = _aggregate_package_hash(root, package, declared)
        if entry.get("package_sha256") != package_hash:
            raise HandoffLoadError(f"Package fingerprint mismatch: {feature_id}")

        dependencies = manifest.get("shared_dependencies")
        if not isinstance(dependencies, list):
            raise HandoffLoadError(f"shared_dependencies must be a list: {feature_id}")
        descriptor = {
            "feature_id": feature_id,
            "domain": domain,
            "path": expected_path,
            "package_version": package_version,
            "statuses": dict(statuses),
            "examples_present": bool(
                _object(manifest.get("examples"), str(manifest_path)).get("present")
            ),
            "shared_dependencies": sorted(
                dependencies,
                key=lambda item: (
                    (\n                        str(item.get("shared_contract_id"))\n                        if isinstance(item, dict)\n                        else ""\n                    ),
                    str(item.get("version")) if isinstance(item, dict) else "",
                ),
            ),
            "package_sha256": package_hash,
        }
        if entry.get("descriptor_sha256") != _canonical_sha256(descriptor):
            raise HandoffLoadError(f"Descriptor fingerprint mismatch: {feature_id}")

        contract_feature = _object(contract.get("feature"), str(contract_path))
        if contract_feature.get("feature_id") != feature_id:
            raise HandoffLoadError(f"Contract identity mismatch: {feature_id}")
        if contract.get("package_version") != package_version:
            raise HandoffLoadError(f"Contract version mismatch: {feature_id}")
        if acceptance.get("applies_to") != feature_id:
            raise HandoffLoadError(f"Acceptance identity mismatch: {feature_id}")
        if acceptance.get("package_version") != package_version:
            raise HandoffLoadError(f"Acceptance version mismatch: {feature_id}")
        if traceability.get("applies_to") != feature_id:
            raise HandoffLoadError(f"Traceability identity mismatch: {feature_id}")
        if traceability.get("package_version") != package_version:
            raise HandoffLoadError(f"Traceability version mismatch: {feature_id}")

        tests = acceptance.get("tests")
        if not isinstance(tests, list):
            raise HandoffLoadError(\n                f"Acceptance tests must be a list: {acceptance_path}"\n            )
        scenarios = tuple(\n            _scenario(feature_id, test, acceptance_path) for test in tests\n        )
        for scenario in scenarios:
            if scenario.scenario_id in seen_scenarios:
                raise HandoffLoadError(
                    f"Duplicate acceptance scenario ID: {scenario.scenario_id}"
                )
            seen_scenarios.add(scenario.scenario_id)

        try:
            frozen_contract = freeze_json(dict(contract))
            frozen_traceability = freeze_json(dict(traceability))
        except ValueError as exc:
            raise HandoffLoadError(
                f"Contract or traceability is not JSON-compatible: {feature_id}"
            ) from exc
        handoffs.append(
            FeatureHandoff(
                feature_id=feature_id,
                domain=domain,
                package_version=package_version,
                scientific_status=scientific_status,
                execution_status=execution_status,
                contract=frozen_contract,
                traceability=frozen_traceability,
                scenarios=scenarios,
            )
        )
    return tuple(handoffs)


def load_bindings(path: Path) -> tuple[ImplementationBinding, ...]:
    """Load explicit runtime qualification decisions from a JSON file."""
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise HandoffLoadError(f"Unable to load bindings: {path}") from exc
    data = _object(value, "Bindings")
    rows = data.get("bindings")
    if not isinstance(rows, list):
        raise HandoffLoadError("Bindings file must contain a bindings list")
    bindings: list[ImplementationBinding] = []
    for raw in rows:
        row = _object(raw, "Binding")
        covered = row.get("covered_scenario_ids", [])
        if not isinstance(covered, list) or not all(
            isinstance(item, str) and item for item in covered
        ):
            raise HandoffLoadError("covered_scenario_ids must be a string list")
        blocked = row.get("blocked_reason")
        if blocked is not None and not isinstance(blocked, str):
            raise HandoffLoadError("blocked_reason must be a string or null")
        bindings.append(
            ImplementationBinding(
                feature_id=_string(row.get("feature_id"), "Binding feature_id"),
                target=_string(row.get("target"), "Binding target"),
                covered_scenario_ids=frozenset(covered),
                blocked_reason=blocked,
            )
        )
    return tuple(bindings)
