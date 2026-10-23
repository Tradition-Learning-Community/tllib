# Security policy — tllib

tllib is in pre-implementation V1 and does not yet distribute a
production C++ runtime or Python wheel. Security reports remain
important for future native memory safety, bindings, providers,
serialization, specification ingestion and supply-chain integrity.

## Responsible reporting

Do **not** disclose exploitable details in a public issue. Use
GitHub's **private vulnerability reporting** for this repository if
enabled. If unavailable, contact an authorized organization maintainer
through an established private channel before disclosing details
publicly. No unsupported email address or response SLA is promised.

Include the affected commit, platform, TLC-FC/specs snapshot if relevant,
risk, reproduction, and affected trust boundary. Scientific
contradictions in upstream contracts belong in `tllib-specs`; defects
in native consumers, bindings or packaging belong here.

Maintainers should triage, protect reporter privacy, prepare a focused
fix, test the original failure and publish an advisory when users need
to respond.

No production support or vulnerability response window is claimed
until the association adopts one explicitly.
