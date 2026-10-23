# Governance — tllib

## Project home and stewardship

**tllib** is an open-source scientific software project of
**Tradition Learning Community ASBL** (the association), hosted in the
`Tradition-Learning-Community` GitHub organization. The association
sets project direction, manages maintainer access, accepts contributions,
and coordinates releases and project assets. The GitHub namespace is a
hosting location, not a legal instrument transferring copyright.

**Tradition Learning** denotes the scientific theory and research
programme; the **Tradition Learning Community** brings together people
who study and implement it. The mathematical domain called
`community` in the scientific model is distinct from the organization.

The repository's implementation and documentation are licensed under
**Apache-2.0** (see [LICENSE](LICENSE)), with [NOTICE](NOTICE) for
attributions. Independently authored contributions are also accepted
under Apache-2.0. This is a community project and not a promise that
the association owns every contributor's copyright.

## Copyright and contribution rights

- Original materials authored by or lawfully assigned to the
  association may belong to it; each third-party author keeps their
  copyright unless a separate, valid assignment provides otherwise.
- Every incoming contribution is submitted for distribution under the
  repository's Apache-2.0 terms with a DCO 1.1 sign-off certifying the
  contributor's right to submit it. See [DCO](DCO) and
  [CONTRIBUTING](CONTRIBUTING.md).
- **No blanket copyright assignment or contributor licence agreement
  (CLA) is required** for ordinary open-source contributions.
- The association may review a separate, explicit written rights
  assignment for a specific contribution if legally needed; such a
  transfer cannot be inferred from a GitHub PR, fork, DCO sign-off,
  commit or project membership.
- Do not import third-party code, datasets, documentation or model
  artefacts without licensing and attribution review. Keep upstream
  notices, permitted modifications and provenance recorded. Scientific
  ideas and scholarly attribution are distinct from copyright ownership.
- No contributor can relicense the entire project, promise an exclusive
  right over others' contributions or change its licensing policy in
  a feature PR.

Apache-2.0 permits use, modification and redistribution, including
commercial uses, subject to its terms. It does **not** grant trademark
rights. The association manages the name and official public
representations of the project; no third-party trademark ownership
claim is implied.

## Decision authority

1. **Normative science:** `tllib-specs` is authoritative for science,
   mathematics, contracts and acceptances. A tllib maintainer cannot
   invent or modify scientific obligations locally.
2. **Software architecture:** versioned ADRs and adopted `docs/v1/`
   policies govern the implementation. Substantial changes require
   targeted issues, rationale, compatibility analysis and review.
3. **Implementation:** contributors own their focused PRs and must
   supply reproducible evidence. Maintainers review scope,
   correctness, licensing, safety and conformance.
4. **Maintainers and releases:** persons explicitly delegated by the
   association through repository permissions approve integrations
   and releases. A GitHub collaborator is not automatically a legal
   representative of the association.

A proposed policy change is discussed in an issue and reviewed via a
PR. Before merging code, reviewers check that its issue is ready,
scientific obligations are unambiguous, and mandatory controls actually
pass. Avoid approving one's own changes; protect `main` with review
requirements when repository settings allow. Conflict of interest and
security concerns must be escalated to an independent maintainer.

## Scope and readiness

The project is in **pre-implementation V1**. The 36 domain epics and
178 TLC-FC lots are not automatically ready. Follow
[the readiness policy](docs/v1/READINESS-AND-GOVERNANCE.md).
A scientific ambiguity blocks only the affected behavior, not the
whole library. Work on the native core, bindings, packaging or
numerical backends begins only under the corresponding accepted ADR
and issue, not as an unreviewed domain-level assumption.

## Security, release and organizational changes

Use [SECURITY.md](SECURITY.md) for sensitive findings. A release must
publish its tllib commit, authoritative tllib-specs snapshot, actual
supported platforms and licence notices. If the association's formal
name, representatives or governance changes, update public documents
with an authorized, reviewed change; past copyright attribution and
authorship must be preserved.

This is project policy, not a substitute for individualized legal
advice or a statutory determination of intellectual-property title.
