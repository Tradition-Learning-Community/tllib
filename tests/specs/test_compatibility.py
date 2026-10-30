"""No fake scientific support: version, Python, CMake and snapshot gates."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools import compatibility as compat

class CompatibilityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "include/tllib/generated").mkdir(parents=True)
        (self.root / "generated/specs").mkdir(parents=True)
        (self.root / "conformance").mkdir(parents=True)
        (self.root / "docs/v1").mkdir(parents=True)
        self.commit = "a"*40
        self.catalog_hash = "b"*64
        self.put("CMakeLists.txt", "project(tllib VERSION 0.1.0 LANGUAGES CXX)\nCOMPATIBILITY SameMinorVersion\n")
        self.put("pyproject.toml", '[project]\nversion = "0.1.0"\nrequires-python = ">=3.12,<3.13"\n')
        self.put("include/tllib/generated/feature_metadata.hpp",
                 f'inline constexpr std::string_view specs_commit = "{self.commit}";\n'
                 f'inline constexpr std::string_view catalog_sha256 = "{self.catalog_hash}";\n')
        self.put("specs.lock.json", json.dumps({"repository":"Tradition-Learning-Community/tllib-specs",
            "commit":self.commit,"catalog_sha256":self.catalog_hash,"model_version":"1.0.0"}))
        self.put("conformance/deprecations.json", json.dumps({"schema_version": "1.0", "entries": []}))
        self.put("generated/specs/feature_index.json", json.dumps({
            "specs_commit":self.commit,"catalog_sha256":self.catalog_hash,"model_version":"1.0.0"}))
    def put(self, name, content):
        (self.root / name).write_text(content,encoding="utf-8")
    def test_matching_metadata(self):
        r=compat.check(self.root)
        self.assertEqual(r["status"],"pass")
        self.assertFalse(r["cpp_abi_stable"])
        self.assertFalse(r["scientific_implementation_claim"])
    def test_breaking_metadata_fails(self):
        for p,v,expected in [
            ("CMakeLists.txt","project(tllib VERSION 1.0.0 LANGUAGES CXX)\nCOMPATIBILITY SameMinorVersion","VERSION_MISMATCH"),
            ("pyproject.toml",'[project]\nversion="0.1.0"\nrequires-python=">=3.9"',"PYTHON_SUPPORT_METADATA_MISMATCH"),
            ("include/tllib/generated/feature_metadata.hpp",
             f'inline constexpr std::string_view specs_commit = "{"c"*40}";',"SPECS_COMMIT_MISMATCH")
        ]:
            old=(self.root / p).read_text()
            self.put(p,v)
            with self.subTest(path=p):
                self.assertIn(expected,compat.check(self.root)["diagnostics"])
            self.put(p,old)
    def test_deprecation_requires_documented_migration_and_later_version(self):
        entry = {
            "symbol": "tllib.legacy",
            "deprecated_in": "0.1.0",
            "remove_no_earlier_than": "0.2.0",
            "replacement": "tllib.new_api",
            "migration_note": "docs/v1/LEGACY-MIGRATION.md",
        }
        path = "conformance/deprecations.json"
        self.put(path, json.dumps({"schema_version": "1.0", "entries": [entry]}))
        self.assertIn("MISSING_MIGRATION_NOTE", compat.check(self.root)["diagnostics"])
        self.put("docs/v1/LEGACY-MIGRATION.md", "Synthetic migration fixture only.\n")
        self.assertEqual(compat.check(self.root)["deprecated_symbol_count"], 1)
        self.assertEqual(compat.check(self.root)["status"], "pass")
        entry["remove_no_earlier_than"] = "0.1.0"
        self.put(path, json.dumps({"schema_version": "1.0", "entries": [entry]}))
        self.assertIn("INVALID_DEPRECATION_ENTRY", compat.check(self.root)["diagnostics"])

    def test_unlocked_catalog_mismatch_blocks(self):
        self.put("generated/specs/feature_index.json",json.dumps({"specs_commit":self.commit,
            "catalog_sha256":"0"*64,"model_version":"1.0.0"}))
        self.assertIn("SPECS_CATALOG_SHA256_MISMATCH",compat.check(self.root)["diagnostics"])

if __name__ == "__main__":
    unittest.main()
