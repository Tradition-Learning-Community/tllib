#!/usr/bin/env python3
"""Offline, non-executing tllib-specs handoff verifier and deterministic structural generator.

Requires an explicitly supplied, clean Git checkout at the exact commit pinned by
specs.lock.json. Never clones, imports source artifacts or reads beyond handoff/.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

EXPECTED_REPOSITORY = "Tradition-Learning-Community/tllib-specs"
CATEGORIES = ("covered", "blocked-by-spec", "provider-required", "structural", "unimplemented", "invalid")
FIELDS = ("package", "scientific", "execution")
KNOWN_STATUS = {
    "package": {"draft", "pilot", "validated", "finalized", "deprecated", "superseded"},
    "scientific": {"defined", "partially_defined", "preserved_unresolved", "external_provider_required", "not_applicable"},
    "execution": {"structural_only", "executable", "conditionally_executable", "unsupported"},
}
MAX_CATALOG = 16 * 1024 * 1024
MAX_DOCUMENT = 4 * 1024 * 1024
MAX_JSON_DEPTH = 80
HEX = re.compile(r"[0-9a-f]{64}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
FEATURE = re.compile(r"TLC-FC-[0-9]{2}-[A-Z][A-Z0-9-]*-[0-9]{3}\Z")
SHARED = re.compile(r"TLC-HC-[A-Z0-9-]+\Z")
DOMAIN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

class PipelineError(Exception):
    def __init__(self, code: str, path: str, expected: object, observed: object):
        self.code, self.path, self.expected, self.observed = code, path, expected, observed
        super().__init__(f"{code}: {path} expected={expected!r} observed={observed!r}")

def require(condition: bool, code: str, path: str, expected: object, observed: object) -> None:
    if not condition:
        raise PipelineError(code, path, expected, observed)

def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON property {key}")
        result[key] = value
    return result

def nesting(value: object, depth: int = 0) -> None:
    if depth > MAX_JSON_DEPTH:
        raise ValueError("JSON nesting exceeds limit")
    if isinstance(value, dict):
        for key, v in value.items():
            if not isinstance(key, str):
                raise ValueError("invalid JSON key")
            nesting(v, depth + 1)
    elif isinstance(value, list):
        for v in value:
            nesting(v, depth + 1)

def parse_json(data: bytes, path: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=no_duplicate_keys,
                           parse_constant=lambda x: (_ for _ in ()).throw(ValueError(f"invalid number {x}")))
        nesting(value)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise PipelineError("INVALID_JSON", path, "valid bounded UTF-8 JSON", str(exc)) from exc
    require(isinstance(value, dict), "INVALID_SHAPE", path, "JSON object", type(value).__name__)
    return value

def canonical(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")

def safe_name(path: str) -> str:
    require(isinstance(path, str) and bool(path), "UNSAFE_PATH", str(path), "nonempty POSIX relative path", path)
    pure = PurePosixPath(path)
    require(not pure.is_absolute() and "\\" not in path and ":" not in path and
            all(p not in ("", ".", "..") for p in path.split("/")), "UNSAFE_PATH", path,
            "relative clean POSIX path", path)
    return path

class Handoff:
    def __init__(self, repository: Path):
        self.repository = repository.resolve(strict=True)
        self.handoff = self.repository / "handoff"
        require(self.handoff.is_dir() and not self.handoff.is_symlink(),
                "MISSING_HANDOFF", "handoff", "directory", "missing or symlink")
        self.files: set[str] = set()

    def bytes(self, relative: str, limit: int = MAX_DOCUMENT) -> bytes:
        safe_name(relative)
        require(relative.startswith("handoff/"), "OUTSIDE_HANDOFF", relative, "handoff/...", relative)
        path = self.repository / relative
        # Explicitly reject every symlink component, including the final file.
        current = self.repository
        for piece in relative.split("/"):
            current = current / piece
            require(not current.is_symlink(), "SYMLINK", relative, "no symlink", piece)
        require(path.is_file(), "MISSING_FILE", relative, "regular file", "absent")
        require(path.stat().st_size <= limit, "FILE_TOO_LARGE", relative, f"<= {limit}", path.stat().st_size)
        resolved = path.resolve(strict=True)
        require(resolved.is_relative_to(self.handoff), "OUTSIDE_HANDOFF", relative, "inside handoff", str(resolved))
        self.files.add(relative)
        return path.read_bytes()

    def json(self, relative: str, limit: int = MAX_DOCUMENT) -> dict:
        return parse_json(self.bytes(relative, limit), relative)

def git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                            timeout=120, check=False)
    if result.returncode != 0:
        raise PipelineError("GIT_PROVENANCE", str(repo), "usable Git checkout", result.stderr.strip()[:150])
    return result.stdout.strip()

def verify_lock(lock_path: Path, repo: Path) -> tuple[dict, Handoff, dict]:
    require(lock_path.stat().st_size <= 65536, "FILE_TOO_LARGE", str(lock_path), "<= 65536 bytes", lock_path.stat().st_size)
    lock = parse_json(lock_path.read_bytes(), str(lock_path))
    require(set(lock) == {"schema_version", "repository", "commit", "handoff_catalog_path",
            "catalog_sha256", "catalog_schema_version", "model_version", "verification"},
            "INVALID_LOCK", str(lock_path), "exact lock fields", sorted(lock))
    require(lock["schema_version"] == "1.0" and lock["repository"] == EXPECTED_REPOSITORY,
            "INVALID_LOCK", str(lock_path), EXPECTED_REPOSITORY, lock.get("repository"))
    require(isinstance(lock["commit"], str) and bool(COMMIT.fullmatch(lock["commit"])),
            "INVALID_COMMIT", str(lock_path), "40 lowercase hex digits", lock["commit"])
    require(lock["handoff_catalog_path"] == "handoff/catalog.json",
            "INVALID_LOCK", str(lock_path), "handoff/catalog.json", lock["handoff_catalog_path"])
    require(isinstance(lock["catalog_sha256"], str) and bool(HEX.fullmatch(lock["catalog_sha256"])),
            "INVALID_HASH", str(lock_path), "64 lowercase hex digits", lock["catalog_sha256"])
    require(lock["verification"] == {"name": "tllib-offline-handoff-verifier", "version": "1.0.0",
        "hash_algorithm": "sha256", "git_object_integrity": "required"}, "INVALID_LOCK",
        str(lock_path), "supported verification method", lock["verification"])
    root = repo.resolve(strict=True)
    actual_repo_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    require(actual_repo_root == root, "GIT_PROVENANCE", str(repo), str(root), str(actual_repo_root))
    actual_commit = git(root, "rev-parse", "HEAD")
    require(actual_commit == lock["commit"], "COMMIT_MISMATCH", str(repo), lock["commit"], actual_commit)
    changes = git(root, "status", "--porcelain", "--untracked-files=all", "--", "handoff")
    require(not changes, "DIRTY_HANDOFF", "handoff", "clean committed tree", changes[:200])
    handoff = Handoff(root)
    catalog_bytes = handoff.bytes("handoff/catalog.json", MAX_CATALOG)
    actual_hash = hashlib.sha256(catalog_bytes).hexdigest()
    require(actual_hash == lock["catalog_sha256"], "CATALOG_HASH_MISMATCH",
            "handoff/catalog.json", lock["catalog_sha256"], actual_hash)
    catalog = parse_json(catalog_bytes, "handoff/catalog.json")
    require(catalog.get("schema_version") == lock["catalog_schema_version"] and
            catalog.get("model_version") == lock["model_version"],
            "VERSION_MISMATCH", "handoff/catalog.json",
            (lock["catalog_schema_version"], lock["model_version"]),
            (catalog.get("schema_version"), catalog.get("model_version")))
    require(lock["catalog_schema_version"] == "1.0" and lock["model_version"] == "1.0.0",
            "UNSUPPORTED_VERSION", str(lock_path), "1.0 / 1.0.0", (
                lock["catalog_schema_version"], lock["model_version"]))
    # Verify path content exactly belongs to HEAD's Git object, not only a claimed commit ID.
    tracked_object = git(root, "rev-parse", "HEAD:handoff/catalog.json")
    observed_object = git(root, "hash-object", "handoff/catalog.json")
    require(tracked_object == observed_object, "GIT_OBJECT_MISMATCH",
            "handoff/catalog.json", tracked_object, observed_object)
    return lock, handoff, catalog

def unique(values: list[str], path: str) -> None:
    require(len(values) == len(set(values)), "DUPLICATE_ID", path, "unique IDs", values[:5])

def validate_catalog(lock: dict, handoff: Handoff, catalog: dict) -> dict:
    require(catalog.get("catalog_status") == "finalized", "INCOMPLETE_CATALOG",
            "handoff/catalog.json", "finalized", catalog.get("catalog_status"))
    domains, features, shared = (catalog.get(x) for x in ("domains", "features", "shared_contracts"))
    require(all(isinstance(x, list) and x for x in (domains, features, shared)),
            "INVALID_CATALOG", "handoff/catalog.json", "nonempty domain/feature/shared lists", "missing")
    domains_by_name, features_by_id, shared_by_id = {}, {}, {}
    summary = catalog.get("summary")
    require(isinstance(summary, dict), "INVALID_CATALOG", "summary", "object", summary)
    for item in domains:
        require(isinstance(item, dict), "INVALID_DOMAIN", "handoff/catalog.json", "domain object", item)
        name = item.get("domain")
        require(isinstance(name, str) and bool(DOMAIN.fullmatch(name)) and name not in domains_by_name,
                "INVALID_DOMAIN", "handoff/catalog.json", "unique valid domain", name)
        count = item.get("feature_count")
        require(type(count) is int and count >= 0, "INVALID_DOMAIN", name, "nonnegative count", count)
        domains_by_name[name] = item
    for item in shared:
        require(isinstance(item, dict), "INVALID_CONTRACT", "handoff/catalog.json", "contract object", item)
        cid = item.get("shared_contract_id")
        require(isinstance(cid, str) and bool(SHARED.fullmatch(cid)) and cid not in shared_by_id,
                "INVALID_CONTRACT", "handoff/catalog.json", "unique shared contract ID", cid)
        require(item.get("version") == "1.0.0", "VERSION_MISMATCH", cid, "1.0.0", item.get("version"))
        shared_by_id[cid] = item
    for item in shared:
        cid = item["shared_contract_id"]
        for dep in item.get("dependencies", []):
            require(dep.get("shared_contract_id") in shared_by_id and dep.get("version") == "1.0.0",
                    "UNKNOWN_DEPENDENCY", cid, "published shared contract@1.0.0", dep)
    visited: dict[str, int] = {}
    def visit(cid: str) -> None:
        state = visited.get(cid, 0)
        require(state != 1, "CYCLIC_DEPENDENCY", cid, "DAG", cid)
        if state == 2:
            return
        visited[cid] = 1
        for d in shared_by_id[cid].get("dependencies", []):
            visit(d["shared_contract_id"])
        visited[cid] = 2
    for cid in sorted(shared_by_id):
        visit(cid)
    by_domain = Counter()
    for item in features:
        require(isinstance(item, dict), "INVALID_FEATURE_ID", "handoff/catalog.json", "feature object", item)
        fid, domain = item.get("feature_id"), item.get("domain")
        require(isinstance(fid, str) and bool(FEATURE.fullmatch(fid)) and fid not in features_by_id,
                "INVALID_FEATURE_ID", "handoff/catalog.json", "unique TLC-FC", fid)
        require(domain in domains_by_name, "UNKNOWN_DOMAIN", fid, "declared domain", domain)
        require(item.get("package_version") == "1.0.0", "VERSION_MISMATCH", fid, "1.0.0", item.get("package_version"))
        statuses = item.get("statuses")
        require(isinstance(statuses, dict) and set(statuses) == set(FIELDS) and
                all(statuses[f] in KNOWN_STATUS[f] for f in FIELDS),
                "INVALID_STATUS", fid, "closed known statuses", statuses)
        require(item.get("path") == f"handoff/features/{fid}" and
                item.get("manifest_path") == f"handoff/features/{fid}/manifest.json",
                "UNSAFE_PATH", fid, f"handoff/features/{fid}", item.get("path"))
        require(all(isinstance(item.get(k), str) and bool(HEX.fullmatch(item[k]))
                    for k in ("package_sha256", "descriptor_sha256")), "INVALID_HASH", fid,
                "64-digit package and descriptor fingerprints", item.get("package_sha256"))
        features_by_id[fid] = item
        by_domain[domain] += 1
    require(all(by_domain.get(d, 0) == entry["feature_count"] for d, entry in domains_by_name.items()),
            "POPULATION_MISMATCH", "domains", "declared feature counts", dict(by_domain))
    expected = {"feature_count": len(features), "domain_count": len(domains), "shared_contract_count": len(shared)}
    require(all(summary.get(key) == count for key, count in expected.items()),
            "POPULATION_MISMATCH", "summary", expected, {key: summary.get(key) for key in expected})
    for key, field in (("package_statuses", "package"), ("scientific_statuses", "scientific"),
                       ("execution_statuses", "execution")):
        actual = dict(Counter(f["statuses"][field] for f in features))
        require(summary.get(key) == actual, "POPULATION_MISMATCH", f"summary.{key}", actual, summary.get(key))
    # Index verification is essential; version/hash alone cannot prove package integrity.
    for domain, entry in sorted(domains_by_name.items()):
        domain_path = entry.get("catalog_path")
        require(domain_path == f"handoff/domains/{domain}/catalog.json",
                "UNSAFE_PATH", domain, f"handoff/domains/{domain}/catalog.json", domain_path)
        dcat = handoff.json(domain_path)
        listed = dcat.get("ordered_feature_ids")
        expected_ids = [f["feature_id"] for f in features if f["domain"] == domain]
        require(dcat.get("domain") == domain and dcat.get("domain_index") == entry["domain_index"] and
                dcat.get("expected_feature_count") == len(expected_ids) and
                isinstance(listed, list) and set(listed) == set(expected_ids) and
                len(listed) == len(expected_ids) and dcat.get("statuses") ==
                {"population": "complete", "validation": "validated"},
                "DOMAIN_CATALOG_MISMATCH", domain_path, "complete matching inventory", dcat.get("statuses"))
        packages = dcat.get("feature_packages")
        require(isinstance(packages, list) and [p.get("feature_id") for p in packages] == listed,
                "DOMAIN_CATALOG_MISMATCH", domain_path, "same package order", packages[:1] if isinstance(packages, list) else None)
        for p in packages:
            require(p.get("path") == f"handoff/features/{p['feature_id']}" and
                    p.get("package_version") == "1.0.0",
                    "DOMAIN_CATALOG_MISMATCH", domain_path, "matching paths/version", p)
    acceptance = {}
    acceptance_cases = {}
    shared_info = {}
    for cid in sorted(shared_by_id):
        base = f"handoff/shared/{cid}"
        meta = handoff.json(base + "/manifest.json")
        require(meta.get("shared_contract_id") == cid and meta.get("package_version") == "1.0.0",
                "SHARED_MANIFEST_MISMATCH", base, cid, meta.get("shared_contract_id"))
        contract = handoff.json(base + "/contract.json")
        tests = handoff.json(base + "/acceptance.json")
        trace = handoff.json(base + "/traceability.json")
        require(contract.get("shared_contract", {}).get("shared_contract_id") == cid and
                tests.get("applies_to") == cid and trace.get("applies_to") == cid,
                "SHARED_CONTRACT_MISMATCH", base, cid, "identity mismatch")
        declared = meta.get("files")
        require(isinstance(declared, list) and len(declared) == len(set(declared)),
                "INVALID_MANIFEST", base, "unique declared files", declared)
        for file in declared:
            require(file in {"README.md", "manifest.json", "contract.json", "acceptance.json",
                             "examples.json", "traceability.json"}, "INVALID_MANIFEST", base, "allowed file", file)
            handoff.bytes(base + "/" + file)
        shared_info[cid] = sorted(t["test_id"] for t in tests.get("tests", []))
        unique(shared_info[cid], base + "/acceptance.json")
    for fid in sorted(features_by_id):
        entry = features_by_id[fid]
        base = entry["path"]
        manifest = handoff.json(base + "/manifest.json")
        require(manifest.get("feature_id") == fid and manifest.get("domain") == entry["domain"] and
                manifest.get("package_version") == entry["package_version"] and
                manifest.get("statuses") == entry["statuses"],
                "MANIFEST_MISMATCH", base + "/manifest.json", entry["statuses"], manifest.get("statuses"))
        contract = handoff.json(base + "/contract.json")
        acceptance_doc = handoff.json(base + "/acceptance.json")
        trace = handoff.json(base + "/traceability.json")
        require(contract.get("feature", {}).get("feature_id") == fid and
                acceptance_doc.get("applies_to") == fid and trace.get("applies_to") == fid,
                "BUNDLE_MISMATCH", base, fid, "contract/acceptance/traceability IDs")
        require(all(doc.get("schema_version") == "1.0" and doc.get("package_version") == "1.0.0"
                    for doc in (manifest, contract, acceptance_doc, trace)),
                "VERSION_MISMATCH", base, "1.0 / 1.0.0", "bundle version differs")
        declared = manifest.get("files")
        require(isinstance(declared, list) and
                len(declared) == len(set(declared)) and
                set(("manifest.json", "contract.json", "acceptance.json", "traceability.json")).issubset(declared),
                "INVALID_MANIFEST", base, "required unique files", declared)
        require(bool(manifest.get("examples", {}).get("present")) == bool(entry.get("examples_present")),
                "MANIFEST_MISMATCH", base, entry.get("examples_present"), manifest.get("examples"))
        for filename in declared:
            require(filename in {"README.md", "manifest.json", "contract.json", "acceptance.json",
                                 "examples.json", "traceability.json"},
                    "INVALID_MANIFEST", base, "allowed file", filename)
            handoff.bytes(base + "/" + filename)
        dep_ids = [(d.get("shared_contract_id"), d.get("version"))
                   for d in manifest.get("shared_dependencies", [])]
        cat_dep_ids = [(d.get("shared_contract_id"), d.get("version"))
                       for d in entry.get("shared_dependencies", [])]
        require(sorted(dep_ids) == sorted(cat_dep_ids) and len(set(dep_ids)) == len(dep_ids) and
                all(cid in shared_by_id and version == "1.0.0" for cid, version in dep_ids),
                "UNKNOWN_DEPENDENCY", base, cat_dep_ids, dep_ids)
        tests = acceptance_doc.get("tests")
        require(isinstance(tests, list), "INVALID_ACCEPTANCE", base, "test list", tests)
        test_ids = [t.get("test_id") for t in tests]
        require(all(isinstance(t, str) and t for t in test_ids),
                "INVALID_ACCEPTANCE", base, "nonempty test IDs", test_ids[:4])
        unique(test_ids, base + "/acceptance.json")
        acceptance[fid] = sorted(test_ids)
        acceptance_cases[fid] = sorted(tests, key=lambda item: item['test_id'])
    return {"features": features_by_id, "domains": domains_by_name, "shared": shared_by_id,
            "acceptance": acceptance, "acceptance_cases": acceptance_cases,
            "shared_acceptance": shared_info}

def generated(lock: dict, index: dict) -> dict[str, bytes]:
    items = index["features"]
    data = {
        "schema_version": "1.0",
        "specs_commit": lock["commit"],
        "catalog_sha256": lock["catalog_sha256"],
        "model_version": lock["model_version"],
        "domains": [{"id": name, "feature_count": item["feature_count"]}
                    for name, item in sorted(index["domains"].items())],
        "shared_contracts": [{"id": cid, "version": info["version"]}
                             for cid, info in sorted(index["shared"].items())],
        "features": [{"id": fid, "domain": entry["domain"],
                      "package_version": entry["package_version"],
                      "statuses": entry["statuses"],
                      "manifest_path": entry["manifest_path"]}
                     for fid, entry in sorted(items.items())]
    }
    # Generated symbols are descriptive metadata only. They never register a feature.
    rows = []
    for fid, entry in sorted(items.items()):
        statuses = entry["statuses"]
        rows.append('  {"%s", "%s", "%s", "%s", "%s"},' %
                    (fid, entry["domain"], statuses["package"], statuses["scientific"],
                     statuses["execution"]))
    header = "\n".join([
        "// GENERATED by tools/specs_pipeline.py from pinned handoff. DO NOT EDIT.",
        "// specs commit: " + lock["commit"],
        "// catalog sha256: " + lock["catalog_sha256"],
        "#pragma once",
        "#include <array>",
        "#include <string_view>",
        "namespace tllib::generated {",
        f'inline constexpr std::string_view specs_commit = "{lock["commit"]}";',
        f'inline constexpr std::string_view catalog_sha256 = "{lock["catalog_sha256"]}";',
        "struct FeatureMetadata {",
        "  std::string_view feature_id, domain, package_status, scientific_status, execution_status;",
        "};",
        f"inline constexpr std::array<FeatureMetadata, {len(rows)}> features = {{{{",
        *rows,
        "}};",
        "} // namespace tllib::generated",
        ""
    ]).encode("utf-8")
    return {"generated/specs/feature_index.json": canonical(data),
            "include/tllib/generated/feature_metadata.hpp": header}

def write_generated(outputs: dict[str, bytes], root: Path, check: bool) -> None:
    for relative, contents in sorted(outputs.items()):
        path = root / relative
        if check:
            require(path.is_file(), "MISSING_GENERATED", relative, "generated committed file", "absent")
            actual = path.read_bytes()
            require(actual == contents, "GENERATED_DRIFT", relative,
                    hashlib.sha256(contents).hexdigest(), hashlib.sha256(actual).hexdigest())
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)

def read_decisions(path: Path, index: dict, lock: dict) -> tuple[dict, list[dict]]:
    require(path.stat().st_size <= 8 * 1024 * 1024, "FILE_TOO_LARGE", str(path),
            "<= 8 MiB", path.stat().st_size)
    source = parse_json(path.read_bytes(), str(path))
    entries = source.get("features")
    require(source.get("specs_commit") == lock["commit"], "DECISION_SNAPSHOT_MISMATCH",
            str(path), lock["commit"], source.get("specs_commit"))
    require(source.get("schema_version") == "1.0" and isinstance(entries, list),
            "INVALID_DECISIONS", str(path), "versioned feature list", source.get("schema_version"))
    mapped, diagnostics = {}, []
    for entry in entries:
        require(isinstance(entry, dict), "INVALID_DECISIONS", str(path), "object", entry)
        fid = entry.get("feature_id")
        require(isinstance(fid, str) and bool(FEATURE.fullmatch(fid)) and fid not in mapped,
                "INVALID_DECISIONS", str(path), "unique TLC-FC", fid)
        require(entry.get("disposition") in CATEGORIES and
                isinstance(entry.get("reason"), str) and bool(entry["reason"].strip()) and
                isinstance(entry.get("evidence"), list),
                "INVALID_DECISIONS", fid, "disposition, reason, evidence", entry)
        mapped[fid] = entry
    requested = set(index["features"])
    known = set(mapped)
    for fid in sorted(requested - known):
        diagnostics.append({"code": "MISSING_DECISION", "feature_id": fid,
                            "path": "conformance/decisions.json", "expected": "explicit decision",
                            "observed": "none"})
    for fid in sorted(known - requested):
        diagnostics.append({"code": "STALE_DECISION", "feature_id": fid,
                            "path": "conformance/decisions.json", "expected": "catalog entry",
                            "observed": "not present in catalog"})
    return mapped, diagnostics

def junit_passes(test_results: Path | None) -> set[str]:
    """Only test runner output, never a decision's asserted result, proves a pass."""
    if test_results is None:
        return set()
    require(test_results.is_file() and test_results.stat().st_size <= 16 * 1024 * 1024,
            "INVALID_TEST_RESULTS", str(test_results), "bounded existing JUnit XML", "absent/oversize")
    data = test_results.read_bytes()
    require(b"<!DOCTYPE" not in data.upper() and b"<!ENTITY" not in data.upper(),
            "INVALID_TEST_RESULTS", str(test_results), "no entity/DTD", "DTD/entity")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise PipelineError("INVALID_TEST_RESULTS", str(test_results), "valid JUnit XML", str(exc)) from exc
    observed: dict[str, bool] = {}
    for node in root.iter("testcase"):
        name = node.get("name")
        require(isinstance(name, str) and bool(name) and name not in observed,
                "INVALID_TEST_RESULTS", str(test_results), "unique JUnit testcase name", name)
        bad = (node.get("status") in ("skipped", "failed", "error") or
               any(child.tag in ("failure", "error", "skipped") for child in node))
        observed[name] = not bad
    return {name for name, passed in observed.items() if passed}

