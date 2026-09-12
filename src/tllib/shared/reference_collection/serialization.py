"""Serialization API for the Reference Collection contract."""

from .._api import from_json, to_json
from .models import ReferenceCollection

__all__ = ["ReferenceCollection", "from_json", "to_json"]
