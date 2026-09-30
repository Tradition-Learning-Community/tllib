"""Tests for explicit implementation discovery."""

import pytest

from tllib.discovery import (
    CatalogFeature,
    DomainImplementation,
    DuplicateImplementationError,
    FeatureImplementation,
    ImplementationRegistry,
    IncompatibleVersionError,
    UnknownFeatureError,
    compare_to_catalog,
    find_implementation,
    list_implementations,
)


@pytest.fixture
def catalog() -> tuple[CatalogFeature, ...]:
    return (
        CatalogFeature("TLC-FC-00-MASTER-001", "master", "1.0.0"),
        CatalogFeature("TLC-FC-00-MASTER-002", "master", "1.0.0"),
        CatalogFeature("TLC-FC-01-DISCIPLE-001", "disciple", "1.0.0"),
    )


def test_lists_and_finds_explicit_implementations(
    catalog: tuple[CatalogFeature, ...],
) -> None:
    feature = FeatureImplementation(
        "TLC-FC-00-MASTER-001", "1.0.0", "tllib.master.describe"
    )
    registry = ImplementationRegistry(catalog)
    registry.register(DomainImplementation("master", (feature,)))

    assert list_implementations(registry) == (feature,)
    assert list_implementations(registry, "disciple") == ()
    assert find_implementation(registry, feature.feature_id) is feature
    assert find_implementation(registry, "TLC-FC-99-UNKNOWN-001") is None


def test_rejects_duplicate_feature_registration(
    catalog: tuple[CatalogFeature, ...],
) -> None:
    feature = FeatureImplementation(
        "TLC-FC-00-MASTER-001", "1.0.0", "tllib.master.describe"
    )
    registry = ImplementationRegistry(catalog)
    registry.register(DomainImplementation("master", (feature,)))

    with pytest.raises(DuplicateImplementationError, match="already registered"):
        registry.register(DomainImplementation("master", (feature,)))


def test_rejects_unknown_feature_id(catalog: tuple[CatalogFeature, ...]) -> None:
    registry = ImplementationRegistry(catalog)

    with pytest.raises(UnknownFeatureError, match="absent from the catalog"):
        registry.register(
            DomainImplementation(
                "master",
                (
                    FeatureImplementation(
                        "TLC-FC-00-MASTER-999", "1.0.0", "tllib.master.unknown"
                    ),
                ),
            )
        )


def test_rejects_incompatible_package_version(
    catalog: tuple[CatalogFeature, ...],
) -> None:
    registry = ImplementationRegistry(catalog)

    with pytest.raises(IncompatibleVersionError, match="requires version 1.0.0"):
        registry.register(
            DomainImplementation(
                "master",
                (
                    FeatureImplementation(
                        "TLC-FC-00-MASTER-001", "2.0.0", "tllib.master.describe"
                    ),
                ),
            )
        )


def test_reports_a_partial_registered_domain(
    catalog: tuple[CatalogFeature, ...],
) -> None:
    registry = ImplementationRegistry(catalog)
    registry.register(
        DomainImplementation(
            "master",
            (
                FeatureImplementation(
                    "TLC-FC-00-MASTER-001", "1.0.0", "tllib.master.describe"
                ),
            ),
        )
    )

    comparison = compare_to_catalog(registry)

    assert comparison.missing_feature_ids == (
        "TLC-FC-00-MASTER-002",
        "TLC-FC-01-DISCIPLE-001",
    )
    assert comparison.partial_domains == {"master": ("TLC-FC-00-MASTER-002",)}
    assert not comparison.is_complete