def report(lock: dict, index: dict, decisions_path: Path, enforce_release: bool,
           test_results: Path | None = None) -> tuple[dict, str, int]:
    decisions, diagnostics = read_decisions(decisions_path, index, lock)
    passed_runner_tests = junit_passes(test_results)
    implementation_root = decisions_path.resolve().parent.parent
    coverage = []
    counts = Counter()
    for fid, entry in sorted(index["features"].items()):
        decision = decisions.get(fid)
        disposition = decision["disposition"] if decision else "invalid"
        reason = decision["reason"] if decision else "No explicit decision"
        evidence = decision["evidence"] if decision else []
        acceptance_ids = index["acceptance"][fid]
        accepted_ids = set(acceptance_ids)
        if disposition in ("covered", "structural"):
            passed: set[str] = set()
            for proof in evidence:
                if not isinstance(proof, dict) or not isinstance(proof.get("test_id"), str):
                    continue
                if proof["test_id"] not in accepted_ids or proof.get("result") != "passed":
                    continue
                artifact, test_name = proof.get("artifact"), proof.get("ctest_name")
                if not isinstance(artifact, str) or not artifact.startswith("tests/"):
                    continue
                if not isinstance(test_name, str) or test_name not in passed_runner_tests:
                    continue
                safe_name(artifact)
                source = implementation_root / artifact
                if not source.is_file() or source.is_symlink() or not source.resolve().is_relative_to(implementation_root):
                    continue
                passed.add(proof["test_id"])
            if not accepted_ids or not accepted_ids.issubset(passed):
                diagnostics.append({"code": "MISSING_ACCEPTANCE_PROOF", "feature_id": fid,
                                    "path": entry["path"] + "/acceptance.json",
                                    "expected": sorted(accepted_ids), "observed": sorted(passed)})
                disposition = "invalid"
            if decision and decision["disposition"] == "structural" and entry["statuses"]["execution"] != "structural_only":
                diagnostics.append({"code": "INVALID_STRUCTURAL_DECISION", "feature_id": fid,
                                    "path": "conformance/decisions.json",
                                    "expected": "structural_only", "observed": entry["statuses"]["execution"]})
                disposition = "invalid"
            if decision and decision["disposition"] == "covered" and entry["statuses"]["execution"] in ("structural_only", "unsupported"):
                diagnostics.append({"code": "INVALID_EXECUTION_DECISION", "feature_id": fid,
                                    "path": "conformance/decisions.json",
                                    "expected": "executable or conditionally_executable",
                                    "observed": entry["statuses"]["execution"]})
                disposition = "invalid"
        else:
            require(not evidence, "INVALID_DECISIONS", fid, "no fabricated evidence", evidence)
        if disposition == "provider-required" and entry["statuses"]["execution"] != "conditionally_executable" and entry["statuses"]["scientific"] != "external_provider_required":
            diagnostics.append({"code": "INVALID_PROVIDER_DECISION", "feature_id": fid,
                                "path": "conformance/decisions.json",
                                "expected": "conditional execution or provider-bound scientific status",
                                "observed": entry["statuses"]})
            disposition = "invalid"
        if disposition == "invalid" and not any(d.get("feature_id") == fid for d in diagnostics):
            diagnostics.append({"code": "INVALID_DECISION", "feature_id": fid,
                                "path": "conformance/decisions.json",
                                "expected": "valid explicit decision", "observed": reason})
        counts[disposition] += 1
        coverage.append({"feature_id": fid, "domain": entry["domain"],
                         "scientific_status": entry["statuses"]["scientific"],
                         "execution_status": entry["statuses"]["execution"],
                         "disposition": disposition, "reason": reason,
                         "acceptance_ids": acceptance_ids, "evidence": evidence})
    if enforce_release:
        for row in coverage:
            if row["disposition"] not in ("covered", "structural"):
                diagnostics.append({"code": "RELEASE_NOT_READY", "feature_id": row["feature_id"],
                                    "path": "conformance/decisions.json",
                                    "expected": "verified covered or structural",
                                    "observed": row["disposition"]})
    machine = {
        "schema_version": "1.0",
        "specs_commit": lock["commit"],
        "catalog_sha256": lock["catalog_sha256"],
        "model_version": lock["model_version"],
        "feature_count": len(index["features"]),
        "decisions_count": len(decisions),
        "summary": {c: counts[c] for c in CATEGORIES},
        "gate": "failed" if diagnostics else "passed",
        "diagnostics": diagnostics,
        "features": coverage
    }
    lines = [
        "# tllib V1 catalogue conformance",
        "",
        f"Specs commit: `{lock['commit']}`",
        f"Catalogue SHA-256: `{lock['catalog_sha256']}`",
        f"Features: **{len(coverage)}**; explicit decisions: **{len(decisions)}**;",
        f"Decision gate: **{machine['gate']}**; release gate: **{'on' if enforce_release else 'off'}**",
        "",
        "| Disposition | Count |", "| --- | ---: |"
    ]
    lines.extend(f"| {c} | {counts[c]} |" for c in CATEGORIES)
    lines.extend(["", "Coverage means explicit inventory decisions, **not** scientific implementation.", "",
                  "| TLC-FC | Status | Decision | Acceptance tests |",
                  "| --- | --- | --- | ---: |"])
    for item in coverage:
        lines.append(f"| {item['feature_id']} | {item['execution_status']} | {item['disposition']} | {len(item['acceptance_ids'])} |")
    if diagnostics:
        lines.extend(["", "## Diagnostics", ""])
        for d in diagnostics:
            lines.append(f"- {d['code']} — {d['feature_id']} / {d['path']}: expected {d['expected']}, observed {d['observed']}")
    return machine, "\n".join(lines) + "\n", (1 if diagnostics else 0)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "generate", "check-generated", "report", "release-gate"))
    parser.add_argument("--specs", type=Path, required=True, help="Explicit pinned tllib-specs checkout (no fetch)")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, help="Report output directory; never inside handoff")
    parser.add_argument("--test-results", type=Path, help="Local JUnit XML from actually executed trusted CTest tests")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve(strict=True)
        lock, handoff, catalog = verify_lock(root / "specs.lock.json", args.specs)
        index = validate_catalog(lock, handoff, catalog)
        if args.command in ("generate", "check-generated"):
            write_generated(generated(lock, index), root, args.command == "check-generated")
        if args.command in ("report", "release-gate"):
            machine, markdown, status = report(lock, index, root / "conformance/decisions.json",
                                               args.command == "release-gate", args.test_results)
            output = args.output or root / "build/specs-report"
            output.mkdir(parents=True, exist_ok=True)
            (output / "coverage.json").write_bytes(canonical(machine))
            (output / "coverage.md").write_text(markdown, encoding="utf-8", newline="\n")
            # Published acceptance test inputs/expectations are copied only as inert data.
            cases = {"schema_version": "1.0", "specs_commit": lock["commit"],
                     "catalog_sha256": lock["catalog_sha256"],
                     "features": [{"feature_id": fid, "tests": tests}
                                  for fid, tests in sorted(index["acceptance_cases"].items())]}
            (output / "acceptance_cases.json").write_bytes(canonical(cases))
            print(f"{args.command}: {machine['feature_count']} features, {machine['decisions_count']} decisions, gate={machine['gate']}")
            return status
        print(f"{args.command}: verified {len(index['features'])} features, {len(index['domains'])} domains, {len(index['shared'])} shared contracts at {lock['commit']}")
        return 0
    except (PipelineError, OSError, subprocess.TimeoutExpired, ValueError,
            TypeError, KeyError, AttributeError, IndexError) as exc:
        if isinstance(exc, PipelineError):
            print(json.dumps({"code": exc.code, "path": exc.path, "expected": exc.expected,
                              "observed": exc.observed}, ensure_ascii=False, sort_keys=True),
                  file=sys.stderr)
        else:
            code = "IO_ERROR" if isinstance(exc, (OSError, subprocess.TimeoutExpired)) else "INVALID_HANDOFF"
            print(json.dumps({"code": code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
