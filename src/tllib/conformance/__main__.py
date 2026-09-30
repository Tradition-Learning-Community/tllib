"""CLI for deterministic Feature Handoff conformance reporting."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .loader import HandoffLoadError, load_handoffs
from .report import build_report, write_report


def _default_handoff_root() -> Path:
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
        help="Feature Handoff Package root (default: sibling tllib-specs/handoff).",
    )
    options = parser.parse_args(arguments)
    try:
        write_report(build_report(load_handoffs(options.handoff)), options.report)
    except (HandoffLoadError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
