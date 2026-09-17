"""Tests for the specification snapshot lock."""

import json
from pathlib import Path
from typing import cast

import pytest

import tllib
from tllib.specs.lock import SpecificationLockError, load_lock

REPOSITORY_ROOT = Path(__file__).parents[1]
LOCK_PATH = REPOSITORY_ROOT / "specs.lock.json"
SPECS_ROOT = REPOSITORY_ROOT.parent / "tllib-specs"


@pytest.fixture
def patch_git_value(monkeypatch: pytest.MonkeyPatch) -> None:
    lock_payload = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    def fake_git_value(_specs_root: Path, *arguments: str) -> str:
        if arguments == ("remote", "get-url", "origin"):
            return cast(str, lock_payload["repository"])
        if arguments == ("rev-parse", "HEAD"):
            return cast(str, lock_payload["sha"])
        raise AssertionError(f"Unexpected git arguments: {arguments}")

    monkeypatch.setattr("tllib.specs.lock._git_value", fake_git_value)


@pytest.fixture
def patch_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_bytes = json.dumps({"model_version": "1.0.0"}).encode("utf-8")
    original_read_bytes = Path.read_bytes

    def fake_read_bytes(path: Path) -> bytes:
        if path.name == "catalog.json":
            return catalog_bytes
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)


def test_valid_specification_lock_and_public_info(patch_git_value: None) -> None:
    lock = load_lock(LOCK_PATH, SPECS_ROOT)

    assert lock.version == "1.0.0"
    assert tllib.specification_info() == lock.as_dict()


def test_divergent_fingerprint_is_rejected(
    tmp_path: Path, patch_git_value: None, patch_catalog: None
) -> None:
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
    tmp_path: Path,
    field: str,
    message: str,
    patch_git_value: None,
    patch_catalog: None,
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
