# ADR-002 — Toolchain, build et dépendances

**Statut : accepté pour la fondation V1.**

- C++20.
- CMake + CMakePresets.
- Ninja lorsque disponible.
- GCC, Clang, MSVC ; AppleClang pour macOS.
- GoogleTest et Google Benchmark.
- clang-format + clang-tidy + warnings stricts.
- sccache lorsque sûr.
- dépendances runtime minimales et justifiées.
- Conan/vcpkg seulement si le graphe réel le justifie.
