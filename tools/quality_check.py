#!/usr/bin/env python3
"""Small changed-file quality gate, no rewriting of existing large source trees.

Requires clang-format and ruff on PATH. New Python files are fully formatted;
edited existing Python files are linted, C++ changed lines are clang-formatted.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
import subprocess
import sys

HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args],
        text=True,
        timeout=30,
    )


def modified(root: Path, base: str) -> list[tuple[str, str]]:
    output = git(root, "diff", "--name-status", "--no-renames", base, "HEAD")
    files: list[tuple[str, str]] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        status, path = line.split("\t", 1)
        if status[0] in ("A", "M") and (
            path.endswith(".py") or path.endswith(".hpp") or path.endswith(".cpp")
        ):
            files.append((status[0], path))
    return sorted(files, key=lambda item: item[1])


def changed_lines(root: Path, base: str, path: str) -> list[str]:
    diff = git(root, "diff", "--unified=0", "--no-ext-diff", base, "HEAD", "--", path)
    result = []
    for line in diff.splitlines():
        match = HUNK.match(line)
        if match:
            first = int(match.group(1))
            count = int(match.group(2) or 1)
            if count:
                result.append(f"--lines={first}:{first + count - 1}")
    return result


def invoke(argv: list[str]) -> bool:
    print("+", " ".join(argv), flush=True)
    return subprocess.run(argv, check=False, timeout=120).returncode == 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Verified base commit, e.g. HEAD^")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args(argv)
    root = args.root.resolve()
    files = modified(root, args.base)
    failed = False
    for status, path in files:
        full = root / path
        if not full.is_file() or not full.resolve().is_relative_to(root):
            print("Invalid project path:", path, file=sys.stderr)
            failed = True
            continue
        if path.endswith(".py"):
            failed |= not invoke(["ruff", "check", "--config", str(root / "ruff.toml"), str(full)])
            if status == "A":
                failed |= not invoke(
                    ["ruff", "format", "--check", "--config", str(root / "ruff.toml"), str(full)]
                )
        else:
            ranges = changed_lines(root, args.base, path)
            if ranges:
                failed |= not invoke(["clang-format", "--dry-run", "--Werror", *ranges, str(full)])
    print(f"quality: {len(files)} source files checked; failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
