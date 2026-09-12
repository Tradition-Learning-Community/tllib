"""Validation API for the Opaque Value contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import OpaqueValue


def validate(value: Mapping[str, Any]) -> OpaqueValue:
    return _validate(OpaqueValue, value)
