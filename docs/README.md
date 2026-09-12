# tllib documentation

Documentation for the public API and domain contracts belongs in this directory.

Shared runtime primitives are documented in [core-primitives.md](core-primitives.md).
Domain modules should use `tllib.core` for immutable identifiers and versions,
stable statuses, serializable errors, explicit `Result` outcomes, and canonical
JSON. This keeps ports and adapters independent from infrastructure while
leaving domain-specific semantics in their owning domain.