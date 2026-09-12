"""Tests for shared tllib primitives."""

import pytest

import tllib
from tllib.core import (
    Identifier,
    Result,
    ResultStatus,
    Status,
    ValidationError,
    Version,
    from_json,
    to_canonical_json,
)
from tllib.domains.master.models import Master


def test_identifiers_and_versions_are_immutable_and_hashable() -> None:
    identifier = Identifier("master.alpha")
    same_identifier = Identifier("master.alpha")
    version = Version.parse("1.2.3")

    assert identifier == same_identifier
    assert hash(identifier) == hash(same_identifier)
    assert str(identifier) == "master.alpha"
    assert version == Version(1, 2, 3)
    assert hash(version) == hash(Version(1, 2, 3))
    assert str(version) == "1.2.3"
    with pytest.raises((AttributeError, TypeError)):
        identifier.value = "other"  # type: ignore[misc]


@pytest.mark.parametrize("value", ["", "-bad", "has space", "étiquette"])
def test_invalid_identifiers_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        Identifier(value)


@pytest.mark.parametrize("value", ["1", "1.2", "01.2.3", "1.2.3-beta"])
def test_invalid_versions_are_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        Version.parse(value)


def test_statuses_are_stable_strings() -> None:
    assert Status.SUCCEEDED.value == "succeeded"
    assert ResultStatus.ERROR.value == "error"
    assert to_canonical_json(Status.SUCCEEDED) == '"succeeded"'


def test_errors_have_stable_codes_and_serializable_context() -> None:
    error = ValidationError("Invalid master", {"field": "name", "retry": False})

    assert error.code == "validation_error"
    assert to_canonical_json(error) == (
        '{"code":"validation_error","context":{"field":"name",'
        '"retry":false},"message":"Invalid master"}'
    )


def test_result_success_and_failure_round_trip_to_canonical_json() -> None:
    success = Result.ok(Master("Ada"))
    failure: Result[Master] = Result.failure(ValidationError("Invalid master"))

    assert success.is_ok
    assert success.unwrap() == Master("Ada")
    assert failure.status is ResultStatus.ERROR
    with pytest.raises(ValidationError):
        failure.unwrap()
    assert from_json(to_canonical_json(failure)) == {
        "error": {
            "code": "validation_error",
            "context": {},
            "message": "Invalid master",
        },
        "status": "error",
        "value": None,
    }


@pytest.mark.parametrize(
    "status, value, error",
    [(ResultStatus.OK, None, ValidationError("bad")), (ResultStatus.ERROR, None, None)],
)
def test_result_invariants_are_enforced(
    status: ResultStatus, value: object | None, error: ValidationError | None
) -> None:
    with pytest.raises(ValueError):
        Result(status, value, error)


def test_domain_and_public_package_remain_compatible() -> None:
    assert Master("Ada").name == "Ada"
    assert "repository" in tllib.specification_info()
