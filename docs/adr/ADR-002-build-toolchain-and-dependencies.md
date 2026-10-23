# ADR-002 — Toolchain, build et dépendances

**Statut : orientation acceptée ; matrice de support et détails de
résolution proposés à l'adoption et à valider techniquement.**

- C++20 ; CMake + CMakePresets ; Ninja préféré mais facultatif.
- GCC, Clang, MSVC, AppleClang selon la matrice validée en release.
- GoogleTest / Google Benchmark uniquement lors des besoins tests/mesures ;
  clang-format, clang-tidy, warnings stricts propres à nos targets.
- sccache lorsqu'il ne compromet pas la provenance.
- Dépendances runtime minimales et justifiées, offline prévisible.
- Conan/vcpkg seulement si un graphe réel le justifie.
- Aucun BLAS/Eigen/FFT imposé avant inventaire #250 et décision #253.
- Voir `docs/v1/DEPENDENCIES-BUILD-POLICY.md` et
  `docs/v1/PLATFORMS-2027.md`.
