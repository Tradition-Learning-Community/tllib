Voir les [parcours contributeurs](../docs/v1/CONTRIBUTOR-QUICKSTART.md) et [règles de revue/fusion](../docs/v1/REVIEW-AND-MERGE.md). Remplir les champs **seulement s'ils sont applicables** : pour une correction documentaire, marquer « sans objet » pour les TLC-FC, la parité et les performances.

## Licence et provenance

- [ ] Je soumets ma contribution sous la licence Apache-2.0 de `tllib` et respecte les licences des tiers.
- [ ] Chaque commit que j'ai personnellement créé porte mon `Signed-off-by` DCO v1.1 (`git commit -s`), ou j'ai indiqué les raisons et actions correctives nécessaires.
- [ ] Je n'affirme pas transférer les droits d'auteur d'autres personnes à l'ASBL.

Références : [LICENSE](../LICENSE) · [DCO](../DCO) · [GOVERNANCE](../GOVERNANCE.md).

## Issue autoritaire et périmètre

Issue concernée : # (ne renseigner `Closes #` que si **tous** les critères sont effectivement satisfaits)
Depends on #
Dépôt d'autorité : tllib pour code/outillage ; tllib-specs pour science

## TLC-FC et snapshot (si applicable)

- TLC-FC IDs / contrats partagés :
- tllib-specs SHA **complet** et catalogue/versions :
- Statuts d'exécution publiés :
- Acceptations / interdictions observables :

## Nature du changement

- [ ] documentation / gouvernance seulement
- [ ] core C++ / arrays / runtime
- [ ] bindings et API Python
- [ ] tooling specs / conformance
- [ ] domaine / lot TLC-FC
- [ ] tests / sécurité / build / packaging

## Contrats et garanties

- Résumé :
- Interfaces/erreurs/ownership modifiés :
- Provenance et comportement deterministe :
- Précision numérique, tolérances **justifiées par contrat** :
- Compatibilité / migration (obligatoire pour API/ABI, wheel, format ou specs modifiés) :
- [ ] Changement breaking ? Si oui : migration documentée, version/ABI, note de release et tests de rejet/upgrade.
- [ ] Snapshot inchangé, ou diff offline `specs_sync.py` relu et modification du lock dans une PR séparée.
- Sûreté / dépendances / licences :

## Preuves réellement exécutées

| Commande | Environnement | Résultat |
| --- | --- | --- |
| (non exécuté / sans objet / commande exacte) | | |

- Acceptation sur cas négatifs / comportements interdits :
- Parité C++/Python si applicable :
- Artefact externe installé si packaging :
- Limites et tests non réalisés :

## Relectures attendues

- Relecteur technique / surface :
- Revue architecture requise ? (API commune, ABI, providers, modèle mémoire) :
- Revue scientifique requise ? (TLC-FC et acceptations publiées) :
- Checks effectivement déclenchés et contrôles manuels pour docs-only :

## Blockers et revue

- Question scientifique upstream dans tllib-specs (URL si applicable) :
- Dépendances de tâche encore ouvertes :
- [ ] Aucun calcul, défaut normatif, provider, catégorie, équation ou tolérance scientifique n'a été inventé
- [ ] Aucune implémentation scientifique parallèle Python
- [ ] Aucun statut ready/terminé déclaré sans preuve
- [ ] PR ciblée : pas de refonte non liée
