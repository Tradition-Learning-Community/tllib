"""Tests for safe Feature Handoff conformance reporting."""

import json
from collections.abc import Mapping
from pathlib import Path

import pytest

from tllib.conformance import (
    HandoffLoadError,
    ImplementationBinding,
    build_report,
    load_handoffs,
)
from tllib.conformance.__main__ import main
from tllib.conformance.report import write_report


def _feature(root: Path, feature_id: str, tests: list[dict[str, object]]) -> None:
    package = root / "features" / feature_id
    package.mkdir(parents=True)
    (package / "manifest.json").write_text(
        json.dumps(
            {
                "feature_id": feature_id,
                "statuses": {"execution": "structural_only"},
            }
        ),
        encoding="utf-8",
    )
    (package / "acceptance.json").write_text(
        json.dumps({"applies_to": feature_id, "tests": tests}), encoding="utf-8"
    )


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


def test_loads_scenarios_and_reports_explicit_coverage(tmp_path: Path) -> None:
    _feature(tmp_path, "TLC-FC-00-MASTER-001", [_scenario("A-2"), _scenario("A-1")])
    _feature(tmp_path, "TLC-FC-00-MASTER-002", [_scenario("B-1")])

    handoffs = load_handoffs(tmp_path)
    report = build_report(
        handoffs,
        [
            ImplementationBinding(
                "TLC-FC-00-MASTER-001",
                "tllib.domains.master.operations.describe",
                frozenset({"A-1"}),
            )
        ],
    )

    assert report["summary"] == {
        "covered": 1,
        "not_covered": 1,
        "blocked": 1,
        "total": 3,
    }
    scenarios = report["scenarios"]
    assert isinstance(scenarios, list)
    assert [scenario["status"] for scenario in scenarios] == [
        "not_covered",
        "covered",
        "blocked",
    ]
    assert isinstance(handoffs[0].scenarios[0].given, Mapping)
    assert handoffs[0].scenarios[0].given["value"] == "input"
    with pytest.raises(TypeError):
        handoffs[0].scenarios[0].given["value"] = "changed"  # type: ignore[index]


@pytest.mark.parametrize(
    "acceptance",
    ["{", json.dumps({"applies_to": "TLC-FC-00-MASTER-001", "tests": [{}]})],
)
def test_rejects_corrupted_handoff_fixtures(tmp_path: Path, acceptance: str) -> None:
    package = tmp_path / "features" / "TLC-FC-00-MASTER-001"
    package.mkdir(parents=True)
    (package / "manifest.json").write_text(
        json.dumps(
            {
                "feature_id": "TLC-FC-00-MASTER-001",
                "statuses": {"execution": "structural_only"},
            }
        ),
        encoding="utf-8",
    )
    (package / "acceptance.json").write_text(acceptance, encoding="utf-8")

    with pytest.raises(HandoffLoadError):
        load_handoffs(tmp_path)


def test_report_is_deterministic(tmp_path: Path) -> None:
    _feature(tmp_path, "TLC-FC-00-MASTER-002", [_scenario("B-1")])
    _feature(tmp_path, "TLC-FC-00-MASTER-001", [_scenario("A-1")])

    report = build_report(load_handoffs(tmp_path))
    first = tmp_path / "one.json"
    second = tmp_path / "two.json"
    write_report(report, first)
    write_report(build_report(load_handoffs(tmp_path)), second)

    assert first.read_bytes() == second.read_bytes()


def test_cli_writes_report_and_rejects_corrupt_input(tmp_path: Path) -> None:
    _feature(tmp_path, "TLC-FC-00-MASTER-001", [_scenario("A-1")])
    report_path = tmp_path / "build" / "conformance.json"

    assert main(["--handoff", str(tmp_path), "--report", str(report_path)]) == 0
    assert (
        json.loads(report_path.read_text(encoding="utf-8"))["summary"]["blocked"] == 1
    )
    (tmp_path / "features" / "TLC-FC-00-MASTER-001" / "acceptance.json").write_text(
        "{", encoding="utf-8"
    )
    assert main(["--handoff", str(tmp_path), "--report", str(report_path)]) == 2
