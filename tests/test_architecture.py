"""Architecture and port-boundary tests for tllib."""

import ast
from pathlib import Path

import pytest

from tllib.domains.master.errors import MasterError
from tllib.domains.master.models import Master
from tllib.domains.master.operations import list_masters
from tllib.domains.master.registry import MasterRegistry

DOMAIN_ROOT = Path(__file__).parents[1] / "src" / "tllib" / "domains"
FORBIDDEN_IMPORT_ROOTS = frozenset(
    {
        "adapters",
        "boto3",
        "django",
        "fastapi",
        "flask",
        "httpx",
        "infrastructure",
        "os",
        "pathlib",
        "psycopg",
        "requests",
        "socket",
        "sqlalchemy",
        "sqlite3",
        "urllib",
    }
)


def _forbidden_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    violations: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            imported_names = [node.module] if node.module else []
            if node.module is None:
                imported_names.extend(alias.name for alias in node.names)
        else:
            continue
        violations.extend(
            name
            for name in imported_names
            if name
            and any(
                component in FORBIDDEN_IMPORT_ROOTS for component in name.split(".")
            )
        )
    return violations


def test_domain_imports_do_not_depend_on_infrastructure() -> None:
    domain_modules = DOMAIN_ROOT.rglob("*.py")

    violations = {
        str(path.relative_to(DOMAIN_ROOT)): imports
        for path in domain_modules
        if (imports := _forbidden_imports(path))
    }

    assert violations == {}


def test_architecture_rule_rejects_an_infrastructure_import(tmp_path: Path) -> None:
    module = tmp_path / "broken_domain.py"
    module.write_text("import sqlalchemy\n", encoding="utf-8")

    assert _forbidden_imports(module) == ["sqlalchemy"]


class InMemoryMasterProvider:
    def list_masters(self) -> list[Master]:
        return [Master(name="Ada")]


def test_list_masters_delegates_to_the_port() -> None:
    assert list(list_masters(InMemoryMasterProvider())) == [Master(name="Ada")]


def test_registry_rejects_missing_provider() -> None:
    with pytest.raises(MasterError, match="No master provider"):
        MasterRegistry().provider()


def test_registry_returns_registered_provider() -> None:
    provider = InMemoryMasterProvider()
    registry = MasterRegistry()

    registry.register(provider)

    assert registry.provider() is provider
