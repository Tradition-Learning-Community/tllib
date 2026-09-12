"""Serialization API for the Structured Error contract."""

from .._api import from_json, to_json
from .models import StructuredError

__all__ = ["StructuredError", "from_json", "to_json"]
