# Phase A — Parité structurelle Python et C++ (#258)

Le runtime C++20 conserve les sources de vérité de `FeatureId`, `DomainId`,
`ExecutionStatus` et `Error`. Le module CPython `tllib._native` valide
ces valeurs en appelant exactement les parseurs C++ existants ; `FeatureId`
et `DomainId` sont des façades Python dataclass frozen, comparables/hashables.
`ExecutionStatus` n'exprime **aucune conformité scientifique nouvelle**.

Le mapping C++ `Result<T>` -> Python valeur ou `TllibError` structuré
est centralisé dans `set_error`. Les catégories Python sont
`ValidationError`, `FeatureUnavailableError`, `ProviderRequiredError`,
`ProviderExecutionError`, `IncompatibleSpecsError`, `CancelledError`,
`IndeterminateOutcomeError`. Le code stable (avec contexte, TLC-FC,
provenance et catégorie) est dérivé de `Error.code` et du
`stable_code` explicite : aucun parsing du texte humain.

`tests/parity/manifest.json` porte les cas techniques, y compris
entrées incorrectes, et référence le snapshot **sans prétendre que ses
features sont exécutables**. `tests/parity/identity_cli.cpp` exécute
les parseurs C++ compilés. `tests/python/test_parity.py` compare pour
chaque cas la représentation canonique native, l'API Python et l'oracle
du manifeste. Le test est exécuté en CTest sur un build Python local et
des tests de façade sont également exercés depuis la wheel propre.

Pour ajouter une future fonction de domaine : ajouter un mapping de
symbole à l'ID TLC-FC, ses acceptations, ses résultats et erreurs réels
dans un manifeste analogue, avec un oracle indépendant approuvé ; ne
jamais copier un algorithme scientifique vers Python pour passer la parité.
Pas de parité scientifique inventée pendant cette phase.
