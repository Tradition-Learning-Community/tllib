# Audit exhaustif du backlog tllib — 2026-10-23

> Audit des **issues du dépôt tllib** obtenu depuis GitHub. Cet inventaire décrit l'état observé et distingue **décision documentaire**, **composant réellement livré**, et **preuve de tests**. Il ne prouve pas qu'une issue ouverte est prête. Autorité scientifique inchangée : tllib-specs.

- Issues inspectées : **259** ; ouvertes **249**, fermées **10**.
- Domaines : **36** epics ouverts (#15–#50).
- Lots : **178** issues TLC-FC ouvertes (#53–#230), **178** identifiées et **0** orientées C++ ; aucune labellisée `status:ready`.
- **N'affecter aucun lot TLC-FC aux contributeurs avant ses dépendances réelles**. Les domaines et lots sont préservés sans réécriture fonctionnelle.

## Trois niveaux d'activité

1. **Avant les contributions domaine (P0/P1) :** stabiliser les décisions communes et livrer les éléments fondationnels C++/Python/specs/conformance qui sont nécessaires à un lot autonome ; vérifier les outils installables.
2. **Pendant les contributions (transverse) :** performance, documentation détaillée, sécurité et CI proportionnées au code qui existe ; aucun faux job exécuté par obligation administrative.
3. **Avant release seulement :** packaging complet, wheels et attestations de publication. Ces epics restent ouverts mais ne doivent pas empêcher un contributeur de commencer un lot dont les interfaces sont validées.

## Registre des issues non-domaines (lecture individuelle)

| Issue | Rôle | Décision et blocage réel |
| --- | --- | --- |
| [#10](https://github.com/Tradition-Learning-Community/tllib/issues/10) | Documentation complète | Avant release ; quickstarts et API générées après code, pas gate de démarrage globale. |
| [#11](https://github.com/Tradition-Learning-Community/tllib/issues/11) | Release/packaging | Après composants C++/Python et conformité ; ne pas confondre avec export CMake #248. |
| [#12](https://github.com/Tradition-Learning-Community/tllib/issues/12) | Performance | Définir méthodologie avant les algorithmes ; baseline chiffrée après implémentation. |
| [#13](https://github.com/Tradition-Learning-Community/tllib/issues/13) | Sécurité | Threat model et limites parseurs/providers d'abord ; fuzz/ASan sur code existant. |
| [#14](https://github.com/Tradition-Learning-Community/tllib/issues/14) | Compatibilité | Politique et mapping specs figés avant APIs ; tests de rupture après types natifs. |
| [#51](https://github.com/Tradition-Learning-Community/tllib/issues/51) | Contributeurs | Chemins concrets et commandes du build, specs, Python, QA vérifiés avant onboarding massif. |
| [#52](https://github.com/Tradition-Learning-Community/tllib/issues/52) | Epic produit | Conteneur V1 ; ne pas fermer avant toute release. |
| [#231](https://github.com/Tradition-Learning-Community/tllib/issues/231) | Blocker scientifique ciblé | EXPANSION-014 uniquement ; renvoi tllib-specs#231 ; ne pas bloquer 36 domaines. |
| [#234](https://github.com/Tradition-Learning-Community/tllib/issues/234) | Epic fondation | Conteneur : dépend de preuves #246–#249. |
| [#235](https://github.com/Tradition-Learning-Community/tllib/issues/235) | Primitives C++ | P0 : FeatureId, statuses, Error/Result, sérialisation testés ; aucun domaine sans types communs. |
| [#236](https://github.com/Tradition-Learning-Community/tllib/issues/236) | Epic arrays | Conteneur : ne pas forcer une abstraction sans #250. |
| [#237](https://github.com/Tradition-Learning-Community/tllib/issues/237) | 8 contrats partagés | P0 : validateurs natifs des huit contrats ; centraliser les fixtures. |
| [#238](https://github.com/Tradition-Learning-Community/tllib/issues/238) | Registry/runtime | P0 : registre déterministe, dispatch, ExecutionContext, invalides testés. |
| [#239](https://github.com/Tradition-Learning-Community/tllib/issues/239) | Providers natifs/Python | P0 : port commun implémenté/testé et non un choix dans chaque lot. |
| [#240](https://github.com/Tradition-Learning-Community/tllib/issues/240) | Epic specs | Conteneur : #254, #255, #244. |
| [#241](https://github.com/Tradition-Learning-Community/tllib/issues/241) | Conformité | P0 : reporting du catalogue complet, états, liens d'acceptation ; pas de faux support. |
| [#242](https://github.com/Tradition-Learning-Community/tllib/issues/242) | Epic Python | Conteneur : #256–#258, #252. |
| [#243](https://github.com/Tradition-Learning-Community/tllib/issues/243) | CI progressive | P1 : checks légers dès que cibles existent ; matrice complète seulement avant release. |
| [#244](https://github.com/Tradition-Learning-Community/tllib/issues/244) | Diff specs | P1 : comparer snapshots sans réouvrir science ; besoin avant toute mise à jour du lock. |
| [#246](https://github.com/Tradition-Learning-Community/tllib/issues/246) | CMake C++20 | Socle initial fusionné via #266 ; revoir CMake/presets et cibles natives avant fermeture. |
| [#247](https://github.com/Tradition-Learning-Community/tllib/issues/247) | Dépendances | P0 : politique décidée ; verrouiller dépendances réelles lorsque introduites. |
| [#248](https://github.com/Tradition-Learning-Community/tllib/issues/248) | Export CMake | Cible interface/finder initiale via #266 ; tests d'installation sur targets natifs futurs. |
| [#249](https://github.com/Tradition-Learning-Community/tllib/issues/249) | Qualité locale | P0 : CTest smoke initial ; clang-format/tidy, analyse, vrais tests à livrer. |
| [#250](https://github.com/Tradition-Learning-Community/tllib/issues/250) | Inventaire 36 domaines | P0 : établir matrice TLC-FC/data/numérique avant #251/#253 ; éviter over-engineering. |
| [#251](https://github.com/Tradition-Learning-Community/tllib/issues/251) | ArrayView | Après #250 : implémenter uniquement shapes/layouts/lifetimes prouvés. |
| [#252](https://github.com/Tradition-Learning-Community/tllib/issues/252) | NumPy/DLPack | Après #251/#256 : port commun, lifetime/copy testés. |
| [#253](https://github.com/Tradition-Learning-Community/tllib/issues/253) | Backends numériques | Après #250/#247 ; ne retenir aucun backend arbitraire. |
| [#254](https://github.com/Tradition-Learning-Community/tllib/issues/254) | specs.lock | P0 : fichier réel immuable, SHA catalogue, validateur offline et cas négatifs. |
| [#255](https://github.com/Tradition-Learning-Community/tllib/issues/255) | specgen | P0 : codegen structurel déterministe, non scientifique, byte-identical. |
| [#256](https://github.com/Tradition-Learning-Community/tllib/issues/256) | Choix binder | P0 : spike nanobind vs pybind11 réellement compilé ; ne pas décider sur préférence. |
| [#257](https://github.com/Tradition-Learning-Community/tllib/issues/257) | Package Python | P0 : wheel CMake-driven, import de l'extension, tests sur artefact installé. |
| [#258](https://github.com/Tradition-Learning-Community/tllib/issues/258) | API/typing/parité | Contrat commun #265 publié ; P0 : implémenter stubs et harness de parité. |
| [#259](https://github.com/Tradition-Learning-Community/tllib/issues/259) | Concurrence | Politique publiée ; P0 : cancellation, providers et réentrance testés. |
| [#260](https://github.com/Tradition-Learning-Community/tllib/issues/260) | Plateformes | Cible documentée ; qualifier matrice minimale réellement promettable. |
| [#261](https://github.com/Tradition-Learning-Community/tllib/issues/261) | Gouvernance des issues | P0 administratif : labels, milestones et dépendances doivent être appliqués, pas seulement écrits. |

## Issues de domaines — 36 epics conservés

- [#15](https://github.com/Tradition-Learning-Community/tllib/issues/15) — [Domaine 03] Implémenter Huit Dimensions (**open**)
- [#16](https://github.com/Tradition-Learning-Community/tllib/issues/16) — [Domaine 04] Implémenter Invariants (**open**)
- [#17](https://github.com/Tradition-Learning-Community/tllib/issues/17) — [Domaine 00] Implémenter Maître (**open**)
- [#18](https://github.com/Tradition-Learning-Community/tllib/issues/18) — [Domaine 01] Implémenter Disciple (**open**)
- [#19](https://github.com/Tradition-Learning-Community/tllib/issues/19) — [Domaine 08] Implémenter Principe (**open**)
- [#20](https://github.com/Tradition-Learning-Community/tllib/issues/20) — [Domaine 10] Implémenter Vertus (**open**)
- [#21](https://github.com/Tradition-Learning-Community/tllib/issues/21) — [Domaine 05] Implémenter Dynamiques (**open**)
- [#22](https://github.com/Tradition-Learning-Community/tllib/issues/22) — [Domaine 06] Implémenter Théorèmes (**open**)
- [#23](https://github.com/Tradition-Learning-Community/tllib/issues/23) — [Domaine 02] Implémenter Communauté (**open**)
- [#24](https://github.com/Tradition-Learning-Community/tllib/issues/24) — [Domaine 09] Implémenter Valeurs (**open**)
- [#25](https://github.com/Tradition-Learning-Community/tllib/issues/25) — [Domaine 07] Implémenter Message (**open**)
- [#26](https://github.com/Tradition-Learning-Community/tllib/issues/26) — [Domaine 11] Implémenter Capacités (**open**)
- [#27](https://github.com/Tradition-Learning-Community/tllib/issues/27) — [Domaine 17] Implémenter Transmission en cascade (**open**)
- [#28](https://github.com/Tradition-Learning-Community/tllib/issues/28) — [Domaine 15] Implémenter Relations (**open**)
- [#29](https://github.com/Tradition-Learning-Community/tllib/issues/29) — [Domaine 19] Implémenter Régulation (**open**)
- [#30](https://github.com/Tradition-Learning-Community/tllib/issues/30) — [Domaine 18] Implémenter Évaluation (**open**)
- [#31](https://github.com/Tradition-Learning-Community/tllib/issues/31) — [Domaine 13] Implémenter Pratique (**open**)
- [#32](https://github.com/Tradition-Learning-Community/tllib/issues/32) — [Domaine 20] Implémenter Robustesse (**open**)
- [#33](https://github.com/Tradition-Learning-Community/tllib/issues/33) — [Domaine 14] Implémenter Expérience vécue (**open**)
- [#34](https://github.com/Tradition-Learning-Community/tllib/issues/34) — [Domaine 16] Implémenter Cohorte (**open**)
- [#35](https://github.com/Tradition-Learning-Community/tllib/issues/35) — [Domaine 12] Implémenter Compétences (**open**)
- [#36](https://github.com/Tradition-Learning-Community/tllib/issues/36) — [Domaine 21] Implémenter Équité (**open**)
- [#37](https://github.com/Tradition-Learning-Community/tllib/issues/37) — [Domaine 23] Implémenter Mémoire (**open**)
- [#38](https://github.com/Tradition-Learning-Community/tllib/issues/38) — [Domaine 22] Implémenter Temporalité (**open**)
- [#39](https://github.com/Tradition-Learning-Community/tllib/issues/39) — [Domaine 29] Implémenter Propagation générationnelle (**open**)
- [#40](https://github.com/Tradition-Learning-Community/tllib/issues/40) — [Domaine 30] Implémenter Expansion (**open**)
- [#41](https://github.com/Tradition-Learning-Community/tllib/issues/41) — [Domaine 24] Implémenter Contexte (**open**)
- [#42](https://github.com/Tradition-Learning-Community/tllib/issues/42) — [Domaine 25] Implémenter Culture (**open**)
- [#43](https://github.com/Tradition-Learning-Community/tllib/issues/43) — [Domaine 26] Implémenter Identité (**open**)
- [#44](https://github.com/Tradition-Learning-Community/tllib/issues/44) — [Domaine 28] Implémenter Finalité et téléologie évolutive (**open**)
- [#45](https://github.com/Tradition-Learning-Community/tllib/issues/45) — [Domaine 27] Implémenter Réflexivité (**open**)
- [#46](https://github.com/Tradition-Learning-Community/tllib/issues/46) — [Domaine 31] Implémenter Institutionnalisation (**open**)
- [#47](https://github.com/Tradition-Learning-Community/tllib/issues/47) — [Domaine 32] Implémenter Dérive et correction (**open**)
- [#48](https://github.com/Tradition-Learning-Community/tllib/issues/48) — [Domaine 33] Implémenter Architecture à faible volume de données (**open**)
- [#49](https://github.com/Tradition-Learning-Community/tllib/issues/49) — [Domaine 35] Implémenter Fidélité au noyau invariant (**open**)
- [#50](https://github.com/Tradition-Learning-Community/tllib/issues/50) — [Domaine 34] Implémenter Cycle de vie de la transmission (**open**)

## Lots TLC-FC — 178 unités inchangées

- [#53](https://github.com/Tradition-Learning-Community/tllib/issues/53) — [Codage 00.01] master — fonctionnalités 001, 002, 003 (**open**)
- [#54](https://github.com/Tradition-Learning-Community/tllib/issues/54) — [Codage 00.02] master — fonctionnalités 004, 005, 006 (**open**)
- [#55](https://github.com/Tradition-Learning-Community/tllib/issues/55) — [Codage 00.03] master — fonctionnalités 007, 008, 009 (**open**)
- [#56](https://github.com/Tradition-Learning-Community/tllib/issues/56) — [Codage 00.04] master — fonctionnalités 010, 011, 012 (**open**)
- [#57](https://github.com/Tradition-Learning-Community/tllib/issues/57) — [Codage 00.05] master — fonctionnalités 013, 014, 015 (**open**)
- [#58](https://github.com/Tradition-Learning-Community/tllib/issues/58) — [Codage 00.06] master — fonctionnalités 016 (**open**)
- [#59](https://github.com/Tradition-Learning-Community/tllib/issues/59) — [Codage 01.01] disciple — fonctionnalités 001, 002, 003 (**open**)
- [#60](https://github.com/Tradition-Learning-Community/tllib/issues/60) — [Codage 01.02] disciple — fonctionnalités 004, 005, 006 (**open**)
- [#61](https://github.com/Tradition-Learning-Community/tllib/issues/61) — [Codage 01.03] disciple — fonctionnalités 007, 008, 009 (**open**)
- [#62](https://github.com/Tradition-Learning-Community/tllib/issues/62) — [Codage 01.04] disciple — fonctionnalités 010 (**open**)
- [#63](https://github.com/Tradition-Learning-Community/tllib/issues/63) — [Codage 02.01] community — fonctionnalités 001, 003, 004 (**open**)
- [#64](https://github.com/Tradition-Learning-Community/tllib/issues/64) — [Codage 02.02] community — fonctionnalités 005, 006, 007 (**open**)
- [#65](https://github.com/Tradition-Learning-Community/tllib/issues/65) — [Codage 02.03] community — fonctionnalités 008, 009 (**open**)
- [#66](https://github.com/Tradition-Learning-Community/tllib/issues/66) — [Codage 03.01] huit-dimensions — fonctionnalités 001, 002, 005 (**open**)
- [#67](https://github.com/Tradition-Learning-Community/tllib/issues/67) — [Codage 03.02] huit-dimensions — fonctionnalités 006, 007, 008 (**open**)
- [#68](https://github.com/Tradition-Learning-Community/tllib/issues/68) — [Codage 03.03] huit-dimensions — fonctionnalités 009, 010, 011 (**open**)
- [#69](https://github.com/Tradition-Learning-Community/tllib/issues/69) — [Codage 03.04] huit-dimensions — fonctionnalités 012, 013 (**open**)
- [#70](https://github.com/Tradition-Learning-Community/tllib/issues/70) — [Codage 04.01] invariants — fonctionnalités 001, 002 (**open**)
- [#71](https://github.com/Tradition-Learning-Community/tllib/issues/71) — [Codage 04.02] invariants — fonctionnalités 003, 004 (**open**)
- [#72](https://github.com/Tradition-Learning-Community/tllib/issues/72) — [Codage 04.03] invariants — fonctionnalités 005, 006, 007 (**open**)
- [#73](https://github.com/Tradition-Learning-Community/tllib/issues/73) — [Codage 04.04] invariants — fonctionnalités 008, 009 (**open**)
- [#74](https://github.com/Tradition-Learning-Community/tllib/issues/74) — [Codage 04.05] invariants — fonctionnalités 010 (**open**)
- [#75](https://github.com/Tradition-Learning-Community/tllib/issues/75) — [Codage 05.01] dynamics — fonctionnalités 001, 002, 003 (**open**)
- [#76](https://github.com/Tradition-Learning-Community/tllib/issues/76) — [Codage 05.02] dynamics — fonctionnalités 004, 005, 006 (**open**)
- [#77](https://github.com/Tradition-Learning-Community/tllib/issues/77) — [Codage 05.03] dynamics — fonctionnalités 007 (**open**)
- [#78](https://github.com/Tradition-Learning-Community/tllib/issues/78) — [Codage 06.01] theorems — fonctionnalités 001, 002, 003, 004 (**open**)
- [#79](https://github.com/Tradition-Learning-Community/tllib/issues/79) — [Codage 06.02] theorems — fonctionnalités 005, 006, 007 (**open**)
- [#80](https://github.com/Tradition-Learning-Community/tllib/issues/80) — [Codage 06.03] theorems — fonctionnalités 008, 009 (**open**)
- [#81](https://github.com/Tradition-Learning-Community/tllib/issues/81) — [Codage 07.01] message — fonctionnalités 001, 002, 003 (**open**)
- [#82](https://github.com/Tradition-Learning-Community/tllib/issues/82) — [Codage 07.02] message — fonctionnalités 004, 005, 006 (**open**)
- [#83](https://github.com/Tradition-Learning-Community/tllib/issues/83) — [Codage 08.01] principle — fonctionnalités 001, 002, 003 (**open**)
- [#84](https://github.com/Tradition-Learning-Community/tllib/issues/84) — [Codage 08.02] principle — fonctionnalités 004, 005, 006 (**open**)
- [#85](https://github.com/Tradition-Learning-Community/tllib/issues/85) — [Codage 08.03] principle — fonctionnalités 007, 008, 010 (**open**)
- [#86](https://github.com/Tradition-Learning-Community/tllib/issues/86) — [Codage 08.04] principle — fonctionnalités 011 (**open**)
- [#87](https://github.com/Tradition-Learning-Community/tllib/issues/87) — [Codage 09.01] values — fonctionnalités 001, 003, 004, 005 (**open**)
- [#88](https://github.com/Tradition-Learning-Community/tllib/issues/88) — [Codage 09.02] values — fonctionnalités 006, 007, 008, 009 (**open**)
- [#89](https://github.com/Tradition-Learning-Community/tllib/issues/89) — [Codage 09.03] values — fonctionnalités 010, 011, 012, 013 (**open**)
- [#90](https://github.com/Tradition-Learning-Community/tllib/issues/90) — [Codage 09.04] values — fonctionnalités 014, 018 (**open**)
- [#91](https://github.com/Tradition-Learning-Community/tllib/issues/91) — [Codage 10.01] virtues — fonctionnalités 001, 002, 005 (**open**)
- [#92](https://github.com/Tradition-Learning-Community/tllib/issues/92) — [Codage 10.02] virtues — fonctionnalités 006, 007, 008 (**open**)
- [#93](https://github.com/Tradition-Learning-Community/tllib/issues/93) — [Codage 10.03] virtues — fonctionnalités 009, 010, 011 (**open**)
- [#94](https://github.com/Tradition-Learning-Community/tllib/issues/94) — [Codage 10.04] virtues — fonctionnalités 014 (**open**)
- [#95](https://github.com/Tradition-Learning-Community/tllib/issues/95) — [Codage 11.01] capacities — fonctionnalités 001, 002 (**open**)
- [#96](https://github.com/Tradition-Learning-Community/tllib/issues/96) — [Codage 11.02] capacities — fonctionnalités 003, 005 (**open**)
- [#97](https://github.com/Tradition-Learning-Community/tllib/issues/97) — [Codage 11.03] capacities — fonctionnalités 006, 007 (**open**)
- [#98](https://github.com/Tradition-Learning-Community/tllib/issues/98) — [Codage 11.04] capacities — fonctionnalités 008, 009, 010 (**open**)
- [#99](https://github.com/Tradition-Learning-Community/tllib/issues/99) — [Codage 11.05] capacities — fonctionnalités 011, 012, 013 (**open**)
- [#100](https://github.com/Tradition-Learning-Community/tllib/issues/100) — [Codage 11.06] capacities — fonctionnalités 014, 015, 018 (**open**)
- [#101](https://github.com/Tradition-Learning-Community/tllib/issues/101) — [Codage 12.01] competencies — fonctionnalités 001, 002 (**open**)
- [#102](https://github.com/Tradition-Learning-Community/tllib/issues/102) — [Codage 12.02] competencies — fonctionnalités 004, 005 (**open**)
- [#103](https://github.com/Tradition-Learning-Community/tllib/issues/103) — [Codage 12.03] competencies — fonctionnalités 006, 007 (**open**)
- [#104](https://github.com/Tradition-Learning-Community/tllib/issues/104) — [Codage 12.04] competencies — fonctionnalités 008, 009 (**open**)
- [#105](https://github.com/Tradition-Learning-Community/tllib/issues/105) — [Codage 12.05] competencies — fonctionnalités 010, 011 (**open**)
- [#106](https://github.com/Tradition-Learning-Community/tllib/issues/106) — [Codage 12.06] competencies — fonctionnalités 012, 013 (**open**)
- [#107](https://github.com/Tradition-Learning-Community/tllib/issues/107) — [Codage 12.07] competencies — fonctionnalités 016 (**open**)
- [#108](https://github.com/Tradition-Learning-Community/tllib/issues/108) — [Codage 13.01] practice — fonctionnalités 001, 003, 004 (**open**)
- [#109](https://github.com/Tradition-Learning-Community/tllib/issues/109) — [Codage 13.02] practice — fonctionnalités 005, 006, 007 (**open**)
- [#110](https://github.com/Tradition-Learning-Community/tllib/issues/110) — [Codage 13.03] practice — fonctionnalités 008, 009, 010 (**open**)
- [#111](https://github.com/Tradition-Learning-Community/tllib/issues/111) — [Codage 13.04] practice — fonctionnalités 012 (**open**)
- [#112](https://github.com/Tradition-Learning-Community/tllib/issues/112) — [Codage 14.01] lived-experience — fonctionnalités 001, 002, 004 (**open**)
- [#113](https://github.com/Tradition-Learning-Community/tllib/issues/113) — [Codage 14.02] lived-experience — fonctionnalités 005, 006, 007 (**open**)
- [#114](https://github.com/Tradition-Learning-Community/tllib/issues/114) — [Codage 14.03] lived-experience — fonctionnalités 008, 009, 010 (**open**)
- [#115](https://github.com/Tradition-Learning-Community/tllib/issues/115) — [Codage 14.04] lived-experience — fonctionnalités 011, 012, 013 (**open**)
- [#116](https://github.com/Tradition-Learning-Community/tllib/issues/116) — [Codage 15.01] relations — fonctionnalités 002, 003 (**open**)
- [#117](https://github.com/Tradition-Learning-Community/tllib/issues/117) — [Codage 15.02] relations — fonctionnalités 004, 007 (**open**)
- [#118](https://github.com/Tradition-Learning-Community/tllib/issues/118) — [Codage 15.03] relations — fonctionnalités 008 (**open**)
- [#119](https://github.com/Tradition-Learning-Community/tllib/issues/119) — [Codage 16.01] cohort — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#120](https://github.com/Tradition-Learning-Community/tllib/issues/120) — [Codage 16.02] cohort — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#121](https://github.com/Tradition-Learning-Community/tllib/issues/121) — [Codage 16.03] cohort — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#122](https://github.com/Tradition-Learning-Community/tllib/issues/122) — [Codage 16.04] cohort — fonctionnalités 016, 017 (**open**)
- [#123](https://github.com/Tradition-Learning-Community/tllib/issues/123) — [Codage 23.01] memory — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#124](https://github.com/Tradition-Learning-Community/tllib/issues/124) — [Codage 23.02] memory — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#125](https://github.com/Tradition-Learning-Community/tllib/issues/125) — [Codage 22.01] temporality — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#126](https://github.com/Tradition-Learning-Community/tllib/issues/126) — [Codage 22.02] temporality — fonctionnalités 006, 007, 008, 009 (**open**)
- [#127](https://github.com/Tradition-Learning-Community/tllib/issues/127) — [Codage 26.01] identity — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#128](https://github.com/Tradition-Learning-Community/tllib/issues/128) — [Codage 26.02] identity — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#129](https://github.com/Tradition-Learning-Community/tllib/issues/129) — [Codage 26.03] identity — fonctionnalités 011, 012, 013 (**open**)
- [#130](https://github.com/Tradition-Learning-Community/tllib/issues/130) — [Codage 24.01] context — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#131](https://github.com/Tradition-Learning-Community/tllib/issues/131) — [Codage 24.02] context — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#132](https://github.com/Tradition-Learning-Community/tllib/issues/132) — [Codage 24.03] context — fonctionnalités 011, 012 (**open**)
- [#133](https://github.com/Tradition-Learning-Community/tllib/issues/133) — [Codage 25.01] culture — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#134](https://github.com/Tradition-Learning-Community/tllib/issues/134) — [Codage 25.02] culture — fonctionnalités 006, 007, 008 (**open**)
- [#135](https://github.com/Tradition-Learning-Community/tllib/issues/135) — [Codage 27.01] reflexivity — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#136](https://github.com/Tradition-Learning-Community/tllib/issues/136) — [Codage 27.02] reflexivity — fonctionnalités 006, 007, 008, 009 (**open**)
- [#137](https://github.com/Tradition-Learning-Community/tllib/issues/137) — [Codage 18.01] evaluation — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#138](https://github.com/Tradition-Learning-Community/tllib/issues/138) — [Codage 18.02] evaluation — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#139](https://github.com/Tradition-Learning-Community/tllib/issues/139) — [Codage 18.03] evaluation — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#140](https://github.com/Tradition-Learning-Community/tllib/issues/140) — [Codage 18.04] evaluation — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#141](https://github.com/Tradition-Learning-Community/tllib/issues/141) — [Codage 19.01] regulation — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#142](https://github.com/Tradition-Learning-Community/tllib/issues/142) — [Codage 19.02] regulation — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#143](https://github.com/Tradition-Learning-Community/tllib/issues/143) — [Codage 19.03] regulation — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#144](https://github.com/Tradition-Learning-Community/tllib/issues/144) — [Codage 19.04] regulation — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#145](https://github.com/Tradition-Learning-Community/tllib/issues/145) — [Codage 21.01] fairness — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#146](https://github.com/Tradition-Learning-Community/tllib/issues/146) — [Codage 21.02] fairness — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#147](https://github.com/Tradition-Learning-Community/tllib/issues/147) — [Codage 21.03] fairness — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#148](https://github.com/Tradition-Learning-Community/tllib/issues/148) — [Codage 21.04] fairness — fonctionnalités 016, 017, 018 (**open**)
- [#149](https://github.com/Tradition-Learning-Community/tllib/issues/149) — [Codage 20.01] robustness — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#150](https://github.com/Tradition-Learning-Community/tllib/issues/150) — [Codage 20.02] robustness — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#151](https://github.com/Tradition-Learning-Community/tllib/issues/151) — [Codage 20.03] robustness — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#152](https://github.com/Tradition-Learning-Community/tllib/issues/152) — [Codage 20.04] robustness — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#153](https://github.com/Tradition-Learning-Community/tllib/issues/153) — [Codage 20.05] robustness — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#154](https://github.com/Tradition-Learning-Community/tllib/issues/154) — [Codage 20.06] robustness — fonctionnalités 026, 027, 028, 029, 030 (**open**)
- [#155](https://github.com/Tradition-Learning-Community/tllib/issues/155) — [Codage 20.07] robustness — fonctionnalités 031, 032, 033, 034, 035 (**open**)
- [#156](https://github.com/Tradition-Learning-Community/tllib/issues/156) — [Codage 35.01] fidelity-to-invariant-core — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#157](https://github.com/Tradition-Learning-Community/tllib/issues/157) — [Codage 35.02] fidelity-to-invariant-core — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#158](https://github.com/Tradition-Learning-Community/tllib/issues/158) — [Codage 35.03] fidelity-to-invariant-core — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#159](https://github.com/Tradition-Learning-Community/tllib/issues/159) — [Codage 35.04] fidelity-to-invariant-core — fonctionnalités 016, 017, 018 (**open**)
- [#160](https://github.com/Tradition-Learning-Community/tllib/issues/160) — [Codage 32.01] drift-and-correction — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#161](https://github.com/Tradition-Learning-Community/tllib/issues/161) — [Codage 32.02] drift-and-correction — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#162](https://github.com/Tradition-Learning-Community/tllib/issues/162) — [Codage 32.03] drift-and-correction — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#163](https://github.com/Tradition-Learning-Community/tllib/issues/163) — [Codage 32.04] drift-and-correction — fonctionnalités 016, 017, 018 (**open**)
- [#164](https://github.com/Tradition-Learning-Community/tllib/issues/164) — [Codage 28.01] finality-and-evolutionary-teleology — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#165](https://github.com/Tradition-Learning-Community/tllib/issues/165) — [Codage 28.02] finality-and-evolutionary-teleology — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#166](https://github.com/Tradition-Learning-Community/tllib/issues/166) — [Codage 28.03] finality-and-evolutionary-teleology — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#167](https://github.com/Tradition-Learning-Community/tllib/issues/167) — [Codage 28.04] finality-and-evolutionary-teleology — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#168](https://github.com/Tradition-Learning-Community/tllib/issues/168) — [Codage 28.05] finality-and-evolutionary-teleology — fonctionnalités 021, 022 (**open**)
- [#169](https://github.com/Tradition-Learning-Community/tllib/issues/169) — [Codage 29.01] generational-propagation — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#170](https://github.com/Tradition-Learning-Community/tllib/issues/170) — [Codage 29.02] generational-propagation — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#171](https://github.com/Tradition-Learning-Community/tllib/issues/171) — [Codage 29.03] generational-propagation — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#172](https://github.com/Tradition-Learning-Community/tllib/issues/172) — [Codage 29.04] generational-propagation — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#173](https://github.com/Tradition-Learning-Community/tllib/issues/173) — [Codage 29.05] generational-propagation — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#174](https://github.com/Tradition-Learning-Community/tllib/issues/174) — [Codage 29.06] generational-propagation — fonctionnalités 026, 027, 028 (**open**)
- [#175](https://github.com/Tradition-Learning-Community/tllib/issues/175) — [Codage 30.01] expansion — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#176](https://github.com/Tradition-Learning-Community/tllib/issues/176) — [Codage 30.02] expansion — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#177](https://github.com/Tradition-Learning-Community/tllib/issues/177) — [Codage 30.03] expansion — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#178](https://github.com/Tradition-Learning-Community/tllib/issues/178) — [Codage 30.04] expansion — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#179](https://github.com/Tradition-Learning-Community/tllib/issues/179) — [Codage 30.05] expansion — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#180](https://github.com/Tradition-Learning-Community/tllib/issues/180) — [Codage 30.06] expansion — fonctionnalités 026, 027, 028, 029 (**open**)
- [#181](https://github.com/Tradition-Learning-Community/tllib/issues/181) — [Codage 31.01] institutionalization — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#182](https://github.com/Tradition-Learning-Community/tllib/issues/182) — [Codage 31.02] institutionalization — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#183](https://github.com/Tradition-Learning-Community/tllib/issues/183) — [Codage 31.03] institutionalization — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#184](https://github.com/Tradition-Learning-Community/tllib/issues/184) — [Codage 31.04] institutionalization — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#185](https://github.com/Tradition-Learning-Community/tllib/issues/185) — [Codage 31.05] institutionalization — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#186](https://github.com/Tradition-Learning-Community/tllib/issues/186) — [Codage 31.06] institutionalization — fonctionnalités 026, 027, 028, 029, 030 (**open**)
- [#187](https://github.com/Tradition-Learning-Community/tllib/issues/187) — [Codage 31.07] institutionalization — fonctionnalités 031, 032, 033, 034, 035 (**open**)
- [#188](https://github.com/Tradition-Learning-Community/tllib/issues/188) — [Codage 31.08] institutionalization — fonctionnalités 036, 037 (**open**)
- [#189](https://github.com/Tradition-Learning-Community/tllib/issues/189) — [Codage 17.01] cascade-transmission — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#190](https://github.com/Tradition-Learning-Community/tllib/issues/190) — [Codage 17.02] cascade-transmission — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#191](https://github.com/Tradition-Learning-Community/tllib/issues/191) — [Codage 17.03] cascade-transmission — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#192](https://github.com/Tradition-Learning-Community/tllib/issues/192) — [Codage 17.04] cascade-transmission — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#193](https://github.com/Tradition-Learning-Community/tllib/issues/193) — [Codage 17.05] cascade-transmission — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#194](https://github.com/Tradition-Learning-Community/tllib/issues/194) — [Codage 17.06] cascade-transmission — fonctionnalités 026, 027, 028, 029, 030 (**open**)
- [#195](https://github.com/Tradition-Learning-Community/tllib/issues/195) — [Codage 17.07] cascade-transmission — fonctionnalités 031, 032, 033, 034, 035 (**open**)
- [#196](https://github.com/Tradition-Learning-Community/tllib/issues/196) — [Codage 17.08] cascade-transmission — fonctionnalités 036, 037, 038, 039, 040 (**open**)
- [#197](https://github.com/Tradition-Learning-Community/tllib/issues/197) — [Codage 17.09] cascade-transmission — fonctionnalités 041, 042, 043, 044, 045 (**open**)
- [#198](https://github.com/Tradition-Learning-Community/tllib/issues/198) — [Codage 17.10] cascade-transmission — fonctionnalités 046, 047, 048, 049, 050 (**open**)
- [#199](https://github.com/Tradition-Learning-Community/tllib/issues/199) — [Codage 17.11] cascade-transmission — fonctionnalités 051, 052, 053, 054, 055 (**open**)
- [#200](https://github.com/Tradition-Learning-Community/tllib/issues/200) — [Codage 17.12] cascade-transmission — fonctionnalités 056, 057, 058, 059, 060 (**open**)
- [#201](https://github.com/Tradition-Learning-Community/tllib/issues/201) — [Codage 17.13] cascade-transmission — fonctionnalités 061, 062, 063, 064 (**open**)
- [#202](https://github.com/Tradition-Learning-Community/tllib/issues/202) — [Codage 34.01] transmission-lifecycle — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#203](https://github.com/Tradition-Learning-Community/tllib/issues/203) — [Codage 34.02] transmission-lifecycle — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#204](https://github.com/Tradition-Learning-Community/tllib/issues/204) — [Codage 34.03] transmission-lifecycle — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#205](https://github.com/Tradition-Learning-Community/tllib/issues/205) — [Codage 34.04] transmission-lifecycle — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#206](https://github.com/Tradition-Learning-Community/tllib/issues/206) — [Codage 34.05] transmission-lifecycle — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#207](https://github.com/Tradition-Learning-Community/tllib/issues/207) — [Codage 34.06] transmission-lifecycle — fonctionnalités 026, 027, 028, 029, 030 (**open**)
- [#208](https://github.com/Tradition-Learning-Community/tllib/issues/208) — [Codage 34.07] transmission-lifecycle — fonctionnalités 031, 032, 033, 034, 035 (**open**)
- [#209](https://github.com/Tradition-Learning-Community/tllib/issues/209) — [Codage 34.08] transmission-lifecycle — fonctionnalités 036, 037, 038, 039, 040 (**open**)
- [#210](https://github.com/Tradition-Learning-Community/tllib/issues/210) — [Codage 34.09] transmission-lifecycle — fonctionnalités 041, 042, 043, 044, 045 (**open**)
- [#211](https://github.com/Tradition-Learning-Community/tllib/issues/211) — [Codage 34.10] transmission-lifecycle — fonctionnalités 046, 047, 048, 049, 050 (**open**)
- [#212](https://github.com/Tradition-Learning-Community/tllib/issues/212) — [Codage 34.11] transmission-lifecycle — fonctionnalités 051, 052, 053, 054, 055 (**open**)
- [#213](https://github.com/Tradition-Learning-Community/tllib/issues/213) — [Codage 34.12] transmission-lifecycle — fonctionnalités 056, 057, 058, 059, 060 (**open**)
- [#214](https://github.com/Tradition-Learning-Community/tllib/issues/214) — [Codage 34.13] transmission-lifecycle — fonctionnalités 061, 062, 063, 064, 065 (**open**)
- [#215](https://github.com/Tradition-Learning-Community/tllib/issues/215) — [Codage 34.14] transmission-lifecycle — fonctionnalités 066, 067, 068, 069, 070 (**open**)
- [#216](https://github.com/Tradition-Learning-Community/tllib/issues/216) — [Codage 34.15] transmission-lifecycle — fonctionnalités 071, 072, 073, 074, 075 (**open**)
- [#217](https://github.com/Tradition-Learning-Community/tllib/issues/217) — [Codage 34.16] transmission-lifecycle — fonctionnalités 076, 077, 078, 079, 080 (**open**)
- [#218](https://github.com/Tradition-Learning-Community/tllib/issues/218) — [Codage 34.17] transmission-lifecycle — fonctionnalités 081, 082, 083, 084, 085 (**open**)
- [#219](https://github.com/Tradition-Learning-Community/tllib/issues/219) — [Codage 34.18] transmission-lifecycle — fonctionnalités 086, 087, 088, 089, 090 (**open**)
- [#220](https://github.com/Tradition-Learning-Community/tllib/issues/220) — [Codage 34.19] transmission-lifecycle — fonctionnalités 091, 092, 093, 094, 095 (**open**)
- [#221](https://github.com/Tradition-Learning-Community/tllib/issues/221) — [Codage 34.20] transmission-lifecycle — fonctionnalités 096, 097, 098, 099, 100 (**open**)
- [#222](https://github.com/Tradition-Learning-Community/tllib/issues/222) — [Codage 34.21] transmission-lifecycle — fonctionnalités 101, 102, 103, 104, 105 (**open**)
- [#223](https://github.com/Tradition-Learning-Community/tllib/issues/223) — [Codage 34.22] transmission-lifecycle — fonctionnalités 106, 107, 108, 109 (**open**)
- [#224](https://github.com/Tradition-Learning-Community/tllib/issues/224) — [Codage 33.01] low-data-architecture — fonctionnalités 001, 002, 003, 004, 005 (**open**)
- [#225](https://github.com/Tradition-Learning-Community/tllib/issues/225) — [Codage 33.02] low-data-architecture — fonctionnalités 006, 007, 008, 009, 010 (**open**)
- [#226](https://github.com/Tradition-Learning-Community/tllib/issues/226) — [Codage 33.03] low-data-architecture — fonctionnalités 011, 012, 013, 014, 015 (**open**)
- [#227](https://github.com/Tradition-Learning-Community/tllib/issues/227) — [Codage 33.04] low-data-architecture — fonctionnalités 016, 017, 018, 019, 020 (**open**)
- [#228](https://github.com/Tradition-Learning-Community/tllib/issues/228) — [Codage 33.05] low-data-architecture — fonctionnalités 021, 022, 023, 024, 025 (**open**)
- [#229](https://github.com/Tradition-Learning-Community/tllib/issues/229) — [Codage 33.06] low-data-architecture — fonctionnalités 026, 027, 028, 029, 030 (**open**)
- [#230](https://github.com/Tradition-Learning-Community/tllib/issues/230) — [Codage 33.07] low-data-architecture — fonctionnalités 031, 032 (**open**)

## Fermées / historiques

- #1 — [SUPERSEDED] [Fondation] Finaliser l’architecture modulaire et les règles de dépendance (**closed**)
- #2 — [SUPERSEDED] [Fondation] Configurer l’environnement de développement, la qualité et la CI (**closed**)
- #3 — [SUPERSEDED] [Spécifications] Épingler et vérifier la version consommée de tllib-specs (**closed**)
- #4 — [SUPERSEDED] [Cœur] Concevoir les identifiants, statuts, résultats et erreurs communes (**closed**)
- #5 — [SUPERSEDED] [Contrats partagés] Implémenter les 8 contrats structurels de tllib-specs (**closed**)
- #6 — [SUPERSEDED] [Fournisseurs] Concevoir l’injection des capacités externes et conditionnelles (**closed**)
- #7 — [SUPERSEDED] [Conformité] Charger les bundles et exécuter les critères d’acceptation (**closed**)
- #8 — [SUPERSEDED] [Catalogue runtime] Créer le registre des domaines et fonctionnalités (**closed**)
- #9 — [SUPERSEDED] [Synchronisation] Détecter les évolutions de tllib-specs et générer le backlog (**closed**)
- #263 — [Legal/Contributors V1] Décider et publier la licence du code tllib avant contributions (**closed**)

## Décision de triage

- **Ne pas fermer les fondations restantes par simple publication de politiques.** Il faut des artefacts C++/Python/outillage et des tests réels.
- **Ne pas rouvrir le travail général de tllib-specs.** Seules les ambiguïtés ciblées changent le snapshot via son processus normatif.
- **Ne pas transformer les 36 epics ni les 178 lots en pseudo-fondations** : leurs TLC-FC et découpage restent inchangés.
- **Ne pas interpréter les 249 issues ouvertes comme 249 décisions en suspens :** 214 sont des conteneurs ou lots de domaines, cinq sont epics de coordination, une est blocker scientifique, et les autres sont des issues transversales/fondations.
- **Éviter de surcharger la CI en phase pré-implémentation.** Les tests locaux sur cibles réelles sont prioritaires.

## Règle d'ouverture aux contributeurs

Une issue de lot peut devenir ready lorsque ses interfaces transverses utiles sont installées et testées, ses exigences scientifiques publiées et non ambiguës, ses fixtures/conformance déterminées, ses dépendances satisfaites, et son reviewer identifié. Ne pas attendre le packaging/release V1 pour tous les lots ; ne pas permettre non plus que des contributeurs écrivent les ports communs à la place de la fondation.
