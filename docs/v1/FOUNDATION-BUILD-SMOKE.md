# Première fondation C++20 — vérification locale

Périmètre **historique de la PR #266** : premier socle de build uniquement, sans exécution scientifique, API native de domaine ni wheel à cette date. **Depuis les PR #270–#278, les fondations C++/providers et une wheel CPython 3.12 locale existent et sont CI-testées sur Linux** ; consulter [les commandes actuelles](CONTRIBUTOR-QUICKSTART.md) plutôt que supposer leur absence.

```sh
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
cmake --install build/dev --prefix /tmp/tllib-prefix
cmake -S tests/consumer -B build/consumer -DCMAKE_PREFIX_PATH=/tmp/tllib-prefix
cmake --build build/consumer
```

Vérification de préparation sur Linux/GCC 14.2.0, CMake 3.31.6 et Ninja 1.12.1 : configuration, compilation, **1/1 CTest réussi**, installation puis build/exécution d'un consommateur `find_package(tllib CONFIG REQUIRED)` réussis. Ces essais locaux ne prouvent pas encore la matrice Windows/macOS, l'API scientifique, le packaging Python, la qualité des fonctions futures, ni une CI complète.

`tllib::core` reste une cible C++20 INTERFACE, mais expose désormais les primitives natives de #235 et les huit porteurs structurels de #237, avec tests dédiés. Voir [SHARED-CXX20-FOUNDATION.md](SHARED-CXX20-FOUNDATION.md) pour les commandes actuelles, la traçabilité normative et les limites de conformité. La version de package de ce compte rendu était **provisoire** (`0.0.0` au moment de #266 ; `0.1.0` depuis la phase A) et ne sont pas une release. Il ne faut ni afficher ces commandes comme preuve de conformité scientifique ni fermer #248 tant que son gate de compatibilité/version est confirmé.
