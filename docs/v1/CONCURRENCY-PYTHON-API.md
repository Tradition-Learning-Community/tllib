# V1 — Concurrence, providers, API Python et binder

Références : #259, #238, #239, #256, #257, #258, #242.

## Concurrence C++

- Value objects immuables : lectures concurrentes autorisées après
  construction, sous réserve de contenu non mutable en profondeur.
- Objets mutables : **pas** de partage concurrent par défaut ;
  l'API publie explicitement les opérations synchronisées et les
  restrictions de réentrance ; pas de promesse générale de thread safety.
- Un même objet runtime ne peut être utilisé sur plusieurs threads qu'après
  preuve et déclaration explicites des opérations autorisées.
- Aucun pool global caché, aucune dépendance à l'ordre du scheduling,
  aucun `thread_local` sémantique non tracé, aucun singleton mutable
  scientifique. Un executor optionnel est passé par l'appelant.
- `ExecutionContext` inclut, selon besoin, un token de cancellation
  coopérative, un executor explicite, des options et des capabilities
  liées à l'appel ; ne pas exposer des champs non nécessaires.
- Cancellation : chaque opération déclare ses **points sûrs** et sa
  stratégie de mutation. Si elle promet l'atomicité, annuler implique
  rollback complet ou absence de commit visible. Si elle **n'est pas
  atomique**, elle doit exposer de manière stable les effets effectivement
  validés (identités/étapes/état observable) et un protocole de reprise
  ou de réconciliation permettant d'éviter les duplications au retry.
  Un simple `cancelled` silencieux après effets partiels est interdit.
  Lorsque l'état des effets externes ne peut être connu, signaler
  explicitement un résultat `outcome_indeterminate` / état à réconcilier,
  et interdire le retry aveugle ; ne pas inventer un résultat scientifique.
  S'il est impossible d'assurer l'une de ces garanties, désactiver la
  cancellation pour la section critique et documenter le comportement.
  Les erreurs de cancellation restent distinctes de validation/timeout
  et préservent provenance, feature ID et conséquences observables.
- Les callbacks providers ne sont invoqués ni en tenant des verrous
  internes arbitraires ni après expiration de leurs owners ; les contrats
  précisent synchronie, réentrance, erreurs et responsabilités.
- Réduction parallèle seulement si déterminisme/ordre/tolérances du
  contrat restent préservés et si mesures démontrent le bénéfice.
- C++ pur ne dépend pas du GIL ; bindings Python traduisent correctement
  GIL, callbacks et temps de vie. GIL relâché uniquement autour de code
  natif qui ne touche aucun objet Python et qui est sûr en concurrence.

## Python public

Noms Python `snake_case`, classes `PascalCase`, constantes `UPPER_SNAKE_CASE`.
`tllib` expose le même statut, les mêmes identifiants et les mêmes
obligations observables que C++ ; un helper Python ne peut apporter
de calcul normatif manquant. Stubs `.pyi` ou annotation runtime vérifiées
et marqueur `py.typed`, docstrings, sémantique d'ownership explicite.
Les erreurs attendues C++ sont traduites en exceptions Python typées
avec code, feature ID et provenance préservés ; ne pas masquer
`unresolved` ou `provider_required`.

Parité : même bundle verrouillé, même cas d'acceptation, sorties conformes
aux mêmes invariants (et pas nécessairement même disposition mémoire),
erreurs/limites et formes validées. Les conversions Python/C++ ne
doivent pas dégrader silencieusement des valeurs.

## Choix du binder : décision exécutée sur spike (#256)

**nanobind est candidat de référence** à soumettre au spike #256 ;
**pybind11 est le comparateur obligatoire**. Le verdict final exige
un prototype à surface identique : value object, `Result/Error`,
arrays/strides/lifetime, callbacks providers, exceptions, typing,
build size/time, import, calls, free-threading et wheels. Résultats
reproductibles sur les plateformes promises ; corriger les bugs de
lifetime avant toute décision. Le choix est documenté dans ADR-004.
Aucun faux benchmark ni adoption définitive sans ce test.

`scikit-build-core` pilote CMake pour les wheels natives depuis la PR #275. Un consommateur C++ ne doit jamais importer Python.
Ne pas annoncer free-threaded ni stable ABI (abi3/abi3t) avant essais
spécifiques sur CPython et au minimum tests TSan ou équivalents pertinents.

Référence technique nanobind :
https://nanobind.readthedocs.io/en/latest/free_threaded.html .
