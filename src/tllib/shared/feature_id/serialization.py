"""Serialization API for the Feature Identifier contract."""

from .._api import from_json, to_json
from .models import FeatureIdentifier

__all__ = ["FeatureIdentifier", "from_json", "to_json"]
