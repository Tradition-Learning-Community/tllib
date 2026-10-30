"""Verify actual workflow path filters against representative PR changes."""

from __future__ import annotations

import fnmatch
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github/workflows"


def triggered_by(path: str) -> list[str]:
    matched = []
    for workflow in sorted(WORKFLOWS.glob("*.yml")):
        source = workflow.read_text(encoding="utf-8").split("permissions:", 1)[0]
        patterns = re.findall(r"^\s+- '([^']+)'\s*$", source, flags=re.MULTILINE)
        if any(fnmatch.fnmatch(path, pattern) for pattern in patterns):
            matched.append(workflow.name)
    return matched


class WorkflowScopeTests(unittest.TestCase):
    def test_documentation_change_skips_all_compilation(self) -> None:
        self.assertEqual(triggered_by("docs/v1/new-note.md"), [])

    def test_core_triggers_native_wheel_and_quality(self) -> None:
        self.assertEqual(
            triggered_by("include/tllib/core/result.hpp"),
            ["native-core.yml", "python-wheel.yml", "quality.yml"],
        )

    def test_python_triggers_native_bridge_wheel_and_quality(self) -> None:
        self.assertEqual(
            triggered_by("bindings/python/tllib/__init__.py"),
            ["native-core.yml", "python-wheel.yml", "quality.yml"],
        )

    def test_specs_pipeline_checks_conformance_and_quality(self) -> None:
        self.assertEqual(
            triggered_by("tools/specs_pipeline.py"),
            ["pinned-specs.yml", "quality.yml"],
        )
        self.assertEqual(
            triggered_by("generated/specs/feature_index.json"), ["pinned-specs.yml"]
        )

    def test_editing_workflow_triggers_its_own_check(self) -> None:
        for name in (
            "binder-spike.yml",
            "native-core.yml",
            "pinned-specs.yml",
            "python-wheel.yml",
            "quality.yml",
        ):
            with self.subTest(workflow=name):
                self.assertIn(name, triggered_by(f".github/workflows/{name}"))


if __name__ == "__main__":
    unittest.main()
