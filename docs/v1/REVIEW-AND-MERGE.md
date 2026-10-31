# Revue, acceptation et fusion — préparation V1 de tllib

Autorité de gouvernance : **Tradition Learning Community ASBL**, conformément à [GOVERNANCE.md](../../GOVERNANCE.md). Cette procédure concerne les contributions logicielles à `tllib`, sous Apache-2.0 et DCO 1.1. L'autorité scientifique et normative reste exclusivement `tllib-specs`.

## Qui examine quoi

- **Mainteneur habilité par la gouvernance de l'ASBL** : valide le périmètre, la provenance, les preuves, le respect du processus et l'opportunité de fusion. Une approbation d'une personne non autorisée à fusionner n'accorde pas automatiquement ce droit.
- **Relecteur technique adapté à la surface** (C++20/runtime, Python/typing/lifetime, tooling/specs, sécurité/CI, documentation) : examine les interfaces publiées, le modèle mémoire, les erreurs, les versions, les dépendances, la conformité aux ADR et les tests. Une PR touchant une interface commune demande la revue des mainteneurs concernés avant fusion.
- **Revue scientifique quand des TLC-FC sont consommées** : compare les comportements observables, erreurs, préconditions, acceptations positives et négatives à `contract.json`, `acceptance.json` et aux contrats partagés **du SHA verrouillé**. Le relecteur ne peut ni ajouter une obligation normative ni inventer une science absente du handoff. Un blocage est traité dans `tllib-specs` avec blocker logiciel ciblé.
- **Revue de sécurité / compatibilité** : nécessaire lorsqu'une PR modifie les frontières de confiance, la mémoire/lifetime, les providers externes, le packaging, les versions, un format ou un snapshot. Exiger tests de rejet et migration si la compatibilité évolue.

Aucun nombre fixe d'approbations ni identité de CODEOWNER ne sont prétendus configurés automatiquement dans GitHub. Avant la fusion, le mainteneur responsable doit vérifier les règles réellement actives sur `main` ; si une protection est absente ou inaccessible, appliquer ces contrôles **manuellement et le déclarer**, sans prétendre que GitHub les impose.

## Conditions de fusion

1. Issue tllib autoritaire, périmètre circonscrit, dépendances réelles satisfaites. Epic parent et IDs TLC-FC renseignés lorsqu'applicables ; aucune réécriture des 36 epics ou du découpage des 178 lots.
2. Commits de leurs auteurs signés DCO (`Signed-off-by:`), droits/licences tiers et NOTICE préservés. Les auteurs ne cèdent **pas** leurs copyrights à l'ASBL par cette procédure ; aucun CLA systématique.
3. Snapshot immuable identifié par SHA exact lorsque la PR consomme la science. Tout changement du snapshot fait l'objet du diff offline `specs_sync.py`, de la validation scientifique/compatibilité et d'une PR de lock distincte.
4. Les commandes pertinentes ont été **exécutées** et leurs résultats sont présents dans la PR. Pour C++ : build/CTest, consommateur externe si package ; pour Python : installation/wheel/typing, erreurs/lifetime/parité ; pour tooling : tests négatifs, provenance et déterminisme ; pour domaine : chaque acceptance applicable liée à un test réellement réussi. Pas de `covered` sans preuve.
5. Les checks effectivement déclenchés par les filtres de fichiers sont verts. Une PR docs-only peut n'avoir **aucun** job de compilation ; les mainteneurs relisent les liens/commandes, sans exiger un job absent, sans désactiver une protection, ni considérer « aucun job » comme un succès de compilation.
6. Aucune vulnérabilité sensible, secret, contenu tiers incompatible ou risque majeur non traité ; limites et travaux différés explicites. Les problèmes de sécurité sensibles utilisent [SECURITY.md](../../SECURITY.md).
7. L'approbation technique et, si applicable, scientifique précède la fusion. Une PR bloquée reste ouverte ; ne jamais masquer un échec en désactivant un contrôle requis.

## Après la fusion

- Attendre la confirmation GitHub que la PR est **fusionnée** dans `main` et identifier le commit effectivement fusionné.
- Fermer l'issue avec `completed` et les liens PR/commit seulement si **tous** ses critères sont satisfaits. Une PR documentaire ne clôt pas un travail demandant des tests ou une implémentation.
- Une issue remplacée est fermée `not planned` ou `duplicate` avec justification, sans fermer artificiellement les tâches réelles.
- Requalifier `status:ready` ou `status:blocked` après changement de dépendance, et conserver #231 ciblé sur `TLC-FC-30-EXPANSION-014` tant que l'amont normatif n'est pas republie et vérifié.
- Les epics de domaine coordonnent les lots ; ils ne deviennent pas `ready` par simple fermeture des tâches préparatoires. Le gate final [DEFINITION-OF-DONE.md](DEFINITION-OF-DONE.md) reste distinct du gate d'ouverture progressive.

## Rôles contributeurs et limites

Une personne peut contribuer uniquement à la documentation, QA et outillage Python sans connaître tout le C++. La sélection de tâche suit [CONTRIBUTOR-QUICKSTART.md](CONTRIBUTOR-QUICKSTART.md). Le label `good first issue` exige un périmètre autonome, des tests et aucune décision scientifique ou architecturale ouverte ; ne pas l'ajouter à un lot complexe pour attirer des contributeurs.

Les restrictions GitHub (protections, status checks requis, règles CODEOWNERS) doivent être **relues via une vue administrateur**. L'accès actuel de l'intégration a reçu HTTP 403 pour l'endpoint de protection de branche : la protection est donc **non vérifiée**, et non présumée absente ou désactivée.
