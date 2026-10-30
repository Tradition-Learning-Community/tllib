# Compatibility implementation — #14

- **Software**: SemVer `0.1.0` shared by CMake, wheel, runtime version;
  `SameMinorVersion` for a CMake package during the pre-1.0 cycle.
  No universal C++ ABI contract; no Python abi3/free-threaded promise.
- **Python**: CPython 3.12 wheel on Linux x86-64 only is CI-verified at
  this time; `requires-python >=3.12,<3.13` matches this validated set.
  Additional interpreters and OSs require tests and an explicit change.
- **Scientific source**: exact `specs.lock.json` SHA, catalog hash and model
  version, independently mirrored in generated C++/JSON metadata.
  An unknown SHA is **not** an interchangeable snapshot, even if JSON parses.
  A changed TLC-FC is never automatically supported.
- **Runtime/provider**: existing interface versions checked natively;
  unknown contracts or versions must be rejected, not silently coerced.
  A serialization or shared-contract version change requires a reviewed
  migration, independent of the `tllib` SemVer.
- **Deprecation**: announce affected symbols, first deprecated release,
  replacement and migration steps in the PR and changelog. A 0.x breaking
  change needs an explicit migration note. Do not remove without review;
  after 1.0 observe SemVer and a published deprecation window.
- **Lock update**: run `specs_sync.py` offline, review `migration.json` /
  `migration.md`, implement tests, and submit a separate PR for the lock
  and generated files. No automatic upgrade or domain activation.

Machine-checkable policy:

```sh
python3 tools/compatibility.py
python3 -m unittest discover -s tests/specs -p 'test_compatibility.py' -v
```

`compatibility.py --output build/compat` writes deterministic JSON with
the software/specs version pair; mismatches fail CI. It does not pretend
that all feature implementations or formats are mature. Release artifacts
and actual platform support remain gated separately by #11 and #260.

The `conformance/deprecations.json` ledger starts with **zero** entries:
no public API has been invented as deprecated. When a symbol becomes
deprecated, the registry requires its precise symbol, initial SemVer,
a strictly later earliest removal version, replacement and an existing
safe `docs/v1/*` migration note. Broken ledgers fail the same compatibility
gate, with synthetic negative tests.
