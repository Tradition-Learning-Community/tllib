# Threat model — native tllib preparation V1 (#13)

**Scope:** runtime and providers C++20, CPython bridge, numeric buffers,
inert offline handoff ingestion, build, local packaging and CI.
**Not covered:** sandboxing hostile Python or native code, domain science,
a future public release signing service, GPU/abi3/free-threaded.

| Boundary | Threat | Control and evidence | Residual risk |
| --- | --- | --- | --- |
| External specs -> offline build | tampered commit/catalog, traversal, symlink escape, JSON bombs, duplicate identifiers, missing manifests/acceptance | exact Git SHA, Git object, clean handoff and SHA-256 pinned lock, strict relative paths, symlink rejection, size/depth bounds, duplicate keys, closed enums in `specs_pipeline.py`; negative synthetic tests | filesystem TOCTOU with adversarial concurrent mutation is not sandboxed; run on a trusted local checkout |
| Data -> native memory | shape/stride overflow, out-of-allocation, aliasing, misalignment, dangling borrowed view | `ArrayView::create` checks and native CTest; non-owning lifetime documented; ASan/UBSan CI for C++ tests | caller may free owner after construction; no global ownership tracking |
| Python buffer -> C++ | use-after-release, hidden copy, malicious exporter, pointer address leak | RAII `Py_buffer`, contiguous only, native dtype guards, explicit copy, pointer-free metadata and tests | a hostile in-process exporter can violate the Python buffer contract |
| Provider -> registry | absent/mismatched providers, non-Boolean validators, invalid payload, exceptions, recursion, callback after owner disposal | frozen registry, schema/version, validated opaque bytes, strong callback references, stable errors, cancellation/deadline outcome indeterminate and Python integration tests | providers run **inside the process**; arbitrary hostile code is NOT isolated |
| Python callback -> native | GIL races, destructor re-entry, reference leaks | GIL reacquisition, no callback in destructor, typed error categories, negative ownership/reentrancy tests | free-threaded CPython, subinterpreters and TSan unqualified |
| Contributor -> CI | untrusted PR running code, token exfiltration, cache poisoning, artifact injection | `pull_request` (never untrusted `pull_request_target`), `contents: read`, no secrets in these jobs, cache not a correctness oracle, no CI write to specs.lock | third-party action major tags mutable until pinned; privilege/GitHub action updates need security review |
| Build dependency -> wheel | compromised package index, transitive dependency, oversized build surface | explicit dependency versions for quality/spike, CMake offline except declared package install; separate env wheel smoke and consumer smoke | third-party package integrity and hashes not yet locked for release; SBOM/signing required by #11 |
| Artifacts -> users | forged or stale packages, unsupported ABI or snapshot | current package 0.1.0 metadata, exact fingerprint/version pair, local wheel import, no release publication | no release signatures/attestations yet; do not promise production provenance |

**Invariants:** scientific input is data, never imported/executed;
invalid values fail with stable codes; feature support never inferred
from metadata; all lock changes require a separately reviewed PR.
`tllib-specs` is not modified by this project phase.

**Applicable tests:** `tests/specs/test_specs_pipeline.py` negative
fixtures; `tests/specs/test_specs_sync.py` synthetic diffs; CTest memory
and providers, Python buffer/callback/lifetime tests; CI ASan/UBSan on
native C++ code. No claim of kernel/process isolation for provider code.
Release must add signed provenance/SBOM and full platform tests (#11/#13).
