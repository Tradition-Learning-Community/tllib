# Première fondation C++20 — vérification locale

Périmètre : **socle de build uniquement**, aucune exécution scientifique, aucune API native de domaine et aucune wheel.

```sh
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
cmake --install build/dev --prefix /tmp/tllib-prefix
cmake -S tests/consumer -B build/consumer -DCMAKE_PREFIX_PATH=/tmp/tllib-prefix
cmake --build build/consumer
```

Vérification de préparation sur Linux/GCC 14.2.0, CMake 3.31.6 et Ninja 1.12.1 : configuration, compilation, **1/1 CTest réussi**, installation puis build/exécution d'un consommateur `find_package(tllib CONFIG REQUIRED)` réussis. Ces essais locaux ne prouvent pas encore la matrice Windows/macOS, l'API scientifique, le packaging Python, la qualité des fonctions futures, ni une CI complète.

`tllib::core` est actuellement une cible INTERFACE intentionnellement minimale : la surface publique est limitée à un marqueur de statut pré-implémentation ; de vrais objets C++ seront ajoutés par #235, avec tests dédiés. Les versions de package sont **provisoires** (`0.0.0` pour build interne) et ne sont pas une release. Il ne faut ni afficher ces commandes comme preuve de conformité scientifique ni fermer #248 tant que son gate de compatibilité/version est confirmé.
