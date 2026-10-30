"""C++/Python structural parity: same machine-readable manifest and native results."""
import ast
import json
import os
from pathlib import Path
import subprocess
import unittest

import tllib
from tllib import (
    DomainId, ExecutionStatus, FeatureId, TllibError, ValidationError,
    ProviderRequiredError, ProviderExecutionError, IncompatibleSpecsError,
    CancelledError, IndeterminateOutcomeError,
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
        manifest_data=json.loads(Path(manifest).read_text(encoding="utf-8"))
        cases=manifest_data["cases"]
        symbols=manifest_data["symbols"]
        self.assertEqual(set(symbols),{case["kind"] for case in cases})
        for kind,mapping in symbols.items():
            with self.subTest(mapping=kind):
                self.assertTrue(mapping["native"].startswith("tllib::core::"))
                self.assertTrue(mapping["python"].startswith("tllib."))
                self.assertTrue(hasattr(tllib,mapping["python"].split(".")[1]))
                self.assertIn(mapping["kind"],("structural_identity","structural_status"))
        self.assertGreater(len(cases), 10)
        for case in cases:
            with self.subTest(kind=case["kind"], value=case["value"]):
                cpp=subprocess.run([executable,case["kind"],case["value"]],
                                   check=True, text=True,capture_output=True).stdout.strip()
                py=python_outcome(case)
                self.assertEqual(cpp,case["expected"])
                self.assertEqual(py,cpp)

    def test_public_stubs_match_exported_symbols(self):
        stub_path=Path(tllib.__file__).with_name("__init__.pyi")
        self.assertTrue(stub_path.is_file(),"PEP 561 typing must ship in wheel and CMake build")
        self.assertTrue(stub_path.with_name("py.typed").is_file())
        tree=ast.parse(stub_path.read_text(encoding="utf-8"))
        declared=set()
        for node in tree.body:
            if isinstance(node,(ast.ClassDef,ast.FunctionDef)):
                declared.add(node.name)
            elif isinstance(node,ast.AnnAssign) and isinstance(node.target,ast.Name):
                declared.add(node.target.id)
        for name in tllib.__all__:
            with self.subTest(public=name):
                self.assertTrue(hasattr(tllib,name))
                self.assertIn(name,declared)
        self.assertTrue(issubclass(ProviderRequiredError,TllibError))
        self.assertTrue(issubclass(ProviderExecutionError,TllibError))
        self.assertTrue(issubclass(IncompatibleSpecsError,TllibError))
        self.assertTrue(issubclass(CancelledError,TllibError))
        self.assertTrue(issubclass(IndeterminateOutcomeError,TllibError))

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
        with self.assertRaises(AttributeError):
            error.exception.code="SILENTLY_MUTATED"
        with self.assertRaises(AttributeError):
            error.exception.category="silent"
        with self.assertRaises(AttributeError):
            del error.exception.code



if __name__=="__main__":
    unittest.main()
