"""Synthetic migration decisions; no real scientific data altered."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import specs_sync as sync

LOCK = {"model_version": "1.0.0", "catalog_schema_version": "1.0",
        "catalog_sha256": "a" * 64, "commit": "b" * 40}
FID = "TLC-FC-00-EXAMPLE-001"

class SnapshotDiffTests(unittest.TestCase):
    def inventory(self, index, lock=LOCK, files=None):
        return sync.compare({"domains": {}, "features": {}, "shared": {}}, index,
                            LOCK, lock, {}, files or {})

    def test_identical_is_stable_and_no_auto_lock_update(self):
        index = {"domains": {}, "features": {}, "shared": {}}
        first = sync.compare(index, index, LOCK, LOCK, {}, {})
        self.assertEqual(first["status"], "identical")
        self.assertFalse(first["lock_update_permitted_automatically"])
        self.assertEqual(sync.markdown(first), sync.markdown(first))
        self.assertEqual(json.dumps(first, sort_keys=True), json.dumps(first, sort_keys=True))

    def test_provenance_commit_mismatch_is_never_silent(self):
        index = {"domains": {}, "features": {}, "shared": {}}
        candidate = dict(LOCK, commit="c" * 40)
        report = sync.compare(index, index, LOCK, candidate, {}, {})
        self.assertEqual(report["status"], "review_required")
        self.assertEqual(report["changes"][0]["field"], "commit")
        self.assertEqual(report["changes"][0]["impact"], "manual_review_required")
        self.assertFalse(report["lock_update_permitted_automatically"])

    def test_additions_and_removals_never_imply_execution(self):
        added = self.inventory({"domains": {"new": {"feature_count": 1}},
                                "features": {FID: {"statuses": {"execution": "executable"}}},
                                "shared": {}})
        self.assertEqual(added["status"], "review_required")
        self.assertEqual(next(c["impact"] for c in added["changes"] if c["kind"] == "feature"),
                         "gap_unimplemented")
        self.assertFalse(added["compatible"])
        gone = sync.compare({"domains": {}, "features": {FID: {}}, "shared": {}},
                            {"domains": {}, "features": {}, "shared": {}},
                            LOCK, LOCK, {}, {})
        self.assertEqual(gone["changes"][0]["impact"], "breaking_or_removal")

    def test_status_contract_acceptance_versions_and_provenance(self):
        old = {"domains": {}, "shared": {}, "features": {
            FID: {"statuses": {"execution": "structural_only"}, "package_version": "1.0.0"}}}
        new = {"domains": {}, "shared": {}, "features": {
            FID: {"statuses": {"execution": "executable"}, "package_version": "2.0.0"}}}
        changed = sync.compare(old, new, LOCK, dict(LOCK, catalog_sha256="c"*64),
                               {"feature:"+FID+"/contract.json":{"path":"handoff/features/"+FID+"/contract.json",
                                    "kind":"feature","identity":FID,"sha256":"a"}},
                               {"feature:"+FID+"/contract.json":{"path":"handoff/features/"+FID+"/contract.json",
                                    "kind":"feature","identity":FID,"sha256":"b"}})
        self.assertTrue(any(c["field"].endswith("/contract.json") for c in changed["changes"]))
        self.assertTrue(any(c["field"] == "statuses" for c in changed["changes"]))
        self.assertTrue(any(c["field"] == "package_version" for c in changed["changes"]))
        self.assertTrue(all(c["impact"] == "manual_review_required" for c in changed["changes"]))
        self.assertIn("manual", sync.markdown(changed).lower())
        self.assertNotIn("automatically compatible", sync.markdown(changed))

if __name__ == "__main__":
    unittest.main()
