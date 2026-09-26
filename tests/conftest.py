"""Shared pytest fixtures."""

from pathlib import Path

import pytest

FAKE_SPECS_REPOSITORY = "https://example.invalid/tllib-specs.git"
FAKE_SPECS_SHA = "0123456789abcdef0123456789abcdef01234567"


@pytest.fixture
def specs_git_values() -> dict[str, str]:
    """Return the simulated Git metadata used by specification tests."""

    return {"repository": FAKE_SPECS_REPOSITORY, "sha": FAKE_SPECS_SHA}


@pytest.fixture
def patch_specs_git(
    monkeypatch: pytest.MonkeyPatch, specs_git_values: dict[str, str]
) -> None:
    """Make specification-lock tests independent from a Git checkout."""

    def fake_git_value(_specs_root: Path, *arguments: str) -> str:
        if arguments == ("remote", "get-url", "origin"):
            return specs_git_values["repository"]
        if arguments == ("rev-parse", "HEAD"):
            return specs_git_values["sha"]
        raise AssertionError(f"Unexpected git arguments: {arguments}")

    monkeypatch.setattr("tllib.specs.lock._git_value", fake_git_value)
    monkeypatch.setattr(
        "tllib.specs.lock.EXPECTED_REPOSITORY", specs_git_values["repository"]
    )
