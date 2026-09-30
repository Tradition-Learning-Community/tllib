"""Explicit, immutable registrations compared with the Feature Handoff catalog."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path

from tllib.core.identifiers import Identifier, Version


class DiscoveryError(ValueError):
    """Base error for invalid implementation discovery data."""


class DuplicateImplementationError(DiscoveryError):
    """Raised when a feature or domain is registered more than once."""


class UnknownFeatureError(DiscoveryError):
    """Raised when an implementation does not exist in the supplied catalog."""


class IncompatibleVersionError(DiscoveryError):
    """Raised when an implementation targets a different package version."""


@dataclass(frozen=True, slots=True)
class FeatureImplementation:
    """Immutable registration of one TLC-FC feature implementation."""

    feature_id: str
    package_version: str
    target: str

    def __post_init__(self) -> None:
        Identifier(self.feature_id)
        Version.parse(self.package_version)
        if not isinstance(self.target, str) or not self.target:
            raise ValueError("Implementation target must be a non-empty string")


@dataclass(frozen=True, slots=True)
class DomainImplementation:
    """Immutable explicit collection of feature implementations for one domain."""

    domain: str
    features: tuple[FeatureImplementation, ...]

    def __post_init__(self) -> None:
        Identifier(self.domain)
        features = tuple(self.features)
        feature_ids = [feature.feature_id for feature in features]
        if len(feature_ids) != len(set(feature_ids)):
            raise DuplicateImplementationError(
                f"Domain {self.domain} declares a feature more than once"
            )
        object.__setattr__(self, "features", features)


@dataclass(frozen=True, slots=True)
class CatalogFeature:
    """The catalog data required to validate a feature implementation."""

    feature_id: str
    domain: str
    package_version: str

    def __post_init__(self) -> None:
        Identifier(self.feature_id)
        Identifier(self.domain)
        Version.parse(self.package_version)


@dataclass(frozen=True, slots=True)
class CatalogComparison:
    """Deterministic differences between registered and catalogued features."""

    missing_feature_ids: tuple[str, ...]
    partial_domains: Mapping[str, tuple[str, ...]]

    @property
    def is_complete(self) -> bool:
        """Return whether every catalogued feature is explicitly registered."""
        return not self.missing_feature_ids


def _catalog_object(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, dict) or not all(isinstance(key, str) for key in value):
        raise DiscoveryError(f"{label} must be an object")
    return value


def _catalog_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DiscoveryError(f"{label} must be a non-empty string")
    return value


def catalog_features(catalog: Mapping[str, object]) -> tuple[CatalogFeature, ...]:
    """Extract the feature inventory needed by the explicit registry."""
    raw_features = catalog.get("features")
    if not isinstance(raw_features, list):
        raise DiscoveryError("Catalog features must be a list")
    features: list[CatalogFeature] = []
    seen: set[str] = set()
    for raw_feature in raw_features:
        feature = _catalog_object(raw_feature, "Catalog feature")
        item = CatalogFeature(
            feature_id=_catalog_string(feature.get("feature_id"), "feature_id"),
            domain=_catalog_string(feature.get("domain"), "domain"),
            package_version=_catalog_string(
                feature.get("package_version"), "package_version"
            ),
        )
        if item.feature_id in seen:
            raise DuplicateImplementationError(
                f"Catalog declares feature {item.feature_id} more than once"
            )
        seen.add(item.feature_id)
        features.append(item)
    return tuple(features)


def load_catalog(catalog_path: Path) -> tuple[CatalogFeature, ...]:
    """Load a catalog JSON file into immutable feature metadata."""
    try:
        value = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DiscoveryError(f"Unable to load catalog: {catalog_path}") from exc
    return catalog_features(_catalog_object(value, "Catalog"))


class ImplementationRegistry:
    """Registry populated only by explicit, catalog-validated registrations."""

    def __init__(self, catalog: Iterable[CatalogFeature]) -> None:
        self._catalog = {feature.feature_id: feature for feature in catalog}
        if not self._catalog:
            raise DiscoveryError("Implementation registry requires a non-empty catalog")
        self._domains: dict[str, DomainImplementation] = {}
        self._features: dict[str, FeatureImplementation] = {}

    def register(self, implementation: DomainImplementation) -> None:
        """Register one domain after validating every feature against the catalog."""
        if implementation.domain in self._domains:
            raise DuplicateImplementationError(
                f"Domain {implementation.domain} is already registered"
            )
        for feature in implementation.features:
            if feature.feature_id in self._features:
                raise DuplicateImplementationError(
                    f"Feature {feature.feature_id} is already registered"
                )
            expected = self._catalog.get(feature.feature_id)
            if expected is None:
                raise UnknownFeatureError(
                    f"Feature {feature.feature_id} is absent from the catalog"
                )
            if expected.domain != implementation.domain:
                raise UnknownFeatureError(
                    f"Feature {feature.feature_id} belongs to domain {expected.domain}"
                )
            if expected.package_version != feature.package_version:
                raise IncompatibleVersionError(
                    f"Feature {feature.feature_id} requires version "
                    f"{expected.package_version}, got {feature.package_version}"
                )
        self._domains[implementation.domain] = implementation
        self._features.update(
            {feature.feature_id: feature for feature in implementation.features}
        )

    def list(self, domain: str | None = None) -> tuple[FeatureImplementation, ...]:
        """List registered features in stable feature-ID order."""
        features = (
            self._features.values()
            if domain is None
            else self._domains.get(domain, DomainImplementation(domain, ())).features
        )
        return tuple(sorted(features, key=lambda item: item.feature_id))

    def find(self, feature_id: str) -> FeatureImplementation | None:
        """Return one registered feature or ``None`` when it is not registered."""
        return self._features.get(feature_id)

    def compare(self) -> CatalogComparison:
        """Compare all registrations with the authoritative catalog snapshot."""
        missing = tuple(sorted(set(self._catalog) - set(self._features)))
        partial: dict[str, tuple[str, ...]] = {}
        for domain in sorted(self._domains):
            expected = {
                feature.feature_id
                for feature in self._catalog.values()
                if feature.domain == domain
            }
            registered = {
                feature.feature_id for feature in self._domains[domain].features
            }
            domain_missing = tuple(sorted(expected - registered))
            if domain_missing:
                partial[domain] = domain_missing
        return CatalogComparison(missing, partial)


def list_implementations(
    registry: ImplementationRegistry, domain: str | None = None
) -> tuple[FeatureImplementation, ...]:
    """List explicit implementations from a registry."""
    return registry.list(domain)


def find_implementation(
    registry: ImplementationRegistry, feature_id: str
) -> FeatureImplementation | None:
    """Find one explicit implementation by its TLC-FC ID."""
    return registry.find(feature_id)


def compare_to_catalog(registry: ImplementationRegistry) -> CatalogComparison:
    """Compare explicit registrations with the registry's catalog snapshot."""
    return registry.compare()
