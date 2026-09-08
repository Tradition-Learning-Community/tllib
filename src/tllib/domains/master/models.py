"""Data models for the master domain."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Master:
    """A named master-domain entity."""

    name: str