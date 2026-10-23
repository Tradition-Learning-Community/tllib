# Contribuer à tllib

`tllib` est en **phase pré-implémentation V1**. Ne démarrer aucun domaine
sans issue autonome `status:ready` et toutes les dépendances satisfaites.
Les politiques de préparation sont proposées à l'adoption :
[registre](docs/v1/PREPARATION-STATUS.md) et
[gouvernance](docs/v1/READINESS-AND-GOVERNANCE.md).

## Avant toute contribution

1. Lire [le contrat produit](docs/v1/PRODUCT-CONTRACT.md), #52 et les ADR.
2. Vérifier le dépôt autoritaire : science dans `tllib-specs`,
   logiciel et API dans `tllib`.
3. Sélectionner une issue réellement autonome et non bloquée ;
   un epic domaine n'est pas une tâche prête par lui-même.
4. Pour les tâches normatives-consommatrices, utiliser le snapshot
   `tllib-specs` verrouillé et les packages autonomes de `handoff/`.
5. Lire `contract.json`, `acceptance.json`, les contrats partagés ;
   ne jamais inventer formule, valeur, provider ou comportement manquant.

## Parcours

- **C++** : core, données, runtime, providers, domaines, performance ;
  références : [build](docs/v1/DEPENDENCIES-BUILD-POLICY.md),
  [concurrence](docs/v1/CONCURRENCY-PYTHON-API.md).
- **Python/bindings** : API et typing, NumPy/DLPack, erreurs, parité ;
  [contrat Python](docs/v1/CONCURRENCY-PYTHON-API.md).
- **Tooling Python** : snapshot/specgen/conformance/migration ;
  [contrat specs](docs/v1/SPECS-LOCK-AND-CONFORMANCE.md).
- **Documentation, QA et sécurité** : tests, preuves, audit,
  [qualité](docs/v1/SECURITY-QUALITY-COMPATIBILITY.md).
- **Recherche scientifique** : seulement dans `tllib-specs` par
  décision normative revue, pas en modifiant un contrat localement.

## Pull requests

Une PR, une issue autonome. Préciser :
- issue et dépendances ; périmètre exact/TLC-FC ;
- SHA complet du snapshot de specs si applicable ;
- obligations d'acceptation (y compris négatives) et changements ;
- commandes de tests **réellement exécutées**, résultats et limites ;
- analyse ownership, concurrence, précision, compatibilité et sécurité
  selon le changement ;
- preuve de parité C++/Python lorsqu'applicable ;
- blockers scientifiques renvoyés vers `tllib-specs`.

Une PR de domaine ne peut introduire ni politique d'architecture locale,
ni tolérance numérique arbitraire, ni fallback provider, ni moteur
scientifique Python alternatif.

## Exécuter les tests

**Il n'existe actuellement pas encore de configuration native CMake,
de wheels ni de suite CTest exécutables**. Les commandes futures
seront publiées et validées par #246/#249/#257 ; les inventer ici
induirait le contributeur en erreur. Les tests documentaires peuvent
être revus sans démarrer une CI de compilation.
