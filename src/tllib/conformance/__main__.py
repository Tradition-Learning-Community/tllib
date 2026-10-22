"""CLI for deterministic Feature Handoff conformance reporting."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from .loader import HandoffLoadError, load_bindings, load_handoffs
from .report import build_report, write_report


def _default_handoff_root() -> Path:
    specs_root = os.environ.get("TLLIB_SPECS_ROOT")
    if specs_root:
        return Path(specs_root) / "handoff"
    return Path.cwd().parent / "tllib-specs" / "handoff"


def main(arguments: Sequence[str] | None = None) -> int:
    """Generate the conformance report and return a process status."""
    parser = argparse.ArgumentParser(
        description="Generate a TLC-FC conformance report."
    )
    parser.add_argument(
        "--report", type=Path, required=True, help="Output JSON report path."
    )
    parser.add_argument(
        "--handoff",
        type=Path,
        default=_default_handoff_root(),
        help="Feature Handoff root (default: pinned tllib-specs checkout).",
    )
    parser.add_argument(
        "--bindings",
        type=Path,
        help="Explicit JSON qualification decisions for runtime features.",
    )
    parser.add_argument(
        "--allow-unqualified",
        action="store_true",
        help="Write the report without failing when features lack decisions.",
    )
    options = parser.parse_args(arguments)
    try:
        handoffs = load_handoffs(options.handoff)
        bindings = load_bindings(options.bindings) if options.bindings else ()
        report = build_report(handoffs, bindings)
        write_report(report, options.report)
    except (HandoffLoadError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    summary = report["summary"]
    if (
        isinstance(summary, dict)
        and summary.get("unqualified_feature_count")
        and not options.allow_unqualified
    ):
        print("ERROR: unqualified TLC-FC features remain", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
