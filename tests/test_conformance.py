"""Tests for safe, catalog-driven Feature Handoff conformance."""

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from tllib.conformance import (
    HandoffLoadError,
    ImplementationBinding,
    build_report,
    load_bindings,
    load_handoffs,
)
from tllib.conformance.__main__ import main
from tllib.conformance.report import write_report

FILES = (
    "README.md",
    "manifest.json",
    "contract.json",
    "acceptance.json",
    "traceability.json",
)


def _canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()


def _package_sha(package: Path, feature_id: str) -> str:
    digest = hashlib.sha256()
    for name in sorted(FILES):
        path = package / name
        relative = f"handoff/features/{feature_id}/{name}"
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
        digest.update(b"\n")
    return digest.hexdigest()


def _scenario(identifier: str) -> dict[str, object]:
    return {
        "test_id": identifier,
        "applies_to": "DESCRIBE",
        "category": "valid_input",
        "given": {"value": "input"},
        "when": "The operation is invoked.",
        "expect": {"accepted": True},
        "source_basis": ["oracle.yaml"],
    }


def _feature(
    root: Path,
    feature_id: str,
    tests: list[dict[str, object]],
    *,
    domain: str = "master",
) -> dict[str, object]:
    package = root / "features" / feature_id
    package.mkdir(parents=True)
    manifest = {
        "schema_version": "1.0",
        "package_version": "1.0.0",
        "feature_id": feature_id,
        "title": feature_id,
        "domain": domain,
        "statuses": {
            "package": "finalized",
            "scientific": "preserved_unresolved",
            "execution": "structural_only",
        },
        "files": list(FILES),
        "shared_dependencies": [],
        "examples": {"present": False, "file": None},
    }
    contract = {
        "schema_version": "1.0",
        "package_version": "1.0.0",
        "feature": {"feature_id": feature_id, "title": feature_id, "domain": domain},
    }
    acceptance = {
        "schema_version": "1.0",
        "package_version": "1.0.0",
        "applies_to": feature_id,
        "tests": tests,
    }
    traceability = {
        "schema_version": "1.0",
        "package_version": "1.0.0",
        "applies_to": feature_id,
    }
    (package / "README.md").write_text(feature_id, encoding="utf-8")
    for name, value in (
        ("manifest.json", manifest),
        ("contract.json", contract),
        ("acceptance.json", acceptance),
        ("traceability.json", traceability),
    ):
        (package / name).write_text(json.dumps(value), encoding="utf-8")

    package_hash = _package_sha(package, feature_id)
    descriptor = {
        "feature_id": feature_id,
        "domain": domain,
        "path": f"handoff/features/{feature_id}",
        "package_version": "1.0.0",
        "statuses": manifest["statuses"],
        "examples_present": False,
        "shared_dependencies": [],
        "package_sha256": package_hash,
    }
    return {
        **descriptor,
        "manifest_path": f"handoff/features/{feature_id}/manifest.json",
        "descriptor_sha256": _canonical_sha256(descriptor),
        "deprecation": None,
        "substitution": None,
    }


def _catalog(root: Path, features: list[dict[str, object]]) -> None:
    root.mkdir(exist_ok=True)
    (root / "catalog.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "model_version": "1.0.0",
                "features": features,
                "summary": {"feature_count": len(features)},
            }
        ),
        encoding="utf-8",
    )


def test_loads_catalogued_scenarios_and_reports_explicit_coverage(
    tmp_path: Path,
) -> None:
    root = tmp_path / "handoff"
    first = _feature(
        root, "TLC-FC-00-MASTER-001", [_scenario("A-2"), _scenario("A-1")]
    )
    second = _feature(root, "TLC-FC-00-MASTER-002", [_scenario("B-1")])
    _catalog(root, [first, second])

    handoffs = load_handoffs(root)
    report = build_report(
        handoffs,
        [
            ImplementationBinding(
                "TLC-FC-00-MASTER-001",
                "tllib.domains.master.operations.describe",
                frozenset({"A-1"}),
            ),
            ImplementationBinding(
                "TLC-FC-00-MASTER-002",
                "unavailable",
                blocked_reason="structural only",
            ),
        ],
    )

    assert report["summary"] == {
        "covered": 1,
        "not_covered": 1,
        "blocked": 1,
        "unqualified": 0,
        "total": 3,
        "feature_count": 2,
        "unqualified_feature_count": 0,
    }
    scenarios = report["scenarios"]
    assert isinstance(scenarios, list)
    assert [scenario["status"] for scenario in scenarios] == [
        "not_covered",
        "covered",
        "blocked",
    ]
    assert isinstance(handoffs[0].scenarios[0].given, Mapping)
    with pytest.raises(TypeError):
        handoffs[0].scenarios[0].given["value"] = "changed"  # type: ignore[index]


