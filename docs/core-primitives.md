# Core primitives

The `tllib.core` package provides small, dependency-free contracts shared by
domains. These types carry value semantics and keep serialization and error
handling consistent at domain boundaries.

## Identifiers and versions

`Identifier("master.alpha")` accepts portable identifiers made of ASCII
letters, digits, `.`, `_`, and `-`. `Version.parse("1.2.3")` accepts strict
`major.minor.patch` versions. Both are frozen, comparable, and hashable, so
they can safely be used as dictionary keys or set members.

## Status and errors

`Status` describes a lifecycle (`pending`, `running`, `succeeded`, `failed`).
`ResultStatus` describes whether a `Result` is successful. `TLCError` and its
`ValidationError`, `NotFoundError`, and `ConflictError` subclasses expose a
stable `code`, a human-readable message, and a JSON-compatible `context`.

## Results and JSON

Use `Result.ok(value)` for a value and `Result.failure(error)` for a domain
failure. `unwrap()` returns the value or raises the contained `TLCError`.
`to_canonical_json(value)` produces deterministic JSON with sorted keys and
compact separators; `from_json()` decodes the JSON structure for a caller to
reconstruct its domain type.

```python
from tllib.core import Identifier, Result, ValidationError, Version
from tllib.core import to_canonical_json

master_id = Identifier("master.ada")
contract_version = Version.parse("1.0.0")
result = Result.failure(
    ValidationError("Master name is required", {"id": str(master_id)})
)
payload = to_canonical_json(result)
```

Domains should depend on these primitives for identifiers, operation outcomes,
and boundary errors. They should keep scientific models and domain-specific
rules in the domain package; adapters should only translate external data into
these stable types.