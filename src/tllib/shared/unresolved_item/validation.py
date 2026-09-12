"""Validation API for the Unresolved Item contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import UnresolvedItem


def validate(value: Mapping[str, Any]) -> UnresolvedItem:
    return _validate(UnresolvedItem, value)
