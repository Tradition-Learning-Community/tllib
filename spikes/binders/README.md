# Phase A — Spike comparatif des binders (#256)

Deux modules **isolés et non distribués** exportent la même surface C++20 :
value object, enum, parsing de `FeatureId` via `Result` avec exception,
`float64` NumPy contiguous sans conversion implicite et callback opaque.
Les callbacks sont de simples tests de port ; les providers réels restent
testés dans le pont CPython déjà en place.

L'intégration CMake, le temps de compilation, la taille des modules,
le temps d'appel et la mémoire RSS sont mesurés en CI Linux / CPython 3.12,
dans un environnement à versions journalisées. **Un seul essai** par cas,
donc les différences ne sont pas des garanties de performance ou de
portabilité. Les sorties JSON sont attachées au workflow
`Binder comparison spike`.

Ce dossier ne change ni les fonctions scientifiques ni les statuts
d'exécution. L'ADR-004 sera finalisé **après** observation des mesures
et succès des deux implémentations sur la même surface.
