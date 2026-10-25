"""Offline verifier/codegen/conformance contract tests with a synthetic committed handoff.

The tests do NOT execute any data from the handoff, or require network services.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import specs_pipeline as pipeline  # noqa: E402

FID = "TLC-FC-00-MASTER-001"
CID = "TLC-HC-FEATURE-ID"
STATUS = {"package": "finalized", "scientific": "partially_defined", "execution": "structural_only"}

def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pipeline.canonical(value))

def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

class SyntheticCase(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.specs, self.tllib = base / "specs", base / "tllib"
        self.specs.mkdir()
        self.tllib.mkdir()
        git(self.specs, "init")
        git(self.specs, "config", "user.email", "test@example.invalid")
        git(self.specs, "config", "user.name", "test")
        shared_base = self.specs / "handoff" / "shared" / CID
        feature_base = self.specs / "handoff" / "features" / FID
        self.feature_base = feature_base
        shared_files = ["manifest.json", "contract.json", "acceptance.json", "traceability.json"]
        write_json(shared_base / "manifest.json", {
            "schema_version": "1.0", "package_version": "1.0.0", "shared_contract_id": CID,
            "files": shared_files,
        })
        write_json(shared_base / "contract.json", {"shared_contract": {"shared_contract_id": CID}})
        write_json(shared_base / "acceptance.json", {"applies_to": CID, "tests": [{"test_id": "HC-FID-001"}]})
        write_json(shared_base / "traceability.json", {"applies_to": CID})
        write_json(feature_base / "manifest.json", {
            "schema_version": "1.0", "package_version": "1.0.0", "feature_id": FID,
            "domain": "master", "statuses": STATUS, "files": shared_files,
            "shared_dependencies": [{"shared_contract_id": CID, "version": "1.0.0"}],
            "examples": {"present": False, "file": None},
        })
        write_json(feature_base / "contract.json", {
            "schema_version": "1.0", "package_version": "1.0.0",
            "feature": {"feature_id": FID},
        })
        write_json(feature_base / "acceptance.json", {
            "schema_version": "1.0", "package_version": "1.0.0",
            "applies_to": FID, "tests": [{"test_id": "MASTER-001-A01"}],
        })
        write_json(feature_base / "traceability.json", {
            "schema_version": "1.0", "package_version": "1.0.0", "applies_to": FID,
        })
        domain_entry = {"domain": "master", "domain_index": 0,
                        "feature_count": 1, "catalog_path": "handoff/domains/master/catalog.json"}
        feature_entry = {
            "feature_id": FID, "domain": "master", "path": f"handoff/features/{FID}",
            "package_version": "1.0.0", "statuses": STATUS, "examples_present": False,
            "shared_dependencies": [{"shared_contract_id": CID, "version": "1.0.0"}],
            "package_sha256": "a" * 64, "descriptor_sha256": "b" * 64,
            "manifest_path": f"handoff/features/{FID}/manifest.json",
        }
        write_json(self.specs / "handoff/domains/master/catalog.json", {
            "domain": "master", "domain_index": 0, "expected_feature_count": 1,
            "ordered_feature_ids": [FID], "statuses": {"population": "complete", "validation": "validated"},
            "feature_packages": [{"feature_id": FID, "path": f"handoff/features/{FID}",
                                  "package_version": "1.0.0"}],
        })
        self.catalog = {
            "schema_version": "1.0", "model_version": "1.0.0", "catalog_status": "finalized",
            "domains": [domain_entry],
            "shared_contracts": [{"shared_contract_id": CID, "version": "1.0.0", "dependencies": []}],
            "features": [feature_entry],
            "summary": {"feature_count": 1, "domain_count": 1, "shared_contract_count": 1,
                        "package_statuses": {"finalized": 1},
                        "scientific_statuses": {"partially_defined": 1},
                        "execution_statuses": {"structural_only": 1}},
        }
        write_json(self.specs / "handoff/catalog.json", self.catalog)
        git(self.specs, "add", "handoff")
        git(self.specs, "commit", "-m", "synthetic pinned snapshot")
        result = subprocess.run(["git", "-C", str(self.specs), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=True)
        self.commit = result.stdout.strip()
        self.lock = {
            "schema_version": "1.0", "repository": pipeline.EXPECTED_REPOSITORY,
            "commit": self.commit, "handoff_catalog_path": "handoff/catalog.json",
            "catalog_sha256": hashlib.sha256((self.specs / "handoff/catalog.json").read_bytes()).hexdigest(),
            "catalog_schema_version": "1.0", "model_version": "1.0.0",
            "verification": {"name": "tllib-offline-handoff-verifier", "version": "1.0.0",
                             "hash_algorithm": "sha256", "git_object_integrity": "required"},
        }
        self.lock_path = self.tllib / "specs.lock.json"
        self.decisions_path = self.tllib / "conformance/decisions.json"
        write_json(self.lock_path, self.lock)
        write_json(self.decisions_path, {
            "schema_version": "1.0", "specs_commit": self.commit,
            "features": [{"feature_id": FID, "disposition": "unimplemented",
                          "reason": "No feature implementation in synthetic test.", "evidence": []}],
        })

    def validate(self):
        lock, root, catalog = pipeline.verify_lock(self.lock_path, self.specs)
        return lock, pipeline.validate_catalog(lock, root, catalog)

    def check_error(self, code, callback):
        with self.assertRaises(pipeline.PipelineError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code, str(caught.exception))

    def test_verification_generation_and_no_implicit_support(self):
        lock, index = self.validate()
        self.assertEqual(set(index["features"]), {FID})
        self.assertEqual(index["acceptance_cases"][FID][0]["test_id"], "MASTER-001-A01")
        generated = pipeline.generated(lock, index)
        self.assertEqual(len(generated), 2)
        pipeline.write_generated(generated, self.tllib, False)
        pipeline.write_generated(generated, self.tllib, True)
        original = generated.copy()
        self.assertEqual(original, pipeline.generated(lock, index))
        parsed = json.loads(generated["generated/specs/feature_index.json"])
        self.assertEqual(parsed["features"][0]["statuses"]["execution"], "structural_only")
        report, markdown, status = pipeline.report(lock, index, self.decisions_path, False)
        self.assertEqual(status, 0)
        self.assertEqual(report["feature_count"], 1)
        self.assertEqual(report["summary"]["unimplemented"], 1)
        self.assertIn(FID, markdown)
        release_report, _, release_status = pipeline.report(lock, index, self.decisions_path, True)
        self.assertEqual(release_status, 1)
        self.assertEqual(release_report["diagnostics"][0]["code"], "RELEASE_NOT_READY")
        output = self.tllib / "generated/specs/feature_index.json"
        output.write_bytes(b"corrupted")
        self.check_error("GENERATED_DRIFT", lambda: pipeline.write_generated(generated, self.tllib, True))

    def test_hash_commit_and_version_mismatch(self):
        altered = dict(self.lock, catalog_sha256="0" * 64)
        write_json(self.lock_path, altered)
        self.check_error("CATALOG_HASH_MISMATCH",
                         lambda: pipeline.verify_lock(self.lock_path, self.specs))
        altered = dict(self.lock, commit="0" * 40)
        write_json(self.lock_path, altered)
        self.check_error("COMMIT_MISMATCH", lambda: pipeline.verify_lock(self.lock_path, self.specs))
        altered = dict(self.lock, model_version="9.0.0")
        write_json(self.lock_path, altered)
        self.check_error("VERSION_MISMATCH", lambda: pipeline.verify_lock(self.lock_path, self.specs))
        altered = dict(self.lock, repository="wrong/repository")
        write_json(self.lock_path, altered)
        self.check_error("INVALID_LOCK", lambda: pipeline.verify_lock(self.lock_path, self.specs))

    def test_uncommitted_corrupt_bundle_and_escape(self):
        original = (self.feature_base / "contract.json").read_bytes()
        (self.feature_base / "contract.json").write_bytes(b"{ invalid json")
        self.check_error("DIRTY_HANDOFF", lambda: self.validate())
        (self.feature_base / "contract.json").write_bytes(original)
        root = pipeline.Handoff(self.specs)
        for forbidden in ("handoff/../secret.json", "handoff//catalog.json",
                          "handoff/features/./feature", "handoff/../../etc/passwd",
                          "handoff\\catalog.json", "/handoff/catalog.json"):
            self.check_error("UNSAFE_PATH", lambda forbidden=forbidden: root.bytes(forbidden))
        (self.specs / "handoff" / "danger").symlink_to(self.tllib)
        self.check_error("SYMLINK", lambda: root.bytes("handoff/danger/catalog.json"))

    def test_missing_new_decision_is_an_error(self):
        lock, index = self.validate()
        other = "TLC-FC-00-MASTER-002"
        index["features"][other] = dict(index["features"][FID], feature_id=other,
                                        path=f"handoff/features/{other}")
        index["acceptance"][other] = ["MASTER-002-A01"]
        report, _, result = pipeline.report(lock, index, self.decisions_path, False)
        self.assertEqual(result, 1)
        self.assertEqual(report["diagnostics"][0]["code"], "MISSING_DECISION")
        self.assertEqual(report["feature_count"], 2)

    def test_false_evidence_cannot_turn_into_scientific_coverage(self):
        lock, index = self.validate()
        write_json(self.decisions_path, {
            "schema_version": "1.0", "specs_commit": self.commit,
            "features": [{"feature_id": FID, "disposition": "covered",
                          "reason": "Pretend the feature works.", "evidence": []}],
        })
        report, _, result = pipeline.report(lock, index, self.decisions_path, False)
        self.assertEqual(result, 1)
        self.assertEqual(report["summary"]["invalid"], 1)
        self.assertEqual(report["diagnostics"][0]["code"], "MISSING_ACCEPTANCE_PROOF")

    def test_trusted_ctest_evidence_required_for_structural_claim(self):
        lock, index = self.validate()
        artifact = self.tllib / "tests" / "feature_acceptance.cpp"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("// Owned by tllib, not by tllib-specs\n", encoding="utf-8")
        junit = self.tllib / "ctest-results.xml"
        junit.write_text('<testsuite><testcase name="structural-fixture" /></testsuite>', encoding="utf-8")
        proof = {"test_id": "MASTER-001-A01", "result": "passed",
                 "artifact": "tests/feature_acceptance.cpp", "ctest_name": "structural-fixture"}
        write_json(self.decisions_path, {
            "schema_version": "1.0", "specs_commit": self.commit,
            "features": [{"feature_id": FID, "disposition": "structural",
                          "reason": "Verified structural acceptance only.", "evidence": [proof]}],
        })
        missing, _, state = pipeline.report(lock, index, self.decisions_path, False)
        self.assertEqual(state, 1)
        self.assertEqual(missing["diagnostics"][0]["code"], "MISSING_ACCEPTANCE_PROOF")
        accepted, _, state = pipeline.report(lock, index, self.decisions_path, True, junit)
        self.assertEqual(state, 0)
        self.assertEqual(accepted["summary"]["structural"], 1)
        junit.write_text('<testsuite><testcase name="structural-fixture"><failure /></testcase></testsuite>',
                         encoding="utf-8")
        rejected, _, state = pipeline.report(lock, index, self.decisions_path, True, junit)
        self.assertEqual(state, 1)
        self.assertEqual(rejected["summary"]["invalid"], 1)
        junit.write_text('<!DOCTYPE foo><testsuite />', encoding="utf-8")
        self.check_error("INVALID_TEST_RESULTS",
                         lambda: pipeline.report(lock, index, self.decisions_path, False, junit))

    def test_explicit_invalid_decision_cannot_pass_gate(self):
        lock, index = self.validate()
        write_json(self.decisions_path, {
            "schema_version": "1.0", "specs_commit": self.commit,
            "features": [{"feature_id": FID, "disposition": "invalid",
                          "reason": "Unresolved invalid runtime state.", "evidence": []}],
        })
        report, _, result = pipeline.report(lock, index, self.decisions_path, False)
        self.assertEqual(result, 1)
        self.assertEqual(report["diagnostics"][0]["code"], "INVALID_DECISION")

    def test_manifest_status_and_shared_cycle_detected(self):
        lock, handoff, catalog = pipeline.verify_lock(self.lock_path, self.specs)
        altered = json.loads(json.dumps(catalog))
        altered["features"][0]["statuses"]["execution"] = "unknown"
        self.check_error("INVALID_STATUS",
                         lambda: pipeline.validate_catalog(lock, handoff, altered))
        altered = json.loads(json.dumps(catalog))
        altered["shared_contracts"][0]["dependencies"] = [
            {"shared_contract_id": CID, "version": "1.0.0"}]
        self.check_error("CYCLIC_DEPENDENCY",
                         lambda: pipeline.validate_catalog(lock, handoff, altered))
        altered = json.loads(json.dumps(catalog))
        altered["features"][0]["domain"] = "unknown"
        self.check_error("UNKNOWN_DOMAIN",
                         lambda: pipeline.validate_catalog(lock, handoff, altered))

    def test_reject_duplicate_json_and_deep_nesting(self):
        self.check_error("INVALID_JSON", lambda: pipeline.parse_json(b'{"a":1,"a":2}', "duplicate"))
        self.check_error("INVALID_JSON", lambda: pipeline.parse_json(b'{"a":NaN}', "non-finite"))
        deeply_nested = b"[" * 100 + b"0" + b"]" * 100
        self.check_error("INVALID_JSON", lambda: pipeline.parse_json(deeply_nested, "deep"))

if __name__ == "__main__":
    unittest.main()
