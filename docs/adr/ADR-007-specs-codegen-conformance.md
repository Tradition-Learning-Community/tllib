# ADR-007 — Snapshot specs, specgen et conformité

**Statut : accepté.**

- chaque release tllib cible un SHA immuable de tllib-specs.
- specgen lit uniquement le handoff publié.
- codegen limité aux structures/métadonnées déterministes.
- generated artifacts utiles au build portent leur provenance.
- CI régénère et exige zéro diff.
- conformance couvre 100 % du catalogue.
- nouvel ID = gap jusqu'à décision explicite.
- ambiguïté scientifique = blocker amont, jamais invention locale.
