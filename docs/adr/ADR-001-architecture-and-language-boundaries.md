# ADR-001 — Architecture et frontières de langage

**Statut : accepté.**

- C++20 est le runtime de référence.
- Python est une API de première classe et sert aussi au tooling/conformance/prototypes.
- Il n'existe pas deux moteurs normatifs C++/Python.
- `tllib-specs` est une dépendance de conception/build-time par snapshot, pas runtime.
- tout autre langage futur passe par une frontière dédiée, pas une nouvelle implémentation TL.
