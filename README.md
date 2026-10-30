# tllib

**tllib** est la bibliothèque logicielle scientifique open source de **Tradition Learning**, portée, maintenue et gouvernée par **Tradition Learning Community ASBL**.

**Licence : [Apache-2.0](LICENSE)** · **[Gouvernance](GOVERNANCE.md)** · **[Contributions](CONTRIBUTING.md)** · **[DCO](DCO)** · **[Sécurité](SECURITY.md)**

> **État actuel : fondations techniques de préparation V1.**
>
> Le runtime structurel C++20, les providers et l'API Python commune existent.
> Les packages CMake et wheel locale sont vérifiés sur Linux.
> **Les algorithmes des 36 domaines TLC-FC ne sont pas encore implémentés.**

## Projet communautaire

Les scientifiques, mathématiciens, ingénieurs et développeurs peuvent contribuer sous les règles de [CONTRIBUTING.md](CONTRIBUTING.md). L'ASBL administre le projet et coordonne les versions ; chaque auteur conserve les droits sur sa contribution sauf cession écrite distincte. Le dépôt est sous Apache-2.0, qui ne transfère pas automatiquement le copyright des contributeurs. Voir [NOTICE](NOTICE) et [GOVERNANCE.md](GOVERNANCE.md). Aucun CLA ni transfert général de droits n'est exigé ; les contributions utilisent le [DCO 1.1](DCO).

## Autorité des dépôts

- **tllib-specs** : science, mathématiques, contrats, acceptations, statuts,
  traçabilité et publication normative.
- **tllib** : architecture, runtime, API C++/Python, conformité, packaging,
  documentation et release.

Une ambiguïté scientifique découverte pendant l'implémentation est bloquée et
renvoyée vers `tllib-specs`. `tllib` ne complète jamais une spécification par
invention locale.

## Architecture V1

Les documents autoritaires sur l'architecture déjà acceptée sont :
- `docs/v1/ARCHITECTURE.md` et `docs/v1/PRODUCT-CONTRACT.md` ;
- `docs/adr/`.

Les politiques de préparation **proposées à l'adoption**, qui ne prétendent
pas avoir livré les tests/builds requis, sont :
- [État et preuves des préparations](docs/v1/PREPARATION-STATUS.md) ;
- [Gouvernance et statut ready](docs/v1/READINESS-AND-GOVERNANCE.md) ;
- [Matrice plateformes cible 2027](docs/v1/PLATFORMS-2027.md) ;
- [Dépendances, build, export CMake](docs/v1/DEPENDENCIES-BUILD-POLICY.md) ;
- [Arrays, calcul et exactitude numérique](docs/v1/ARRAYS-NUMERICS-CONTRACT.md) ;
- [Concurrence, bindings et Python](docs/v1/CONCURRENCY-PYTHON-API.md) ;
- [Snapshot, lock et conformité](docs/v1/SPECS-LOCK-AND-CONFORMANCE.md) ;
- [Sécurité, qualité et compatibilité](docs/v1/SECURITY-QUALITY-COMPATIBILITY.md).

Principes principaux :
- runtime de référence en C++20 ;
- API C++ publique ;
- API Python de première classe sur le même runtime ;
- Python pour tooling, génération, conformité, tests et prototypes ;
- pas de second moteur scientifique Python concurrent ;
- réutilisation des briques matures (NumPy, DLPack, BLAS/LAPACK lorsque
  **justifiés par des besoins prouvés**) ;
- V1 couvre le snapshot complet de `tllib-specs`, pas une release par domaine.

## Backlog V1

Epic principal : #52. Fondations : #234 à #244.
Les 36 issues domaine et leurs 178 lots TLC-FC restent les unités de réalisation.
Les issues préparatoires ne sont pas terminées par une simple décision
documentaire ; leur clôture est conditionnée à leurs propres preuves.
Voir [plan du backlog](docs/v1/ISSUE-PLAN.md).

## Fondations techniques disponibles

Le squelette C++20/CTest et l'export CMake ont été livrés depuis la PR #266 ;
les contrats structurels, le runtime providers, le pont CPython, les données
natives CPU, les wheels Python, le spike des binders et les tests de parité
structurelle ont ensuite été ajoutés (PR #270–#277).
Voir [la documentation du build](docs/v1/FOUNDATION-BUILD-SMOKE.md),
[ADR-004](docs/adr/ADR-004-python-bindings.md) et
[le packaging Python](docs/v1/PYTHON-WHEEL-PACKAGING.md).

Ce sont des **fondations préparatoires** et non des implémentations scientifiques.
