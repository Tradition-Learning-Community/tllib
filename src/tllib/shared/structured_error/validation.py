"""Validation API for the Structured Error contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import StructuredError


def validate(value: Mapping[str, Any]) -> StructuredError:
    return _validate(StructuredError, value)
