"""Tests for the specification snapshot lock."""

import json
from pathlib import Path

import pytest

import tllib
from tllib.specs.lock import SpecificationLockError, load_lock

REPOSITORY_ROOT = Path(__file__).parents[1]
LOCK_PATH = REPOSITORY_ROOT / "specs.lock.json"
SPECS_ROOT = REPOSITORY_ROOT.parent / "tllib-specs"


def test_valid_specification_lock_and_public_info() -> None:
    lock = load_lock(LOCK_PATH, SPECS_ROOT)

    assert lock.version == "1.0.0"
    assert tllib.specification_info() == lock.as_dict()


def test_divergent_fingerprint_is_rejected(tmp_path: Path) -> None:
    payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    payload["fingerprint"] = "sha256:" + "0" * 64
    divergent_lock = tmp_path / "specs.lock.json"
    divergent_lock.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(
        SpecificationLockError,
        match="fingerprint diverges",
    ):
        load_lock(divergent_lock, SPECS_ROOT)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("{", "Invalid JSON"),
        ("[]", "JSON object"),
        ('{"repository": "only"}', "exactly five"),
        (
            json.dumps(
                {
                    "repository": "x",
                    "sha": "X" * 40,
                    "version": "1.0.0",
                    "fingerprint": "sha256:" + "0" * 64,
                    "date": "2026-09-11",
                }
            ),
            "lowercase Git SHA",
        ),
        (
            json.dumps(
                {
                    "repository": "x",
                    "sha": "0" * 40,
                    "version": "1.0.0",
                    "fingerprint": "md5:" + "0" * 32,
                    "date": "2026-09-11",
                }
            ),
            "sha256",
        ),
        (
            json.dumps(
                {
                    "repository": "x",
                    "sha": "0" * 40,
                    "version": "1.0.0",
                    "fingerprint": "sha256:" + "Z" * 64,
                    "date": "2026-09-11",
                }
            ),
            "lowercase hexadecimal",
        ),
        (
            json.dumps(
                {
                    "repository": "x",
                    "sha": "0" * 40,
                    "version": "1.0.0",
                    "fingerprint": "sha256:" + "0" * 64,
                    "date": "invalid",
                }
            ),
            "YYYY-MM-DD",
        ),
    ],
)
def test_invalid_lock_formats_are_rejected(
    tmp_path: Path, content: str, message: str
) -> None:
    lock_path = tmp_path / "specs.lock.json"
    lock_path.write_text(content, encoding="utf-8")

    with pytest.raises(SpecificationLockError, match=message):
        load_lock(lock_path, SPECS_ROOT)


@pytest.mark.parametrize(
    ("field", "message"),
    [
        ("repository", "repository diverges"),
        ("sha", "SHA diverges"),
        ("version", "version diverges"),
    ],
)
def test_lock_metadata_divergence_is_rejected(
    tmp_path: Path, field: str, message: str
) -> None:
    payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    payload[field] = {
        "repository": "https://example.invalid/specs.git",
        "sha": "0" * 40,
        "version": "0.0.0",
    }[field]
    lock_path = tmp_path / "specs.lock.json"
    lock_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(SpecificationLockError, match=message):
        load_lock(lock_path, SPECS_ROOT)
