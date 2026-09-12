"""Serialization API for the Scientific Reference contract."""

from .._api import from_json, to_json
from .models import ScientificReference

__all__ = ["ScientificReference", "from_json", "to_json"]
