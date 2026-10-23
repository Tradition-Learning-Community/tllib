# ADR-004 — Bindings et API Python

**Statut : direction acceptée ; binder final bloqué par des preuves.**

- Package Python construit sur runtime C++ via scikit-build-core/CMake.
- API Python de première classe, typée et documentée, sans moteur
  scientifique normatif indépendant.
- **nanobind est le candidat de référence pour le spike #256 ;
  pybind11 est le comparateur obligatoire.** Ce n'est pas une adoption.
- Le spike compare mini-surface identique : value types, Result/Error,
  ArrayView/NumPy, ownership, callbacks/providers, stubs, latences
  d'appel, taille et temps de build et installations multi-plateformes.
- Le choix final exige résultats reproductibles et tests de lifetime ;
  ne pas décider sur marketing ou benchmark tiers.
- CPython free-threaded et stable ABI/abi3t sont expérimentaux
  jusqu'à validation spécifique, pas des promesses implicites.
- Voir `docs/v1/CONCURRENCY-PYTHON-API.md`,
  `docs/v1/PLATFORMS-2027.md` et issues #256–#258.
