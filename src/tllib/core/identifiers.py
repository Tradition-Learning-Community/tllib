"""Immutable identifiers and versions shared by tllib domains."""

from __future__ import annotations

import re
from dataclasses import dataclass

_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


@dataclass(frozen=True, slots=True)
class Identifier:
    """A non-empty, portable identifier with stable value semantics."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _IDENTIFIER_PATTERN.fullmatch(
            self.value
        ):
            raise ValueError("Identifier must match [A-Za-z0-9][A-Za-z0-9._-]*")

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Version:
    """A strict three-part semantic version without pre-release metadata."""

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        if any(
            not isinstance(part, int) or isinstance(part, bool) or part < 0
            for part in (self.major, self.minor, self.patch)
        ):
            raise ValueError("Version components must be non-negative integers")

    @classmethod
    def parse(cls, value: str) -> Version:
        """Parse a strict ``major.minor.patch`` version."""
        if not isinstance(value, str):
            raise ValueError("Version must be a string")
        match = _VERSION_PATTERN.fullmatch(value)
        if match is None:
            raise ValueError("Version must use major.minor.patch notation")
        return cls(*(int(component) for component in match.groups()))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
