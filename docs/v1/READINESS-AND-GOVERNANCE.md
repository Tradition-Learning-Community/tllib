# V1 — Gouvernance des issues et ouverture aux contributeurs

Statut : **politique de gouvernance des contributions V1**, avec application initiale des labels de type/aire en phase C. Les milestones, protections et qualifications scientifiques individuelles sont des gates distincts encore à vérifier. Voir [l'audit du 31 octobre 2026](PHASE-C-AUDIT-2026-10-31.md).
Autorité de gouvernance du projet : **Tradition Learning Community ASBL** (voir `GOVERNANCE.md`). tllib reste autoritaire pour le logiciel, tllib-specs pour les décisions scientifiques. Contributions sous Apache-2.0 avec DCO 1.1, droits des auteurs préservés (voir `LICENSE`, `NOTICE`, `DCO`).
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
**Milestones :** #261 a été clôturée après décision de ne **pas** rendre les jalons GitHub obligatoires. Leur absence n'empêche ni de qualifier une tâche ni de commencer le développement. Les epics et les lots existants fournissent la coordination ; ne pas recréer de gates administratifs. Les composants de contribution documentent les responsabilités, indépendamment des labels `area:*` existants.

## Licence et contribution

L'association détient la responsabilité du projet et de ses publications. Elle n'acquiert pas automatiquement les droits d'auteur de toutes les contributions ; toute cession exige un accord distinct. Le prérequis de publication de la licence est **terminé** : #263, PR #264. `LICENSE`, `NOTICE`, `DCO` et `GOVERNANCE.md` sont intégrés à `main`. Ce préalable juridique est **distinct** des gates de CMake, des labels et de conformité scientifique.

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
- #261 est **clôturée** : la taxonomie est appliquée ; les jalons supplémentaires n'ont pas été retenus comme condition bloquante.

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

## Historique de l'audit (31 octobre 2026 — ne pas utiliser comme statut courant)

Au début de la phase C, l'audit GitHub a recensé 225 issues ouvertes : 36 epics domaine, 178 lots, cinq epics techniques/produit, cinq tâches transversales et un blocker scientifique. La clôture justifiée des quatre epics de préparation #234, #236, #240 et #242 ramène ensuite le backlog à 221 issues ouvertes ; l'epic produit #52 reste ouvert. Toutes ont un type et au moins une aire ; **aucun** lot n'a reçu `status:ready` sans revue de sa mini-matrice. Seuls #231 et #177 portent `status:blocked` (blocage scientifique limité à TLC-FC-30-EXPANSION-014). Les milestones **ne sont pas encore appliqués** ; le gate d'acceptation de #261 reste donc ouvert. Voir [audit détaillé](PHASE-C-AUDIT-2026-10-31.md), [parcours contributeurs](CONTRIBUTOR-QUICKSTART.md) et [revue/fusion](REVIEW-AND-MERGE.md).

**Décision de triage :** la fermeture d'une fondation commune ne constitue pas, à elle seule, une preuve que les entrées/sorties, acceptations et providers de chaque TLC-FC sont prêts. Documenter des critères ciblés d'acceptation par lot avant toute application de `status:ready`. Les issues sans statut restent à qualifier, pas bloquées par défaut.


## Application actuelle : lancement de l'implémentation

- Les issues **#15–#50** et **#53–#230** restent les directives de domaine et de lot ; aucune requalification en masse ni redécoupage des 694 TLC-FC.
- **#52** est l'epic produit, **#10** documentation, **#11** release, **#12** performance. Les huit composants sont documentés dans [COMPONENTS-AND-CONTRIBUTION.md](COMPONENTS-AND-CONTRIBUTION.md), sans nouvelle hiérarchie concurrente.
- `status:ready` est donné **au cas par cas**, avant le travail sur une tâche suffisamment définie ; si une information manque, préciser cette tâche, pas tout le dépôt.
- Les deux seuls blockers déjà identifiés restent ciblés sur TLC-FC-30-EXPANSION-014 (#231 et partie de #177) ; aucune autre réalisation ne doit attendre leur résolution.
- Les checklists des issues se cochent uniquement lorsque les livrables/tests correspondants existent ; une issue `open` ou sans statut reste ouverte sans être nécessairement bloquée.
- Les paragraphes de « graphe de préparation » et les chiffres d'audit ci-dessus sont **historiques**, non des prérequis à recommencer.
