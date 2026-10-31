# V1 — Registre historique des décisions et preuves attendues

> **ARCHIVE DE PRÉPARATION** : ce registre décrit les critères formulés avant la livraison des phases A et B. Plusieurs issues listées ci-dessous ont été **fermées depuis** avec preuves (PR #270–#282) ; leurs statuts/risques ici ne sont donc **pas l'état GitHub actuel**. Pour l'état vérifié du 31 octobre 2026, utiliser [l'audit de phase C](PHASE-C-AUDIT-2026-10-31.md), [les parcours actuels](CONTRIBUTOR-QUICKSTART.md) et [la gouvernance appliquée](READINESS-AND-GOVERNANCE.md).


Ce tableau distingue **politique proposée** de **livraison vérifiée**.
Une PR documentaire n'accomplit pas les gates de build et de test.
Ne pas fermer les issues autonomes avant la vérification de leurs
critères d'acceptation.

| Issue | Décision / source proposée | Preuve encore requise avant clôture |
| --- | --- | --- |
| #260 | PLATFORM-2027 ; Tier 1/Tier 2 cibles | support validé par builds + wheels |
| #247 | DEPENDENCIES-BUILD-POLICY | inventaire des dépendances retenues |
| #246 | DEPENDENCIES-BUILD-POLICY + FOUNDATION-BUILD-SMOKE | socle CMake/presets exécuté Linux/GCC ; compléter cibles et plateforme visées |
| #259 | CONCURRENCY-PYTHON-API | tests race, cancellation, providers |
| #256 | CONCURRENCY-PYTHON-API : nanobind candidat | spike comparatif nanobind/pybind11 mesuré |
| #250 | ARRAYS-NUMERICS-CONTRACT | inventaire tracé 36/36 et TLC-FC |
| #251 | ARRAYS-NUMERICS-CONTRACT | types natifs/tests ownership/layout |
| #253 | ARRAYS-NUMERICS-CONTRACT | sélection fondée sur #250 et mesures |
| #248 | DEPENDENCIES-BUILD-POLICY + FOUNDATION-BUILD-SMOKE | export/consommateur CMake Linux prouvés ; politiques de version et tests de cibles réelles restants |
| #249 | SECURITY-QUALITY-COMPATIBILITY + FOUNDATION-BUILD-SMOKE | CTest minimal 1/1 réussi Linux ; format/analyse statique et tests natifs réels à ajouter |
| #254 | SPECS-LOCK-AND-CONFORMANCE | lock + vérif réelle/offline/négative |
| #255 | SPECS-LOCK-AND-CONFORMANCE | specgen exécuté deux fois, identité |
| #258 | CONCURRENCY-PYTHON-API | API/stubs/parité sur objets natifs |
| #257 | CONCURRENCY-PYTHON-API | wheels/install/import natives réelles |
| #243 | SECURITY-QUALITY-COMPATIBILITY | workflows impact-aware appliqués |
| #14 | SECURITY-QUALITY-COMPATIBILITY | compatibilité et migration éprouvées |
| #13 | SECURITY-QUALITY-COMPATIBILITY | threat model et tests négatifs |
| #51 | READINESS-AND-GOVERNANCE + CONTRIBUTING | parcours clonable/PR template |
| #261 | READINESS-AND-GOVERNANCE | labels/milestones/gates **appliqués** |
| #263 | LICENSE + NOTICE + DCO + GOVERNANCE + LICENSE-GATE | fichiers fusionnés sur main, licence projet publiée et règles de contribution vérifiées |

## Ordre d'exécution sans implémenter les domaines

1. Adopter ces politiques par revue ; accepter/réviser les limites.
2. Appliquer taxonomie GitHub à l'inventaire des issues.
3. Exécuter l'inventaire des 36 domaines (#250), puis arbitrer #251/#253.
4. Livrer le squelette technique non scientifique (#246, #249, #248,
   #254, #255, #256, #257) et vérifier ses preuves ; ce n'est pas une
   obligation de le coder pendant l'adoption des politiques.
5. Enrichir #51 avec commandes **réellement exécutables** et template PR.
6. Marquer `ready` seulement les issues qui respectent le contrat ;
   les domaines/lots ne sont pas automatiquement prêts.
7. Fermer les issues préparatoires **individuellement**, jamais par
   balayage administratif.

## Position scientifique

Le snapshot de départ demeure celui cité par #234 ; tout nouveau
snapshot exige diff #244 et décision #254. tllib-specs#231 et tllib#231
restent des blockers spécifiques, aucun « fix » local.
