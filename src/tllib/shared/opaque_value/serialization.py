"""Serialization API for the Opaque Value contract."""

from .._api import from_json, to_json
from .models import OpaqueValue

__all__ = ["OpaqueValue", "from_json", "to_json"]
