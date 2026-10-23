# Migration du backlog

## Principe

Un problème possède une seule issue autoritaire.

- questions scientifiques/normatives : `tllib-specs` ;
- architecture, runtime, bindings, packaging et domaines implémentés :
  `tllib`.

## tllib-specs

- conserver l'historique de publication/handoff déjà terminé ;
- #206 est superseded par l'epic V1 autoritaire dans `tllib` ;
- #207–#214 doivent être remplacées par les issues de fondation correspondantes
  dans `tllib`, puis fermées comme superseded ;
- #179–#204 et #215–#224 doivent renvoyer vers les 36 epics domaine de
  `tllib`, puis être fermées comme superseded ;
- #230 doit être superseded par le guide contributeur de `tllib` ;
- toute nouvelle ambiguïté scientifique reste ou est créée dans
  `tllib-specs`.

## tllib

- #1–#9 restent dans l'historique ; ne pas les rouvrir pour réécrire l'histoire ;
- #10–#14 sont réécrites pour C++ + Python ;
- #15–#50 restent les 36 epics domaine ;
- #51 devient le guide multi-voie contributeur ;
- #52 devient l'epic autoritaire V1 complète ;
- #53–#230 gardent les TLC-FC et les liens de snapshot mais reçoivent le nouveau
  template end-to-end ;
- #231 reste un blocker d'implémentation lié à une issue normative créée dans
  `tllib-specs`.

## Anti-duplication

Avant toute nouvelle issue :
1. identifier le dépôt autoritaire ;
2. chercher une issue existante ;
3. lier un blocker au lieu de recopier le problème ;
4. garder une seule checklist d'acceptation autoritaire.
