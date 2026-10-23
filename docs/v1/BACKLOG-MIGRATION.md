# Migration du backlog

## Principe

Un problème possède une seule issue autoritaire.

- questions scientifiques/normatives : `tllib-specs` ;
- architecture, runtime, bindings, packaging, domaines et lots d'implémentation : `tllib`.

## État atteint

### tllib-specs

Les anciennes issues d'implémentation ont été fermées comme superseded :

- #206–#214 : fondation/architecture/packaging/documentation tllib ;
- #179–#204 et #215–#224 : 36 domaines ;
- #230 : guide contributeur tllib.

Elles restent dans l'historique avec des liens vers leurs remplacements dans tllib.

Le dépôt conserve les vraies questions normatives. Exemple actuel :
- tllib-specs#231 — clarifier les entrées de TLC-FC-30-EXPANSION-014.

### tllib

- #1–#9 restent dans l'historique et ne définissent plus l'architecture V1 ;
- #10–#14 sont réalignées C++ + Python ;
- #15–#50 sont les 36 epics domaine autoritaires ;
- #51 est le guide contributeur multi-profils ;
- #52 est l'epic autoritaire V1 complète ;
- #53–#230 sont les 178 lots TLC-FC migrés vers le template V1 end-to-end ;
- #231 est un blocker d'implémentation lié à tllib-specs#231 ;
- #234–#244 sont les fondations techniques autonomes V1.

## Règle anti-duplication

Avant toute nouvelle issue :

1. identifier le dépôt autoritaire ;
2. chercher une issue existante ;
3. lier un blocker au lieu de recopier un problème ;
4. garder une seule checklist d'acceptation autoritaire ;
5. ne jamais résoudre une ambiguïté scientifique dans tllib.

## Règle de synchronisation

Une évolution de tllib-specs passe par #244 puis #240.

Un nouveau domaine ou TLC-FC reste un gap tant qu'une décision explicite n'existe pas dans tllib. Aucun support implicite n'est autorisé.
