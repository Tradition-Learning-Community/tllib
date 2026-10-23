# Plan V1 — groupes de travail autonomes

## EPIC 0 — Architecture et gouvernance
- A0.1 Adopter contrat produit + ADR.
- A0.2 Migrer le backlog sans doublons.
- A0.3 Réinitialiser l'arbre de tllib après validation des ADR.

## EPIC 1 — Toolchain et build natif
- A1.1 CMake + presets + C++20.
- A1.2 Politique de dépendances.
- A1.3 Installation/export C++.
- A1.4 clang-format/clang-tidy/warnings.

## EPIC 2 — Primitives fondamentales
- A2.1 FeatureId/DomainId/versions/fingerprints.
- A2.2 statuts scientifique/exécution.
- A2.3 Error + Result.
- A2.4 sérialisation canonique.

## EPIC 3 — Mémoire, arrays et numérique
- A3.1 inventaire des besoins des 36 domaines.
- A3.2 ArrayView/dtype/shape/strides/device.
- A3.3 ownership outputs/buffers.
- A3.4 sélection de backends numériques.
- A3.5 interop NumPy zero-copy.
- A3.6 DLPack.

## EPIC 4 — Runtime, shared contracts et providers
- A4.1 8 shared contracts C++.
- A4.2 runtime feature registry.
- A4.3 dispatcher.
- A4.4 ExecutionContext.
- A4.5 provider interface + registry.
- A4.6 provider adapter Python.

## EPIC 5 — Specs, codegen et conformité
- A5.1 specs.lock V1.
- A5.2 verifier de snapshot.
- A5.3 specgen déterministe.
- A5.4 generated artifact policy.
- A5.5 loader/conformance model.
- A5.6 coverage report complet.
- A5.7 diff/migration de snapshots.

## EPIC 6 — Bindings et API Python
- A6.1 spike nanobind vs pybind11.
- A6.2 skeleton package Python.
- A6.3 mapping primitives C++ -> Python.
- A6.4 design API Python.
- A6.5 typing/stubs.
- A6.6 parity harness.

## EPIC 7 — Sécurité, qualité et performance
- A7.1 threat model.
- A7.2 ASan/UBSan ; TSan si pertinent.
- A7.3 fuzzing.
- A7.4 benchmark harness.
- A7.5 performance budgets fondés sur mesures.
- A7.6 dépendances/SBOM/licences.

## EPIC 8 — CI/CD impact-aware
- A8.1 graph d'impact fichiers -> targets -> TLC-FC.
- A8.2 PR Fast.
- A8.3 PR Native.
- A8.4 main validation.
- A8.5 nightly.
- A8.6 sccache/caches sûrs.
- A8.7 release workflow.

## EPIC 9 — Packaging et compatibilité
- A9.1 SemVer + compatibilité specs/runtime.
- A9.2 politique API C++.
- A9.3 ABI/plugin boundary.
- A9.4 compatibilité Python.
- A9.5 wheels multi-plateformes.
- A9.6 artifacts natifs.

## EPIC 10 — Documentation
- A10.1 guide développeur C++.
- A10.2 guide contributeur Python/tooling.
- A10.3 architecture + ADR.
- A10.4 API docs C++.
- A10.5 API docs Python.
- A10.6 matrice de support générée.

## EPIC 11 — 36 domaines

Les 36 epics actuels sont conservés. Chaque domaine couvre toute sa population
du snapshot cible. Les lots TLC-FC existants restent les unités de découpage,
mais sont réalisés selon le nouveau template C++/Python/conformance.

## EPIC 12 — V1 Release Gate
- catalogue complet ;
- executable gate ;
- conditional gate ;
- structural/unresolved gate ;
- C++ API gate ;
- Python API gate ;
- security/performance gate ;
- reproducible release.
