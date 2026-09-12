"""Command-line entry point for specification lock operations."""

import argparse

from .lock import SpecificationLockError, verify_lock


def main() -> int:
    parser = argparse.ArgumentParser(prog="python -m tllib.specs")
    parser.add_argument("command", choices=["verify"])
    args = parser.parse_args()

    if args.command == "verify":
        try:
            lock = verify_lock()
        except SpecificationLockError as exc:
            parser.error(str(exc))
        print(
            f"verified specifications: {lock.version} at {lock.sha} "
            f"({lock.fingerprint})"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
