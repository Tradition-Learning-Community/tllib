# ADR-004 — Bindings et API Python

**Statut : direction acceptée ; binding final après spike.**

- package Python construit sur le runtime C++.
- scikit-build-core pilote CMake.
- nanobind vs pybind11 est décidé par un spike réel.
- Python est une API de première classe mais ne duplique pas la logique runtime.
- typing/stubs et documentation font partie de la surface publique.
- stable ABI/free-threading sont évalués, pas supposés.
