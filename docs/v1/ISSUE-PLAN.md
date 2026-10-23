# Plan V1 — groupes de travail autonomes

## Epic autoritaire

- #52 — V1 complète : runtime C++20 + API Python + conformité au snapshot entier.

## Architecture et gouvernance

- #233 — architecture V1 et ADR.
- #234 — reset du dépôt sur la structure native C++20 + Python.

## Fondations techniques

- #235 — primitives/API C++ fondamentales.
- #236 — mémoire, ArrayView, numérique et zéro-copie.
- #237 — 8 contrats structurels partagés en C++.
- #238 — runtime registry, dispatcher et ExecutionContext.
- #239 — providers natifs et adaptation Python.
- #240 — specs.lock, vérification et specgen.
- #241 — conformité catalogue-complet et coverage.
- #242 — bindings/API Python.
- #243 — CI progressive et impact-aware.
- #244 — diff/synchronisation des snapshots tllib-specs.

## Travaux transversaux

- #10 — documentation C++/Python/domaines.
- #11 — packaging/release natif + Python.
- #12 — performance native + coût bindings.
- #13 — sécurité runtime/specs/providers/supply chain.
- #14 — compatibilité SemVer/API/ABI/Python/specs.
- #51 — parcours contributeurs C++, Python, tooling, docs et conformité.

## 36 domaines

Les issues #15–#50 restent les epics de domaine autoritaires.

Chaque domaine :
- découvre sa population dynamiquement depuis le catalogue du snapshot verrouillé ;
- couvre 100 % de ses TLC-FC ;
- utilise les fondations communes ;
- ne crée aucune architecture locale provisoire.

Aucun domaine n'est une mini-release. Les 36 convergent vers la même V1.

## Lots TLC-FC

Les 178 issues #53–#230 restent les unités de contribution autonomes.

Elles ont été migrées vers un contrat V1 commun :
- IDs résolus depuis les catalogues du snapshot certifié ;
- executable -> implémentation C++ de référence ;
- conditionally_executable -> provider commun #239 ;
- structural_only/unresolved -> représentation fidèle sans fausse exécution ;
- conformance #241 ;
- binding/parité Python #242 lorsque applicable.

Le découpage des lots est conservé ; les anciennes recettes Python-first ne sont plus autoritaires.

## Blockers normatifs

- #231 — blocker runtime pour TLC-FC-30-EXPANSION-014.
- la décision normative autoritaire vit dans tllib-specs#231.

Toute ambiguïté future suit le même modèle : issue normative dans tllib-specs, blocker ciblé dans tllib.

## V1 Release Gate

La release est autorisée seulement si #52 et docs/v1/DEFINITION-OF-DONE.md sont satisfaits sur le même commit tllib et le même snapshot tllib-specs :
- catalogue complet ;
- executable gate ;
- conditional/provider gate ;
- structural/unresolved gate ;
- API C++ gate ;
- API Python/parity gate ;
- security/performance gate ;
- packaging/release reproductible.
