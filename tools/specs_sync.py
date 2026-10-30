#!/usr/bin/env python3
"""Compare two explicitly verified local tllib-specs Git handoffs; never update a lock.

No network calls, scientific inference, auto compatibility or auto-created GitHub issues.
Candidate metadata must be in an independently supplied lock, NOT specs.lock.json.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from tools import specs_pipeline as pipeline

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def inventory(handoff: pipeline.Handoff, index: dict) -> dict[str, dict]:
    """Hashes of ALL validated per-bundle files, plus catalog/domain metadata."""
    result = {}
    for name, entry in sorted(index["domains"].items()):
        path = entry["catalog_path"]
        result["domain:" + name] = {"path": path, "sha256": sha(handoff.bytes(path)),
                                     "identity": name, "kind": "domain"}
    for cid in sorted(index["shared"]):
        base = "handoff/shared/" + cid
        manifest = handoff.json(base + "/manifest.json")
        for filename in sorted(manifest["files"]):
            path = base + "/" + filename
            result["shared:" + cid + "/" + filename] = {
                "kind": "shared", "identity": cid, "path": path,
                "sha256": sha(handoff.bytes(path))}
    for fid, entry in sorted(index["features"].items()):
        base = entry["path"]
        manifest = handoff.json(base + "/manifest.json")
        for filename in sorted(manifest["files"]):
            path = base + "/" + filename
            result["feature:" + fid + "/" + filename] = {
                "kind": "feature", "identity": fid, "path": path,
                "sha256": sha(handoff.bytes(path))}
    return result

def compare(reference: dict, candidate: dict, ref_lock: dict, cand_lock: dict,
            ref_inventory: dict, cand_inventory: dict) -> dict:
    """Pure stable comparison, conservative classifications, with no execution."""
    changes = []
    def add(kind: str, identity: str, field: str, before, after, impact: str) -> None:
        changes.append({"kind": kind, "id": identity, "field": field,
                        "reference": before, "candidate": after,
                        "impact": impact})
    for key in ("model_version", "catalog_schema_version", "catalog_sha256"):
        if ref_lock[key] != cand_lock[key]:
            add("snapshot", "catalog", key, ref_lock[key], cand_lock[key],
                "manual_review_required")
    for name, key in (("domain", "domains"), ("feature", "features"),
                      ("shared", "shared")):
        previous, current = reference[key], candidate[key]
        for identity in sorted(set(previous) | set(current)):
            if identity not in previous:
                add(name, identity, "entry", None, current[identity],
                    "gap_unimplemented" if name == "feature" else "manual_review_required")
            elif identity not in current:
                add(name, identity, "entry", previous[identity], None, "breaking_or_removal")
            elif previous[identity] != current[identity]:
                before, after = previous[identity], current[identity]
                for field in sorted(set(before) | set(after)):
                    if before.get(field) != after.get(field):
                        add(name, identity, field, before.get(field), after.get(field),
                            "manual_review_required")
    for key in sorted(set(ref_inventory) | set(cand_inventory)):
        previous, current = ref_inventory.get(key), cand_inventory.get(key)
        if previous == current:
            continue
        sample = previous or current
        impact = ("breaking_or_removal" if current is None else
                  "gap_unimplemented" if previous is None and sample["kind"] == "feature"
                  else "manual_review_required")
        add(sample["kind"] + "_file", sample["identity"], sample["path"],
            None if previous is None else previous["sha256"],
            None if current is None else current["sha256"], impact)
    changes.sort(key=lambda item: (item["kind"], item["id"], item["field"]))
    actions = []
    for item in changes:
        action = ("Keep existing implementation unsupported and add a backlog assessment"
                  if item["impact"] == "gap_unimplemented" else
                  "Assess breakage and document migration/removal before lock approval"
                  if item["impact"] == "breaking_or_removal" else
                  "Obtain scientific/compatibility review; do not presume compatible")
        actions.append({"kind": item["kind"], "id": item["id"],
                        "field": item["field"], "action": action})
    return {"schema_version": "1.0",
            "reference": {"commit": ref_lock["commit"], "catalog_sha256": ref_lock["catalog_sha256"]},
            "candidate": {"commit": cand_lock["commit"], "catalog_sha256": cand_lock["catalog_sha256"]},
            "status": "review_required" if changes else "identical",
            "compatible": False if changes else True,
            "lock_update_permitted_automatically": False,
            "changes": changes, "migration_plan": actions}

def markdown(result: dict) -> str:
    lines = ["# tllib-specs snapshot difference (non-normative software review)", "",
             "Reference: `" + result["reference"]["commit"] + "`",
             "Candidate: `" + result["candidate"]["commit"] + "`", "",
             "Status: **" + result["status"] + "**.",
             "An added TLC-FC is **not implemented**. No compatibility is inferred.",
             "The tool never changes `specs.lock.json` or creates issues.", "",
             "| Kind | ID | Path/field | Impact |", "| --- | --- | --- | --- |"]
    for item in result["changes"]:
        lines.append("| " + " | ".join(str(item[field]).replace("|", "\\|")
                     for field in ("kind", "id", "field", "impact")) + " |")
    lines.extend(["", "## Proposed migration checklist", ""])
    for item in result["migration_plan"]:
        lines.append("- [ ] `" + item["id"] + "` / `" + item["field"] +
                     "`: " + item["action"])
    lines.extend(["", "**Gate:** human review, explicit compatibility decision, domain tests "
                  "and a separate reviewed lock-change PR are required before consuming any change.", ""])
    return "\n".join(lines)

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-specs", type=Path, required=True)
    parser.add_argument("--candidate-specs", type=Path, required=True)
    parser.add_argument("--candidate-lock", type=Path, required=True)
    parser.add_argument("--reference-lock", type=Path, default=Path(__file__).resolve().parents[1] / "specs.lock.json")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # Independently validate each full handoff against its own Git SHA and hash.
        ref_lock, ref_hand, ref_catalog = pipeline.verify_lock(args.reference_lock, args.reference_specs)
        cand_lock, cand_hand, cand_catalog = pipeline.verify_lock(args.candidate_lock, args.candidate_specs)
        first = pipeline.validate_catalog(ref_lock, ref_hand, ref_catalog)
        second = pipeline.validate_catalog(cand_lock, cand_hand, cand_catalog)
        result = compare(first, second, ref_lock, cand_lock,
                         inventory(ref_hand, first), inventory(cand_hand, second))
        out = args.output.resolve()
        if out == args.reference_lock.resolve() or out == args.candidate_lock.resolve():
            raise pipeline.PipelineError("UNSAFE_OUTPUT", str(out), "directory separate from lock", "lock path")
        for repo in (ref_hand.repository, cand_hand.repository):
            if out == repo or out.is_relative_to(repo / "handoff"):
                raise pipeline.PipelineError("UNSAFE_OUTPUT", str(out), "not a source handoff", str(repo))
        out.mkdir(parents=True, exist_ok=True)
        (out / "migration.json").write_bytes(pipeline.canonical(result))
        (out / "migration.md").write_text(markdown(result), encoding="utf-8", newline="\n")
        print("specs-sync: " + result["status"] + ", " + str(len(result["changes"])) + " changes")
        return 0 if not result["changes"] else 1
    except (pipeline.PipelineError, OSError, ValueError, KeyError, TypeError) as exc:
        code = exc.code if isinstance(exc, pipeline.PipelineError) else "INVALID_SNAPSHOT"
        print(json.dumps({"code": code, "message": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
