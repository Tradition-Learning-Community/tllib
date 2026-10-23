# V1 — Build et politique de dépendances

Références : #247, #246, #248, #249, #253, ADR-002.
**Contrat de conception**, pas preuve que le squelette CMake existe.

## Choix verrouillés pour l'implémentation

- C++20 strict (`CMAKE_CXX_STANDARD 20`, requis, extensions désactivées).
- CMake >= 3.27 (minimum cible à vérifier sur toutes les plateformes) ;
  presets versionnés ; Ninja préféré mais générateurs natifs possibles.
- Targets CMake namespacés à l'installation (`tllib::...`) ;
  `BUILD_INTERFACE` / `INSTALL_INTERFACE` distincts ; headers privés
  non exportés. Aucun import de Python pour construire le cœur C++.
- Le nombre de bibliothèques/targets est dicté par de **vraies**
  frontières de dépendances ; ne pas créer de DLL inutile par domaine.
- Defaults de build : aucun téléchargement réseau implicite ;
  build offline possible à partir d'archives/dépendances préinstallées
  explicitement décrites. Build reproductible sous environnement gelé.
- Les définitions `-Werror` et équivalents s'appliquent à nos cibles
  selon preset, jamais à des bibliothèques tierces.
- Éviter macros et includes propriétaires dans les headers publics ;
  install + projet externe `find_package(tllib CONFIG REQUIRED)`
  obligatoire pour clôturer #248.

## Hiérarchie de résolution

1. standard C++ / code TL minimal quand suffisant ;
2. package natif existant via `find_package` ou config target ;
3. dépendance verrouillée et vendue seulement avec justification et
   validation licence/supply chain ;
4. Conan ou vcpkg seulement si une matrice de dépendances réelles démontre
   qu'ils simplifient le graphe ; pas de mélange non maîtrisé ;
5. `FetchContent` **opt-in pour développement**, jamais fetch surprise
   dans un build offline ou release.

Chaque ajout de dépendance nécessite une fiche : TLC-FC/contrat ou besoin
ingénierie, fonction, propriétaire, version et empreinte, licence
(SPDX + obligations), origine, CVE/procédure de mise à jour,
dépendances transitives, statut runtime/optionnel/build/test, tailles,
portabilité et plan de retrait. Une dépendance non retenue ne doit pas
apparaître en API publique.

## Ce qu'on ne décide pas arbitrairement

Ne pas préinstaller Eigen, BLAS, LAPACK, FFT, GPU, sparse ou un framework
de graphes dans le cœur **avant l'inventaire #250 et l'arbitrage #253**.
Il n'existe pas de backend numérique par défaut garanti s'il n'est
pas requis par le catalogue. Un provider optionnel n'est jamais appelé
implicitement.

## Qualité locale visée

`cmake --preset <dev>`, `cmake --build --preset <dev>`,
`ctest --preset <dev> --output-on-failure` une fois les presets livrés.
GoogleTest ou alternative éprouvée uniquement quand un vrai test existe ;
clang-format et clang-tidy configurables sur nos fichiers ;
GCC/Clang/MSVC warnings cohérents ; sanitizers sous presets dédiés.
Ne pas marquer #246, #248 ou #249 terminés tant que les commandes
et le test externe ne sont pas effectivement passés.
