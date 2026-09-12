"""Serialization API for the Descriptor Envelope contract."""

from .._api import from_json, to_json
from .models import DescriptorEnvelope

__all__ = ["DescriptorEnvelope", "from_json", "to_json"]