def test_catalog_population_and_hashes_are_enforced(tmp_path: Path) -> None:
    root = tmp_path / "handoff"
    feature = _feature(root, "TLC-FC-00-MASTER-001", [_scenario("A-1")])
    _catalog(root, [feature])

    (root / "features" / "TLC-FC-00-MASTER-001" / "README.md").write_text(
        "tampered", encoding="utf-8"
    )
    with pytest.raises(HandoffLoadError, match="fingerprint mismatch"):
        load_handoffs(root)


def test_report_is_deterministic(tmp_path: Path) -> None:
    root = tmp_path / "handoff"
    second = _feature(root, "TLC-FC-00-MASTER-002", [_scenario("B-1")])
    first_feature = _feature(root, "TLC-FC-00-MASTER-001", [_scenario("A-1")])
    _catalog(root, [first_feature, second])

    bindings = [
        ImplementationBinding(
            "TLC-FC-00-MASTER-001", "x", blocked_reason="not implemented"
        ),
        ImplementationBinding(
            "TLC-FC-00-MASTER-002", "x", blocked_reason="not implemented"
        ),
    ]
    report = build_report(load_handoffs(root), bindings)
    first = tmp_path / "one.json"
    second_path = tmp_path / "two.json"
    write_report(report, first)
    write_report(build_report(load_handoffs(root), bindings), second_path)

    assert first.read_bytes() == second_path.read_bytes()


def test_cli_fails_until_catalogue_features_are_qualified(tmp_path: Path) -> None:
    root = tmp_path / "handoff"
    feature = _feature(root, "TLC-FC-00-MASTER-001", [_scenario("A-1")])
    _catalog(root, [feature])
    report_path = tmp_path / "build" / "conformance.json"

    assert main(["--handoff", str(root), "--report", str(report_path)]) == 3
    assert (
        main(
            [
                "--handoff",
                str(root),
                "--report",
                str(report_path),
                "--allow-unqualified",
            ]
        )
        == 0
    )


def test_bindings_file_makes_qualification_explicit(tmp_path: Path) -> None:
    root = tmp_path / "handoff"
    feature = _feature(root, "TLC-FC-00-MASTER-001", [_scenario("A-1")])
    _catalog(root, [feature])
    bindings_path = tmp_path / "bindings.json"
    bindings_path.write_text(
        json.dumps(
            {
                "bindings": [
                    {
                        "feature_id": "TLC-FC-00-MASTER-001",
                        "target": "unavailable",
                        "covered_scenario_ids": [],
                        "blocked_reason": "structural only",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    bindings = load_bindings(bindings_path)
    report = build_report(load_handoffs(root), bindings)

    summary = report["summary"]
    assert isinstance(summary, dict)
    assert summary["unqualified_feature_count"] == 0


def test_domain_support_directory_is_snapshot_bound(tmp_path: Path) -> None:
    support = tmp_path / "domains"
    support.mkdir()
    payload = {
        "schema_version": "1.0",
        "specification_sha": "a" * 40,
        "domain": "master",
        "feature_ids": ["TLC-FC-00-MASTER-001"],
        "target": "unimplemented",
        "blocked_reason": "not implemented",
    }
    (support / "master.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )

    bindings = load_bindings(support, specification_sha="a" * 40)
    assert bindings[0].feature_id == "TLC-FC-00-MASTER-001"
    assert bindings[0].domain == "master"

    with pytest.raises(HandoffLoadError, match="snapshot diverges"):
        load_bindings(support, specification_sha="b" * 40)
