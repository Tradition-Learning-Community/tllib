"""Validation API for the Reference Collection contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import ReferenceCollection


def validate(value: Mapping[str, Any]) -> ReferenceCollection:
    return _validate(ReferenceCollection, value)
