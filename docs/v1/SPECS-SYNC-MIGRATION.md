# Specs snapshot synchronization — #244 / #14

`python3 tools/specs_sync.py --reference-specs /local/ref --candidate-specs /local/candidate --candidate-lock /local/candidate.lock.json --output build/specs-sync`

The reference lock defaults to `specs.lock.json` (unchanged). The candidate lock
is an **independent review input** and must identify its checkout's exact Git HEAD,
catalog SHA-256, supported schema, and verification method. The tool verifies
**both** sources with the existing offline handoff verifier, including all
packages, shared contracts, manifests, acceptance data, provenance and dependencies.
It never clones/fetches and never evaluates handoff content.

Outputs: `migration.json` (canonical UTF-8, sorted keys, stable arrays) and
`migration.md` (migration checklist). Identical snapshots exit 0; any change
produces `review_required` and exits 1; invalid/corrupt source exits 2.
Catalog, domain and feature identity, statuses, versions, paths, fingerprints,
dependency metadata and hashes of all declared package/acceptance/manifest/
traceability/shared files are compared. Changed science is **never** deemed
compatible merely because it remains valid JSON; removals are classified as
potentially breaking and additions as unimplemented gaps.

**No automatic lock update.** First review the diff and missing
domain evidence, obtain human scientific/compatibility approval, add separate
tests and mapping decisions, and submit a distinct PR changing
`specs.lock.json` and regenerated data. Do not create issues automatically.
Synthetic fixtures in `tests/specs/test_specs_sync.py` are software test data,
not TLC-FC implementations.
