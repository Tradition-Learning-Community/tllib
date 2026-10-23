# V1 — Politique de support plateformes (cible 2027)

Statut : **matrice cible à valider par builds natifs et wheels** ; elle ne
constitue pas une déclaration de support déjà testé. Références :
#260, #246, #243, #11, #14, ADR-002, ADR-008 et ADR-009.

## Cible par niveau

| Niveau | Plateforme / architecture | Outil principal | Artefact |
| --- | --- | --- | --- |
| Tier 1 visé | Linux glibc x86-64 | GCC 13+ et Clang 17+ | bibliothèque C++ + wheels |
| Tier 1 visé | Windows x86-64 | MSVC VS 2022 17.8+ (19.38+) | bibliothèque C++ + wheels |
| Tier 1 visé | macOS arm64 | AppleClang 15+ | bibliothèque C++ + wheels |
| Tier 2 candidat | Linux aarch64 | GCC 13+ / Clang 17+ | build et wheels si validés |
| Tier 2 candidat | macOS x86-64 | AppleClang 15+ | build si support runner disponible |
| Expérimental | Windows arm64, musl, GPU et autres CPU | sélection explicite | aucune promesse |

Les minima sont des **bornes de conception proposées**. Chaque triplet
plateforme/compilateur/architecture n'obtient Tier 1 qu'après passage de
tests C++ installés, conformité, sécurité applicable et installation réelle
du package Python. Ne pas déduire un support d'un simple `configure`.
Aucune hypothèse d'ABI inter-compilateur C++.

## Python

CPython **3.12, 3.13 et 3.14** : cibles Tier 1 prévues sur les plateformes
Tier 1 lorsque l'écosystème de bindings/roues est effectivement testé.
CPython **3.15** (stable depuis octobre 2026) : **candidat prioritaire**
à qualifier et promouvoir en Tier 1 dès tests du binder, des dépendances
et des roues ; sa disponibilité en amont n'est pas une preuve de support.
3.11 : aucune promesse initiale de roues V1, car fin de vie prévue
octobre 2027. Python 3.10 et versions antérieures : hors support V1.

CPython free-threaded (3.13t et ultérieurs) : **expérimental**, désactivé
en release normale jusqu'à tests de concurrence, callbacks et ownership.
`abi3` et `abi3t` : fonctionnalités optionnelles à évaluer, jamais
promesses implicites. PyPy et autres implémentations : non supportées V1.

## Révision et sortie du support

- Pas de versions EOL dans la matrice de release sans exception datée,
  motivée et publiée.
- Une nouvelle version Python est évaluée dès sa release stable, puis
  explicitement ajoutée seulement après les tests ; ne pas annoncer
  automatiquement le support.
- Chaque retrait de plateforme, d'architecture ou de version Python
  suit #14 : dépréciation/migration et note de release.
- CI PR : une petite combinaison représentative ; branche principale :
  couverture Tier 1 proportionnée ; release : **tous** les artefacts promis.
- Les runners CI, versions des toolchains et image de base sont enregistrés
  dans les preuves de release et les attestions ; versions verrouillées
  à la granularité réellement nécessaire.

Sources de veille : https://devguide.python.org/versions/ ,
https://peps.python.org/pep-0790/ ,
https://gcc.gnu.org/projects/cxx-status.html .
