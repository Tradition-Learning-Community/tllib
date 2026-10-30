"""C++/Python structural parity: same machine-readable manifest and native results."""
import json
import os
from pathlib import Path
import subprocess
import unittest

from tllib import (
    DomainId, ExecutionStatus, FeatureId, TllibError, ValidationError,
    parse_execution_status,
)


def python_outcome(case):
    try:
        if case["kind"] == "feature":
            return "OK\t" + str(FeatureId(case["value"]))
        if case["kind"] == "domain":
            return "OK\t" + str(DomainId(case["value"]))
        if case["kind"] == "execution_status":
            return "OK\t" + parse_execution_status(case["value"]).value
        raise AssertionError("Unknown manifest case")
    except TllibError as error:
        assert isinstance(error, ValidationError)
        assert error.category == "validation"
        assert isinstance(error.context, dict)
        return "ERROR\t" + error.code


class IdentityParity(unittest.TestCase):
    def test_manifest_cpp_python(self):
        executable=os.environ.get("TLLIB_PARITY_EXECUTABLE")
        manifest=os.environ.get("TLLIB_PARITY_MANIFEST")
        if not executable or not manifest:
            self.skipTest("CMake sets both paths when running installed parity CTest")
        cases=json.loads(Path(manifest).read_text(encoding="utf-8"))["cases"]
        self.assertGreater(len(cases), 10)
        for case in cases:
            with self.subTest(kind=case["kind"], value=case["value"]):
                cpp=subprocess.run([executable,case["kind"],case["value"]],
                                   check=True, text=True,capture_output=True).stdout.strip()
                py=python_outcome(case)
                self.assertEqual(cpp,case["expected"])
                self.assertEqual(py,cpp)

    def test_structural_types_are_immutable_hashable(self):
        feature=FeatureId("TLC-FC-00-MASTER-005")
        self.assertEqual(feature,FeatureId(str(feature)))
        self.assertEqual(len({feature,FeatureId(str(feature))}),1)
        with self.assertRaises((AttributeError,TypeError)):
            feature.value="TLC-FC-00-MASTER-006"
        self.assertEqual(str(DomainId("low-data-architecture")),"low-data-architecture")
        self.assertEqual(parse_execution_status("structural_only"),ExecutionStatus.STRUCTURAL_ONLY)
        with self.assertRaises(ValidationError) as error:
            FeatureId("invalid")
        self.assertEqual(error.exception.code,"INVALID_IDENTIFIER")
        self.assertEqual(error.exception.category,"validation")
        self.assertIsNone(error.exception.feature_id)
        self.assertIsNone(error.exception.specs_provenance)
        self.assertEqual(error.exception.context,{})


if __name__=="__main__":
    unittest.main()
