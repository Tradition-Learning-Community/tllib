"""Load and verify the runtime's specification lock."""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path

LOCK_FILENAME = "specs.lock.json"
CATALOG_RELATIVE_PATH = Path("handoff") / "catalog.json"
EXPECTED_REPOSITORY = "https://github.com/skylore300-hash/tllib-specs.git"
SHA256_PREFIX = "sha256:"


class SpecificationLockError(ValueError):
    """Raised when the specification lock does not match its source."""


@dataclass(frozen=True, slots=True)
class SpecificationLock:
    """Metadata identifying the specification snapshot used by tllib."""

    repository: str
    sha: str
    version: str
    fingerprint: str
    date: str

    def as_dict(self) -> dict[str, str]:
        """Return the lock metadata as a JSON-compatible mapping."""
        return asdict(self)


def _default_lock_path() -> Path:
    return Path(__file__).resolve().parents[3] / LOCK_FILENAME


def _default_specs_root(lock_path: Path) -> Path:
    return lock_path.parent.parent / "tllib-specs"


def _read_lock(lock_path: Path) -> SpecificationLock:
    try:
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SpecificationLockError(f"Lock file not found: {lock_path}") from exc
    except json.JSONDecodeError as exc:
        raise SpecificationLockError(f"Invalid JSON in lock file: {lock_path}") from exc

    if not isinstance(payload, dict):
        raise SpecificationLockError("Lock file must contain a JSON object")

    required = {"repository", "sha", "version", "fingerprint", "date"}
    if set(payload) != required or not all(
        isinstance(payload[key], str) for key in required
    ):
        raise SpecificationLockError(
            "Lock file must contain exactly five string fields: "
            "repository, sha, version, fingerprint, date"
        )

    lock = SpecificationLock(**payload)
    if len(lock.sha) != 40 or any(
        character not in "0123456789abcdef" for character in lock.sha
    ):
        raise SpecificationLockError(
            "Lock SHA must be a 40-character lowercase Git SHA"
        )
    if not lock.fingerprint.startswith(SHA256_PREFIX) or len(lock.fingerprint) != 71:
        raise SpecificationLockError("Lock fingerprint must be a sha256:<64 hex> value")
    if any(character not in "0123456789abcdef" for character in lock.fingerprint[7:]):
        raise SpecificationLockError("Lock fingerprint must use lowercase hexadecimal")
    try:
        date.fromisoformat(lock.date)
    except ValueError as exc:
        raise SpecificationLockError("Lock date must use YYYY-MM-DD format") from exc
    return lock


def _git_value(specs_root: Path, *arguments: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(specs_root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise SpecificationLockError(
            f"Unable to inspect specification repository: {specs_root}"
        ) from exc
    return result.stdout.strip()


def _catalog_version_and_fingerprint(specs_root: Path) -> tuple[str, str]:
    catalog_path = specs_root / CATALOG_RELATIVE_PATH
    try:
        catalog_bytes = catalog_path.read_bytes()
        catalog = json.loads(catalog_bytes.decode("utf-8"))
    except (FileNotFoundError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise SpecificationLockError(
            f"Unable to read specification catalog: {catalog_path}"
        ) from exc
    version = catalog.get("model_version") if isinstance(catalog, dict) else None
    if not isinstance(version, str):
        raise SpecificationLockError("Specification catalog has no model_version")
    digest = hashlib.sha256(catalog_bytes).hexdigest()
    return version, f"{SHA256_PREFIX}{digest}"


def verify_lock(
    lock_path: Path | None = None,
    specs_root: Path | None = None,
) -> SpecificationLock:
    """Load the lock and verify it against the checked-out specifications."""
    resolved_lock_path = (lock_path or _default_lock_path()).resolve()
    lock = _read_lock(resolved_lock_path)
    resolved_specs_root = (
        specs_root or _default_specs_root(resolved_lock_path)
    ).resolve()

    repository = _git_value(resolved_specs_root, "remote", "get-url", "origin")
    if repository != lock.repository or repository != EXPECTED_REPOSITORY:
        raise SpecificationLockError(
            f"Specification repository diverges: expected {lock.repository}, "
            f"got {repository}"
        )

    sha = _git_value(resolved_specs_root, "rev-parse", "HEAD")
    if sha != lock.sha:
        raise SpecificationLockError(
            f"Specification SHA diverges: expected {lock.sha}, got {sha}"
        )

    version, fingerprint = _catalog_version_and_fingerprint(resolved_specs_root)
    if version != lock.version:
        raise SpecificationLockError(
            f"Specification version diverges: expected {lock.version}, got {version}"
        )
    if fingerprint != lock.fingerprint:
        raise SpecificationLockError(
            "Specification fingerprint diverges from handoff/catalog.json"
        )
    return lock


def load_lock(
    lock_path: Path | None = None,
    specs_root: Path | None = None,
) -> SpecificationLock:
    """Load and validate the default or explicitly supplied specification lock."""
    return verify_lock(lock_path=lock_path, specs_root=specs_root)
