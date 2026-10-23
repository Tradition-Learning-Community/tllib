# Contribuer à tllib

Le dépôt est actuellement en **phase pré-implémentation V1**.

Ne démarrez pas une implémentation de runtime ou de domaine sans issue V1
autonome et sans dépendances satisfaites.

## Avant toute contribution

1. lire l'epic #52 ;
2. lire les ADR applicables sous `docs/adr/` ;
3. identifier l'issue autoritaire ;
4. vérifier si le sujet est logiciel (`tllib`) ou normatif (`tllib-specs`) ;
5. ne jamais inventer de formule, valeur, provider ou comportement absent des
   spécifications.

## Profils de contribution prévus

- C++ : core, runtime, domaines, performance ;
- Python : bindings, API, interop, providers Python ;
- tooling Python : specgen, conformance, migration, rapports ;
- docs/tests : documentation, fixtures, QA ;
- spécifications : dans `tllib-specs`.

Voir #51 pour le parcours contributeur complet à finaliser avec l'implémentation.

## Pull requests

Une PR doit rester liée à une seule issue autonome et expliquer :

- le problème traité ;
- les contrats/TLC-FC concernés ;
- le snapshot `tllib-specs` utilisé lorsque pertinent ;
- les changements effectués ;
- les validations exécutées ;
- les limites ou blockers normatifs.

## CI

Aucune ancienne CI Python-first n'est considérée autoritaire.

La CI V1 définitive sera mise en place par #243 lorsque la fondation native
existera. Pendant la phase pré-implémentation, la documentation et la
gouvernance ne doivent pas déclencher une matrice de build inutile.
