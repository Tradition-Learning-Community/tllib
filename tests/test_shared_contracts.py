"""Valid and invalid cases for the eight pinned shared contracts."""

import json

import pytest

from tllib.shared import (
    DescriptorEnvelope,
    FeatureIdentifier,
    OpaqueValue,
    ReferenceCollection,
    ScientificReference,
    StructuredError,
    Traceability,
    UnresolvedItem,
)
from tllib.shared._api import from_json, to_json
from tllib.shared._base import ContractModel, ContractValidationError

REFERENCE = {"source_path": "maths/README.md", "section": "Definitions"}


def test_all_published_contracts_validate_and_serialize_deterministically() -> None:
    values = [
        FeatureIdentifier.from_mapping({"value": "TLC-FC-00-MASTER-001"}),
        ScientificReference.from_mapping(REFERENCE),
        OpaqueValue.from_mapping(
            {
                "semantic_type_id": "TLC-VALUE-001",
                "payload": {"raw": "preserve me"},
                "source_reference": REFERENCE,
            }
        ),
        ReferenceCollection.from_mapping(
            {
                "kind": "sequence",
                "membership": "open",
                "cardinality": {"minimum": 0, "maximum": None},
                "ordering": "preserved",
                "duplicates": "allowed",
                "key_contract": None,
                "value_contract": {
                    "shared_contract_ref": "TLC-HC-SCIENTIFIC-REFERENCE@1.0.0"
                },
            }
        ),
        StructuredError.from_mapping(
            {
                "code": "MASTER-INVALID",
                "category": "validation",
                "condition": "name missing",
                "recoverability": "non_retryable",
                "public_result": "error_only",
                "failure_atomicity": "no_observable_partial_result",
                "context": {"field": "name"},
                "transport": "implementation_defined",
            }
        ),
        Traceability.from_mapping(
            {
                "scientific_sources": [REFERENCE],
                "mathematical_contracts": [],
                "source_irs": [],
                "finalized_irs": [],
                "algorithm_specifications": [],
                "test_plans": [],
                "acceptance_oracles": [],
                "scientific_decisions": [],
            }
        ),
        UnresolvedItem.from_mapping(
            {
                "unresolved_id": "UNR-001",
                "classification": "missing_definition",
                "source_reference": REFERENCE,
                "blocking_scope": "master",
                "status": "preserved_unresolved",
            }
        ),
        DescriptorEnvelope.from_mapping(
            {
                "feature_id": "TLC-FC-00-MASTER-001",
                "representation": "record",
                "references": [REFERENCE],
                "unresolved": [],
                "dependencies": [],
                "provenance": {"scientific_sources": [REFERENCE]},
                "status": {"state": "finalized"},
            }
        ),
    ]

    for value in values:
        serialized = to_json(value)
        assert serialized == to_json(value)
        assert json.loads(serialized) == value.to_mapping()


def test_opaque_payload_is_preserved_without_interpretation() -> None:
    payload = {"unit": "unknown", "expression": "x + 1"}
    value = OpaqueValue.from_mapping(
        {
            "semantic_type_id": "TLC-VALUE-001",
            "payload": payload,
            "source_reference": REFERENCE,
        }
    )

    assert value.to_mapping()["payload"] == payload


def test_json_round_trip_revalidates_the_same_structure() -> None:
    value = FeatureIdentifier.from_mapping({"value": "TLC-FC-01-DISCIPLE-001"})
    restored = from_json(FeatureIdentifier, to_json(value))

    assert restored == value
    assert hash(restored) == hash(value)


@pytest.mark.parametrize(
    "contract, invalid",
    [
        (FeatureIdentifier, {"value": "bad value"}),
        (ScientificReference, {"source_path": "../secret.md"}),
        (OpaqueValue, {"semantic_type_id": "x", "payload": {}, "source_reference": {}}),
        (
            ReferenceCollection,
            {
                "kind": "not_a_kind",
                "membership": "open",
                "cardinality": {"minimum": 0, "maximum": None},
                "ordering": "preserved",
                "duplicates": "allowed",
                "key_contract": None,
                "value_contract": None,
            },
        ),
        (StructuredError, {"code": "x"}),
        (Traceability, {"scientific_sources": [], "mathematical_contracts": []}),
        (UnresolvedItem, {"unresolved_id": "x", "status": "resolved"}),
        (DescriptorEnvelope, {"feature_id": "x"}),
    ],
)
def test_invalid_contracts_are_rejected(
    contract: type[ContractModel], invalid: dict[str, object]
) -> None:
    with pytest.raises(ContractValidationError):
        contract.from_mapping(invalid)


def test_cycles_are_rejected() -> None:
    cyclic: dict[str, object] = {"value": "TLC-FC-001"}
    cyclic["cycle"] = cyclic

    with pytest.raises(ContractValidationError, match="cyclic"):
        FeatureIdentifier.from_mapping(cyclic)


def test_unknown_fields_are_rejected() -> None:
    with pytest.raises(ContractValidationError, match="unknown fields"):
        FeatureIdentifier.from_mapping({"value": "TLC-FC-001", "meaning": "invented"})
