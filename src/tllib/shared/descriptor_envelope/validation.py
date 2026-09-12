"""Validation API for the Descriptor Envelope contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import DescriptorEnvelope


def validate(value: Mapping[str, Any]) -> DescriptorEnvelope:
    return _validate(DescriptorEnvelope, value)
