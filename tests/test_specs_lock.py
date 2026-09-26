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
def lock_payload(specs_git_values: dict[str, str]) -> dict[str, str]:
    payload = cast(dict[str, str], json.loads(LOCK_PATH.read_text(encoding="utf-8")))
    payload.update(specs_git_values)
    return payload


@pytest.fixture
def patch_catalog(monkeypatch: pytest.MonkeyPatch) -> None:
    catalog_bytes = json.dumps({"model_version": "1.0.0"}).encode("utf-8")
    original_read_bytes = Path.read_bytes

    def fake_read_bytes(path: Path) -> bytes:
        if path.name == "catalog.json":
            return catalog_bytes
        return original_read_bytes(path)

    monkeypatch.setattr(Path, "read_bytes", fake_read_bytes)


def test_valid_specification_lock_and_public_info(
    tmp_path: Path,
    lock_payload: dict[str, str],
    monkeypatch: pytest.MonkeyPatch,
    patch_specs_git: None,
) -> None:
    lock_path = tmp_path / "specs.lock.json"
    lock_path.write_text(json.dumps(lock_payload), encoding="utf-8")
    default_lock_path = "tllib.specs.lock._default_lock_path"
    monkeypatch.setattr(default_lock_path, lambda: lock_path)
    monkeypatch.setattr(
        "tllib.specs.lock._default_specs_root", lambda _path: SPECS_ROOT
    )
    lock = load_lock(lock_path, SPECS_ROOT)

    assert lock.version == "1.0.0"
    assert tllib.specification_info() == lock.as_dict()


def test_divergent_fingerprint_is_rejected(
    tmp_path: Path,
    lock_payload: dict[str, str],
    patch_specs_git: None,
    patch_catalog: None,
) -> None:
    lock_payload["fingerprint"] = "sha256:" + "0" * 64
    divergent_lock = tmp_path / "specs.lock.json"
    divergent_lock.write_text(json.dumps(lock_payload), encoding="utf-8")

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
    lock_payload: dict[str, str],
    patch_specs_git: None,
    patch_catalog: None,
) -> None:
    lock_payload[field] = {
        "repository": "https://example.invalid/specs.git",
        "sha": "0" * 40,
        "version": "0.0.0",
    }[field]
    lock_path = tmp_path / "specs.lock.json"
    lock_path.write_text(json.dumps(lock_payload), encoding="utf-8")

    with pytest.raises(SpecificationLockError, match=message):
        load_lock(lock_path, SPECS_ROOT)
