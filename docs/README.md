# tllib documentation

Documentation for the public API and domain contracts belongs in this directory.

Shared runtime primitives are documented in [core-primitives.md](core-primitives.md).
Explicit provider injection is documented in [providers.md](providers.md).
Feature Handoff conformance reporting is documented in [conformance.md](conformance.md).
Explicit TLC-FC implementation discovery is documented in [discovery.md](discovery.md).
Domain modules should use `tllib.core` for immutable identifiers and versions,
stable statuses, serializable errors, explicit `Result` outcomes, and canonical
JSON. This keeps ports and adapters independent from infrastructure while
leaving domain-specific semantics in their owning domain.
