# ADR-008 — CI, tests, performance et release

**Statut : accepté.**

- PR fast : build/tests impactés.
- PR native : toolchain/sanitizer ciblés.
- main : plateformes principales.
- nightly : matrices larges, fuzz, full conformance, benchmarks.
- release : artefacts complets + smoke tests installés.
- path filters + graph d'impact.
- pas de matrice cartésienne complète à chaque commit.
- release gate sur le catalogue complet.
