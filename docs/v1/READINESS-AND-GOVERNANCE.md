# V1 — Gouvernance des issues et ouverture aux contributeurs

Statut : **politique proposée pour revue** (PR de préparation, sans implémentation).
Autorité : tllib pour le travail logiciel ; tllib-specs pour les décisions scientifiques.
Le document ne prétend pas que les gates techniques ont déjà été exécutés.

## Taxonomie minimale

Une issue ouverte porte exactement un label de type :
`type:epic`, `type:domain`, `type:tlc-fc`, `type:task`, `type:blocker`.
Une ou plusieurs aires : `area:cpp`, `area:python`, `area:runtime`,
`area:specs`, `area:docs`, `area:ci`, `area:release`.
Un seul état de travail : `status:blocked` ou `status:ready` ;
une issue en cours peut retirer ces deux labels sans signifier « terminé ».
`good first issue` n'est attribué qu'à une tâche autonome et testable.

Des labels sont **des états administratifs**, jamais une preuve de conformité ;
les labels ne doivent pas être créés dans tllib-specs pour des tâches logicielles.
Milestone recommandé : `V1 — preparation` pour les décisions/fondations
et `V1 — implementation` pour domaines/lots, sous réserve de disponibilité
de milestones dans GitHub. Les epics regroupent les issues, pas de travail
en doublon.

## Contrat d'une issue prête

L'issue `status:ready` satisfait **toutes** ces conditions :
1. elle appartient au dépôt autoritaire et a un périmètre unique et stable ;
2. dépendances applicables terminées ou interfaces contractuellement gelées ;
3. snapshot/identifiants du handoff précisés si la tâche touche la science ;
4. intrants, extrants, erreurs et critères d'acceptation non ambigus ;
5. points de variation et dépendances externes explicités ;
6. tests/preuves reproductibles prévus sans demander au contributeur
   de résoudre une décision d'architecture ou une question normative ;
7. propriétaire/reviewer de décision identifié par la gouvernance du projet ;
8. aucun blocker scientifique ouvert ne concerne la partie exécutable.

Une issue de lot peut être partiellement exécutable : décomposer par comportement
sans changer ses TLC-FC et garder le segment concerné `blocked`. Ne jamais
mettre tout `expansion` en attente à cause de #231 : seuls la fonctionnalité
TLC-FC-30-EXPANSION-014 et son sous-travail dans #177 sont bloqués.

## Format d'une issue de contribution

- Autorité / issue parent et dépendances (avec liens GitHub).
- Snapshot de référence : SHA complet et version du modèle du handoff.
- Identifiants TLC-FC et contrats partagés exacts, si pertinents.
- Obligations observables : comportements requis et interdits.
- Surfaces : C++ / Python / fournisseur / documentation.
- Preuves : commande et rapport d'acceptation / tests / comparaison.
- Risques : tolérances, déterminisme, précision, mémoire, sécurité.
- État : ready/blocked et raison ; critères de fermeture vérifiables.

## Graphe de préparation

- #260 (plateformes) éclaire #246 (build), #257 (wheels), #243 (CI).
- #247 (dépendances) éclaire #246, #249 et #253.
- #250 (inventaire effectif) précède la stabilisation de #251 et #253.
- #254 (snapshot) précède #255 (specgen), puis #241 (conformance).
- #256 (spike binder vérifié) précède la fermeture de #257 ; #258 peut
  fixer la convention API indépendamment du binder.
- #259 gouverne #238, #239 et les bindings.
- #14 et #13 sont des revues transverses ; #51 traduit le tout en parcours.
- #261 se clôt uniquement quand labels, jalons et dépendances sont **appliqués
  dans GitHub**, pas seulement écrits ici.

## Règles de clôture

Les issues purement décisionnelles peuvent se fermer après adoption de
l'ADR, références croisées et disparition des décisions ouvertes.
Les issues comportant du build, des tests, de l'export CMake, un spike,
des wheels, des scripts ou de la CI **restent ouvertes** jusqu'à preuve
exécutable réelle. Ne jamais cocher un test sur la seule foi d'une politique.
Ne jamais reclasser en `ready` en masse les 36 domaines et les 178 lots
avant vérification de toutes leurs dépendances.

## PR et discipline

PR focalisée, sans implémentation scientifique ajoutée en opportuniste ;
preuve du SHA specs et de la population ciblée si applicable.
Changements normatifs scientifiques exclusivement dans tllib-specs avec
revue scientifique et republication. Les décisions techniques sont
versionnées par ADR et revue d'architecture, pas inventées dans une PR
de domaine.
