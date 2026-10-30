# ADR-008 — CI, tests, performance et release

**Statut : politique progressive appliquée aux fondations Linux ; release V1 non qualifiée.**

- Les fondations C++20 et Python ont des cibles réelles : CTest, consommateur externe,
  wheel CPython 3.12, providers, parité et conformité du snapshot verrouillé.
- PR fast : chemins impactés, Ruff et formatage à portée des modifications,
  analyse statique clang-tidy ; documentation seule ne compile pas.
- PR native : tests C++20, consommateur externe, CPython provider et ASan/UBSan.
- Main : même périmètre représentatif Linux ; matrice de support vérifiée
  dans `PLATFORMS-2027.md`. Autres systèmes et Python non qualifiés.
- Nightly : futur uniquement si tests/charges réels justifiés.
- Release : conformance complète, artefacts et smoke tests réellement
  installés sur la matrice promise.
- Filtres par workflow/chemin et tests de portée docs-only / C++ ;
  changement core déclenche le consommateur, les bindings et la wheel.
  Les workflows eux-mêmes sont inclus dans leurs propres path filters.
  Les actions GitHub sont référencées par SHA complet ; tokens read-only,
  sans credentials persistants. Aucun cache ne prouve la correction.
- Voir `docs/v1/SECURITY-QUALITY-COMPATIBILITY.md` et #243.
