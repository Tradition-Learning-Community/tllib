"""Tests for the stable public API required by the handoff boundary."""

import pytest

import tllib
from tllib.core import (
    DomainId,
    ExecutionStatus,
    FeatureId,
    FeatureNotExecutableError,
    InvariantViolationError,
    ProviderRequiredError,
    ScientificStatus,
    TllibError,
    VersionIncompatibleError,
    to_canonical_json,
)


def test_feature_and_domain_identities_are_distinct_and_validated() -> None:
    feature = FeatureId("TLC-FC-00-MASTER-001")
    domain = DomainId("master")

    assert str(feature) == "TLC-FC-00-MASTER-001"
    assert str(domain) == "master"
    assert feature != domain

    with pytest.raises(ValueError):
        FeatureId("master")
    with pytest.raises(ValueError):
        DomainId("Master")


def test_published_statuses_are_closed_enums() -> None:
    assert ExecutionStatus.EXECUTABLE.value == "executable"
    assert ExecutionStatus.STRUCTURAL_ONLY.value == "structural_only"
    assert ScientificStatus.PRESERVED_UNRESOLVED.value == "preserved_unresolved"


def test_common_errors_keep_stable_codes_and_feature_identity() -> None:
    feature = FeatureId("TLC-FC-00-MASTER-001")

    errors = [
        ProviderRequiredError("master.lookup", feature_id=feature),
        FeatureNotExecutableError(feature, "structural_only"),
        VersionIncompatibleError("1.0.0", "2.0.0", feature_id=feature),
        InvariantViolationError(feature, "invariant failed"),
    ]

    assert [error.code for error in errors] == [
        "provider_required",
        "feature_not_executable",
        "version_incompatible",
        "invariant_violation",
    ]
    assert all(error.feature_id == feature for error in errors)
    assert '"feature_id":"TLC-FC-00-MASTER-001"' in to_canonical_json(errors[0])


def test_public_package_exports_supported_primitives() -> None:
    assert tllib.FeatureId is FeatureId
    assert tllib.DomainId is DomainId
    assert tllib.TllibError is TllibError
    assert "FeatureId" in tllib.__all__
