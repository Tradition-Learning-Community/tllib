# ADR-004 — Bindings Python : choix de nanobind après spike #256

**Statut : accepté pour les nouvelles surfaces natives, 30 octobre 2026.**

## Contexte et frontières

C++20 reste le runtime scientifique de référence. Le pont provider
`tllib._native` est une adaptation CPython native déjà implémentée
et testée : **il est conservé** pour les providers. Pour les **futures
surfaces de binding** (value objects, enums, tableaux, résultats),
**nanobind est le binder de référence**. Cela évite que chaque domaine
choisisse son binder. Les APIs scientifiques des 36 domaines ne sont pas
implémentées par cette décision.

Le spike technique, dans `spikes/binders`, compile et teste avec les deux
candidats la même surface : C++ `FeatureId` (incluant `Result` et échec
stable), classe valeur, enum, NumPy `float64` contiguous en prêt
d'adresse sans conversion implicite, callback Python recevant bytes.
Il ne simule ni provider scientifique ni contrat TLC-FC.

## Mesures observées (GitHub Actions PR #276)

Workflow `Binder comparison spike`, Linux GitHub Actions Ubuntu,
CPython **3.12**, `nanobind==2.15.0`, `pybind11==3.1.0`,
`numpy==2.5.4`, build CMake Release, deux cibles compilées séparément.
**Un seul essai** : ces nombres sont des observations locales, pas
des garanties de vitesse ni des benchmarks multi-plateformes.

| Mesure | nanobind | pybind11 |
|---|---:|---:|
| Compilation du module, secondes (une exécution) | 12.920 | 6.603 |
| Taille du module, octets | 140096 | 266392 |
| Appel de parsing/Result, ns en moyenne (20000 itérations) | 274.8 | 415.9 |
| Inspection NumPy, ns en moyenne (20000 itérations) | 293.2 | 476.1 |
| Callback, ns en moyenne (10000 itérations) | 403.9 | 410.7 |
| RSS maximum de processus Python, KiB | 35624 | 35900 |

Les deux binders ont passé les mêmes tests de types, enums, exceptions,
callbacks, adresses NumPy sans copie et rejet des conversions incompatibles.
Les différences de mémoire à cette échelle ne fondent aucune conclusion.

## Décision

1. **nanobind** pour les nouveaux bindings C++/Python non scientifiques
   ou pour les futurs modules des domaines, en raison de la surface
   valide, du faible volume des extensions observé et de la simplicité
   des primitives de propriété. La compile plus lente constatée est
   acceptée et devra être surveillée. Aucun chiffre isolé n'est une
   promesse de performance pour les futurs workloads scientifiques.
2. **CPython native API conservée** exclusivement pour le bridge provider
   actuel et la couche transversale de buffers : sa suppression
   exigerait une non-régression provider, cancellation, GIL et lifetime
   que le spike ne constitue pas. Ne pas mélanger nanobind et CPython
   provider dans un même module sans gate d'intégration explicite.
3. **pybind11** comparateur validé et solution de réévaluation si
   portabilité, maintenabilité, stabilité ABI ou contraintes de wheel
   révèlent un problème documenté avec nanobind.
4. Stubs typés et `py.typed` restent une exigence de la façade, vérifiée
   par #258. Aucune génération de stubs non validée n'est automatique.

## Limitations et réévaluation

Validation mesurée sur **Linux/CPython 3.12 uniquement**. Ni Windows,
ni macOS, ni free-threaded, ni abi3, ni sous-interpréteurs ne sont
qualifiés. Phase B (#243, #249, #260) les traitera avec tests
spécifiques. Reconsidérer le choix seulement sur anomalie concrète de
lifetime, coût maintenance, extension excessive, incompatibilité Python,
ou mesures contradictoires représentatives, et documenter une nouvelle
ADR. Les versions du spike sont épinglées et les résultats machine
sont exposés comme artefacts du workflow ; les mesures ci-dessus
correspondent au premier passage validé, avant cet épinglage.
