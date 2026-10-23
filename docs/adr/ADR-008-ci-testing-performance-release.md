# ADR-008 — CI, tests, performance et release

**Statut : politique progressive acceptée ; pipelines à livrer selon besoins.**

- Pré-implémentation : ne pas créer de CI native factice.
- PR fast : tests réellement impactés, documentation sans compilation ;
  PR native : toolchain et sanitizers ciblés lorsque code présent.
- Main : matrice Tier 1 publiée ; nightly : fuzz, performances,
  matrices plus larges lorsque les cibles existent.
- Release : conformance complète, artefacts et smoke tests réellement
  installés sur la matrice promise.
- Path filters + graphe d'impact conservateur ; changement core
  déclenche consommateurs ; pas de matrice cartésienne par commit.
- Voir `docs/v1/SECURITY-QUALITY-COMPATIBILITY.md` et #243.
