# Inventaire des frontières externes V1 — snapshot 07439bab

Source : [catalogue normatif tllib-specs](https://github.com/Tradition-Learning-Community/tllib-specs/blob/07439babd59c657354e3200ed24c55e2e3eeb72c/handoff/catalog.json). Statuts calculés directement depuis les **694** entrées du catalogue ; cette table n'ajoute aucun CapabilityId, provider ni obligation scientifique.

- **36** domaines, **694** fonctionnalités.
- **222** fonctionnalités dont le statut scientifique est `external_provider_required`.
- **237** fonctionnalités dont le statut d'exécution est `conditionally_executable`.
- Les deux statuts ne sont **pas** équivalents. Certaines fonctionnalités structurelles citent un provider non exécutable ; certaines fonctionnalités conditionnelles n'exigent que des opérandes fournis.
- Les capacités et leurs identifiants précis doivent venir des contrats/acceptations de chaque fonctionnalité lors de son implémentation. En absence d'ID normatif, une implémentation doit déclarer explicitement une identité de capability techniquement versionnée, documenter sa correspondance au contrat et interdire la découverte/inférence. Aucun mapping de capability scientifique n'est construit implicitement par le runtime.
- Cette table couvre **les statuts** de tout le catalogue, pas un audit des opérations/providers ligne par ligne. Les numéros indiquent des frontières possibles et **ne certifient aucune implémentation**.

| Domaine | Fonctionnalités | conditionally_executable | external_provider_required | Les deux |
| --- | ---: | ---: | ---: | ---: |
| master | 16 | 9 | 2 | 2 |
| disciple | 10 | 0 | 0 | 0 |
| community | 8 | 0 | 1 | 0 |
| huit-dimensions | 11 | 0 | 0 | 0 |
| invariants | 10 | 0 | 8 | 0 |
| dynamics | 7 | 0 | 2 | 0 |
| theorems | 9 | 0 | 0 | 0 |
| message | 6 | 0 | 1 | 0 |
| principle | 10 | 0 | 2 | 0 |
| values | 14 | 14 | 5 | 5 |
| virtues | 10 | 0 | 0 | 0 |
| capacities | 15 | 0 | 0 | 0 |
| competencies | 13 | 0 | 2 | 0 |
| practice | 10 | 0 | 5 | 0 |
| lived-experience | 12 | 0 | 1 | 0 |
| relations | 5 | 0 | 0 | 0 |
| cohort | 17 | 9 | 0 | 0 |
| memory | 10 | 6 | 0 | 0 |
| temporality | 9 | 4 | 0 | 0 |
| identity | 13 | 7 | 0 | 0 |
| context | 12 | 7 | 5 | 5 |
| culture | 8 | 3 | 3 | 3 |
| reflexivity | 9 | 6 | 3 | 3 |
| evaluation | 20 | 17 | 12 | 12 |
| regulation | 20 | 14 | 13 | 13 |
| fairness | 18 | 12 | 8 | 8 |
| robustness | 35 | 22 | 23 | 22 |
| fidelity-to-invariant-core | 18 | 5 | 9 | 5 |
| drift-and-correction | 18 | 9 | 8 | 8 |
| finality-and-evolutionary-teleology | 22 | 6 | 10 | 5 |
| generational-propagation | 28 | 9 | 11 | 9 |
| expansion | 29 | 13 | 15 | 12 |
| institutionalization | 37 | 12 | 11 | 9 |
| cascade-transmission | 64 | 12 | 18 | 11 |
| transmission-lifecycle | 109 | 20 | 30 | 14 |
| low-data-architecture | 32 | 21 | 14 | 12 |
| **TOTAL** | **694** | **237** | **222** | **158** |

Le registre natif de cette tâche commence vide. Seuls les modèles explicitement inscrits depuis le snapshot verrouillé et validés sont exécutables ; aucune ligne de cet inventaire n'est un enregistrement runtime.
