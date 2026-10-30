#!/usr/bin/env python3
"""Offline compatibility facts and installation metadata consistency gate (#14).

No implied scientific feature support; tllib version != tllib-specs version.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools import specs_pipeline as pipeline

SEMVER = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\Z")
PROJECT_VERSION = re.compile(r"project\(tllib\s+VERSION\s+([^\s)]+)\s+LANGUAGES", re.I)
HEADER_SHA = re.compile(r'inline constexpr std::string_view specs_commit = "([0-9a-f]{40})";')
HEADER_HASH = re.compile(r'inline constexpr std::string_view catalog_sha256 = "([0-9a-f]{64})";')

def check(root: Path) -> dict:
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    cmake = (root / "CMakeLists.txt").read_text(encoding="utf-8")
    header = (root / "include/tllib/generated/feature_metadata.hpp").read_text(encoding="utf-8")
    lock = pipeline.parse_json((root / "specs.lock.json").read_bytes(), "specs.lock.json")
    index = pipeline.parse_json((root / "generated/specs/feature_index.json").read_bytes(),
                                 "generated/specs/feature_index.json")
    version = PROJECT_VERSION.search(cmake)
    native = version.group(1) if version else None
    python_version = project.get("version")
    issues = []
    if not isinstance(native, str) or not SEMVER.fullmatch(native):
        issues.append("INVALID_NATIVE_SEMVER")
    if not isinstance(python_version, str) or not SEMVER.fullmatch(python_version):
        issues.append("INVALID_PYTHON_SEMVER")
    if native != python_version:
        issues.append("VERSION_MISMATCH")
    if "COMPATIBILITY SameMinorVersion" not in cmake:
        issues.append("CMAKE_VERSION_POLICY_MISMATCH")
    require_python = project.get("requires-python")
    if require_python != ">=3.12,<3.13":
        issues.append("PYTHON_SUPPORT_METADATA_MISMATCH")
    if lock.get("repository") != pipeline.EXPECTED_REPOSITORY:
        issues.append("INVALID_SPECS_ORIGIN")
    fields = {"commit": (HEADER_SHA.search(header), "specs_commit"),
              "catalog_sha256": (HEADER_HASH.search(header), "catalog_sha256")}
    for key, (match, index_key) in fields.items():
        value = match.group(1) if match else None
        if value != lock.get(key) or index.get(index_key) != lock.get(key):
            issues.append("SPECS_" + key.upper() + "_MISMATCH")
    # A declared deprecation is actionable only with a versioned migration note.
    registry_file = root / "conformance/deprecations.json"
    registry = pipeline.parse_json(registry_file.read_bytes(), "conformance/deprecations.json")
    entries = registry.get("entries")
    if registry.get("schema_version") != "1.0" or not isinstance(entries, list):
        issues.append("INVALID_DEPRECATION_REGISTRY")
        entries = []
    seen = set()
    for item in entries:
        if not isinstance(item, dict) or set(item) != {
            "symbol", "deprecated_in", "remove_no_earlier_than", "replacement", "migration_note"
        }:
            issues.append("INVALID_DEPRECATION_ENTRY")
            continue
        symbol = item["symbol"]
        note = item["migration_note"]
        start, end = item["deprecated_in"], item["remove_no_earlier_than"]
        if (
            not isinstance(symbol, str) or not symbol.startswith("tllib.")
            or symbol in seen or not isinstance(item["replacement"], str)
            or not item["replacement"] or not isinstance(start, str)
            or not isinstance(end, str) or not SEMVER.fullmatch(start)
            or not SEMVER.fullmatch(end) or tuple(map(int, end.split(".")))
            <= tuple(map(int, start.split(".")))
            or not isinstance(note, str) or not note.startswith("docs/v1/")
        ):
            issues.append("INVALID_DEPRECATION_ENTRY")
        else:
            try:
                pipeline.safe_name(note)
                if not (root / note).is_file():
                    issues.append("MISSING_MIGRATION_NOTE")
            except pipeline.PipelineError:
                issues.append("INVALID_MIGRATION_PATH")
        if isinstance(symbol, str):
            seen.add(symbol)
    if index.get("model_version") != lock.get("model_version"):
        issues.append("SPECS_MODEL_VERSION_MISMATCH")
    return {"schema_version": "1.0", "package_version": native,
            "python_package_version": python_version, "requires_python": require_python,
            "cpp_abi_stable": False, "stable_abi_python": False,
            "scientific_implementation_claim": False,
            "specs": {"repository": lock.get("repository"),
                      "commit": lock.get("commit"), "catalog_sha256": lock.get("catalog_sha256"),
                      "model_version": lock.get("model_version")},
            "deprecated_symbol_count": len(entries),
            "status": "pass" if not issues else "fail",
            "diagnostics": sorted(set(issues))}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="Optional directory outside handoff")
    args = parser.parse_args(argv)
    try:
        result = check(args.root)
        if args.output:
            path = args.output.resolve()
            if path == args.root.resolve() / "specs.lock.json" or (
                    path.is_relative_to(args.root.resolve() / "pinned-specs")):
                raise ValueError("Refusing unsafe output path")
            path.mkdir(parents=True, exist_ok=True)
            (path / "compatibility.json").write_bytes(pipeline.canonical(result))
        print(json.dumps(result, sort_keys=True))
        return 0 if result["status"] == "pass" else 1
    except (OSError, ValueError, TypeError, KeyError, pipeline.PipelineError) as exc:
        print(json.dumps({"code": "INVALID_COMPATIBILITY_INPUT", "error": str(exc)}, sort_keys=True),
              file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
