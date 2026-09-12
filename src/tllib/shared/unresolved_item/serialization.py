"""Serialization API for the Unresolved Item contract."""

from .._api import from_json, to_json
from .models import UnresolvedItem

__all__ = ["UnresolvedItem", "from_json", "to_json"]
