"""Validation API for the Scientific Reference contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import ScientificReference


def validate(value: Mapping[str, Any]) -> ScientificReference:
    return _validate(ScientificReference, value)
