# Phase C — Audit factuel de préparation des contributions (31 octobre 2026)

**Source** : API GitHub des issues de [tllib](https://github.com/Tradition-Learning-Community/tllib/issues) (`state=all`, 3 pages de 100) et fichiers publiés sur `main` au commit `66f54a576ef264bc651354b71cd18e46284cd6e0`. Cet état est un instantané d'audit ; les nombres peuvent évoluer avec les contributions. Références : [#261](https://github.com/Tradition-Learning-Community/tllib/issues/261), [#51](https://github.com/Tradition-Learning-Community/tllib/issues/51), [inventaire historique](ISSUE-AUDIT-2026-10-23.md). La phase C ne modifie **pas** `tllib-specs`.

## 1. Recensement réel

| Groupe | État au début de la phase C |
| --- | ---: |
| Issues tllib, hors PR | **259** |
| Issues ouvertes | **225** |
| Issues fermées | **34** |
| PR historiques (dans la liste issue GitHub) | **23** |
| Epics domaine #15–#50 | **36 ouvertes** |
| Lots TLC-FC #53–#230 | **178 ouverts** |
| Autres issues ouvertes | **11** |

Les 11 issues sont : epic produit #52 ; epics de fondation #234, #236, #240, #242 ; gouvernance #261 ; parcours #51 ; blocker scientifique #231 ; documentation #10 ; release #11 ; performance #12. Les issues techniques autonomes #235, #237–#239, #241, #243–#260 ont été examinées par référence à leurs PR de réalisation/clôture ; les ouvrir à nouveau sans preuve d'une lacune serait un doublon.

### Classification effectivement appliquée à GitHub (au cours de la phase C)

- **`type:domain` : 36** epics de coordination ; **`type:tlc-fc` : 178** lots, étiquetés `area:cpp` comme surface de référence, avec façade Python **seulement si applicable** selon le contrat du lot.
- **`type:epic` : 5** (#52, #234, #236, #240, #242) ; **`type:task` : 5** (#10, #11, #12, #51, #261) ; **`type:blocker` : 1** (#231).
- Chacune des 225 issues ouvertes possède exactement **un** type et **au moins une** aire, après application. Il n'a été créé aucun label `good first issue` fictif.
- **`status:ready` : 0**, non qualifié tant qu'aucune mini-matrice scientifique/technique de lot n'a été vérifiée individuellement. **`status:blocked` : 2** (#231 et #177). Le blocage de #177 concerne sa clôture globale ; **seule** la TLC-FC 014 est scientifiquement bloquée. Les quatre autres fonctionnalités n'héritent pas d'un blocker scientifique.
- **Milestones affectés : 0** à l'instant de cet audit. La politique propose préparation / implémentation / release ; la connexion GitHub disponible ici autorise le classement par labels, mais **n'expose aucune action de création de milestone**, ni d'API GET correspondante. Ne pas prétendre que les milestones sont appliqués avant une action administrative explicite. Préparation : #261/#51 et epics de fondation ; implémentation : domaines/lots et performance ; release : #11 et documentation finale selon scope.

### Références et dépendances observées

Un contrôle de structure des 178 bodies de lots a trouvé des références `TLC-FC`, au SHA verrouillé `07439babd59c657354e3200ed24c55e2e3eeb72c`, à une issue parent #15–#50 et à l'acceptation ; les 36 epics pointent vers un `handoff/domains/`. **Ce contrôle de présence de liens n'est pas la vérification scientifique des contenus des 694 TLC-FC.** Le snapshot est verrouillé dans [specs.lock.json](../../specs.lock.json), catalogue SHA-256 `61ad981d2d65500af2b18aae659867dfa7e738a6cf1a0f8737956eae1624ee88`.

Chaque lot doit être qualifié selon les contrats **réellement utilisés** : types et interfaces #235/#237, runtime #238, providers #239 si requis, arrays #236 si requis, Python #242 si API publique, génération/conformité #240/#241, stabilité du lock et diff #244, tests et règles techniques #243, plus les acceptances spécifiques. Les fondations closes **ne rendent pas automatiquement l'implémentation scientifique prête** : il faut une matrice ID → comportement → I/O/erreurs → providers → tests vérifiable par lot.

L'issue [tllib-specs#231](https://github.com/Tradition-Learning-Community/tllib-specs/issues/231) reste **ouverte** et concerne `TLC-FC-30-EXPANSION-014`. Le blocker d'implémentation [#231](https://github.com/Tradition-Learning-Community/tllib/issues/231) et le lot [#177](https://github.com/Tradition-Learning-Community/tllib/issues/177) restent donc bloqués pour cette fonctionnalité. Ni le domaine #40 ni les 35 autres domaines ne sont globalement bloqués par cette seule question.

### Clôtures préparatoires effectuées pendant la phase C

Après vérification de leurs dépendances et preuves natives/CI, les epics **#234 (fondation)**, **#236 (arrays)**, **#240 (specs)** et **#242 (Python)** ont été fermés avec le motif `completed` et une note de clôture justifiée dans leur body. L'état final à ce point est **221 issues ouvertes et 38 fermées** (36 domaines, 178 lots, epic produit #52, tâches #10/#11/#12/#51/#261, blocker #231). Le tableau précédent conserve l'**état initial** mesuré ; il ne doit pas être relu comme une mesure après clôture. Aucune issue scientifique de domaine ou de lot n'a été fermée.

## 2. Fondations : états vérifiables, sans fausse couverture

| Capability | État et preuve |
| --- | --- |
| Licence / gouvernance | **Terminé et vérifié sur main** : `LICENSE`, `NOTICE`, `DCO`, `GOVERNANCE.md` (PR #264, issue #263 fermée). |
| Core / runtime / huit contrats / providers | **Livré et testé sur Linux** : PR #270–#272, CTest et intégration native ; pas de logique TLC-FC. |
| Arrays, CMake/export, bindings et roue Python locale | **Livré et testé sur Linux** : PR #274–#278, CMake external consumer, CPython 3.12 wheel/import, editable, parité structurelle. |
| Snapshot / génération / conformité | **Livré et testé** : PR #273, #279, #282 ; 36 domaines, 694 TLC-FC, 8 contrats, génération déterministe et rapport explicite. `release-gate` **échoue légitimement**. |
| Qualité / sécurité / compatibilité / CI | **Fondations qualifiées sur Linux** : PR #279–#282 ; tests négatifs, ASan/UBSan, qualité locale/CI impact-aware. Release/sécurité exhaustive des algorithmes à venir **non applicable à ce stade**. |
| Autres OS / Python | **Non vérifiés** : Windows/macOS/aarch64 et CPython autre que 3.12 pour wheel. |
| Instructions contributeurs / revue | **Livrables de la phase C en PR** : [CONTRIBUTOR-QUICKSTART.md](CONTRIBUTOR-QUICKSTART.md), [REVIEW-AND-MERGE.md](REVIEW-AND-MERGE.md) ; clôture #51 conditionnée à la fusion et à la vérification finale. |
| Protection effective de `main` | **Non vérifiée** : GET de la protection de branche a renvoyé 403 pour l'intégration disponible ; l'API des rulesets visible renvoie `[]`. Ceci **ne prouve pas** l'absence de toute protection administrateur. |
| Milestones | **Non appliqués** : action administrative/permission de création nécessaire. Tant que ce gate manque, ne pas fermer #261. |

Les jobs GitHub Actions réussis sur `main` du 30 octobre 2026 incluent le natif, la wheel et la conformité après PR #280, ainsi que la qualité et les specs après #282 (voir [CI-OPERATIONS.md](CI-OPERATIONS.md)). Ce sont des preuves observées dans la CI du dépôt, **pas** un nouveau build local de la phase C ; le shell utilisé ici ne résout pas `github.com` et ne peut donc pas réaliser un clone propre supplémentaire.

## 3. Ouverture progressive et travaux restant à fermer

- **Fondations communes** : exploiter les interfaces effectivement livrées, ne pas refaire les ADR, la politique de dépendances ou les huit contrats.
- **Lot** : revue documentaire du handoff, mini-matrice, statut non ambigu, gate tests/preuves puis `status:ready` **uniquement** après validation. Aucun lot ready au stade de cet audit.
- **QA / tooling / documentation** : contribution possible **par issue autonome** sans compiler la bibliothèque, après périmètre, commandes et critères vérifiables. Ne pas créer de `good first issue` artificiel.
- **Fin de préparation** : faire approuver/fusionner les guides et modèles, vérifier liens/commandes, fermer les epics de fondation uniquement si leurs propres critères le permettent, créer/appliquer les milestones via une interface administrative GitHub, puis fermer #261 uniquement après preuve.
- **Release** : #10 (documentation complète), #11 (publication) et #12 (benchmarks effectifs) restent des tâches V1 réelles ; elles ne doivent pas bloquer artificiellement le commencement d'un lot par ailleurs qualifié.

**Verdict factuel de l'audit avant clôture des tâches administratives : PRÊT PARTIELLEMENT.** Le socle commun fonctionne sur l'environnement Linux vérifié ; l'outillage et la documentation sont contributifs. Aucun lot n'a encore une preuve individuelle suffisante pour porter `status:ready`. L'absence de milestones appliqués et de vérification des protections interdit de déclarer #261 terminée ou la gouvernance entièrement finalisée.
