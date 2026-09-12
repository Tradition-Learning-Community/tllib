"""Serialization API for the Traceability contract."""

from .._api import from_json, to_json
from .models import Traceability

__all__ = ["Traceability", "from_json", "to_json"]
