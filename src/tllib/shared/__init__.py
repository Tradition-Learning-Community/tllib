"""Published shared contract carriers from the pinned specification revision."""

from .descriptor_envelope import DescriptorEnvelope
from .feature_id import FeatureIdentifier
from .opaque_value import OpaqueValue
from .reference_collection import ReferenceCollection
from .scientific_reference import ScientificReference
from .structured_error import StructuredError
from .traceability import Traceability
from .unresolved_item import UnresolvedItem

PINNED_SPECS_SHA = "07439babd59c657354e3200ed24c55e2e3eeb72c"

__all__ = [
    "DescriptorEnvelope",
    "FeatureIdentifier",
    "OpaqueValue",
    "PINNED_SPECS_SHA",
    "ReferenceCollection",
    "ScientificReference",
    "StructuredError",
    "Traceability",
    "UnresolvedItem",
]
