"""Validation API for the Traceability contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import Traceability


def validate(value: Mapping[str, Any]) -> Traceability:
    return _validate(Traceability, value)
