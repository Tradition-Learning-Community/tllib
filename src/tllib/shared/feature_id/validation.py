"""Validation API for the Feature Identifier contract."""

from collections.abc import Mapping
from typing import Any

from .._api import validate as _validate
from .models import FeatureIdentifier


def validate(value: Mapping[str, Any]) -> FeatureIdentifier:
    return _validate(FeatureIdentifier, value)
