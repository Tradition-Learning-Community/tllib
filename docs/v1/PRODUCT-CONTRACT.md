# tllib V1 — Contrat produit

## Autorité et périmètre

`tllib-specs` est l'autorité scientifique, mathématique et normative.
`tllib` est l'implémentation logicielle de référence de Tradition Learning.

V1 n'est pas un MVP partiel. V1 cible un snapshot certifié complet de
`tllib-specs` et doit couvrir l'intégralité de sa population publiée.

## Architecture produit

- runtime de référence principalement en C++20 ;
- API C++ publique ;
- API Python de première classe construite sur le même runtime natif ;
- Python autorisé pour tooling, conformité, génération, tests et prototypage ;
- aucune seconde implémentation normative indépendante en Python ;
- aucun accès runtime aux sources internes de `tllib-specs` ;
- aucune sémantique scientifique inventée dans `tllib`.

## Principe de réutilisation

`tllib` ne réimplémente pas les briques générales matures sans nécessité propre
à Tradition Learning. NumPy, DLPack, BLAS/LAPACK, outils de build, tests,
visualisation et packaging sont utilisés ou encapsulés lorsque cela réduit la
dette sans céder l'autorité scientifique/runtime de TL.

## Fin de V1

V1 est publiable seulement lorsque le même commit `tllib` et le même snapshot
`tllib-specs` satisfont simultanément :

- 100 % des domaines/features du catalogue qualifiés ;
- fonctionnalités exécutables implémentées et conformes ;
- fonctionnalités conditionnelles reliées à des providers explicites ;
- fonctionnalités structurelles/unresolved représentées sans fausse exécution ;
- API C++ et Python installables, documentées et testées ;
- CI, sécurité, performance, packaging et release gate verts.

Les versions suivantes étendent ou améliorent le produit ; elles ne remplacent
pas les fondations architecturales de V1.
