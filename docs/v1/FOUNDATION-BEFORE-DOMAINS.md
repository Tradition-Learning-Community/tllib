# Gate obligatoire — fondations communes avant les 36 domaines

## Décision

Le dépôt `tllib-specs` est **amont finalisé pour le snapshot ciblé** :
on ne lui demande pas de nouveau travail de préparation général.
Seules des contradictions normatives précises sont reportées en amont
(comme `TLC-FC-30-EXPANSION-014`). Les contributeurs des 36 domaines
ne définissent pas l'architecture commune : elle est livrée par des
issues de fondation dans `tllib`.

## Propriétaire des décisions / livrables communs

| Groupe | Issues | Résultat commun à livrer **avant** lots |
| --- | --- | --- |
| Architecture C++ et API/erreurs | #235, #246, #247, #248, #249 | headers, invariants, build et consommateur externe réels |
| Formats scientifiques partagés | #237, #254, #255, #244 | 8 contrats partagés, snapshot lock vérifié, codegen metadata, diff |
| Registry/concurrence/providers | #238, #239, #259 | ports native/runtime, registry, cancellation, adapter Python commun |
| Données, interop, numérique | #250, #251, #252, #253 | inventaire tracé, ArrayView si prouvée, NumPy/DLPack, backends justifiés |
| Python | #256, #257, #258 | binder démontré, wheel, conventions API, typing, harness de parité |
| Conformité/qualité/sécurité | #241, #243, #13, #14 | moteur de rapport de conformance, tests centraux, compatibilité, gates ciblés |
| Expérience contribution | #51, #261, #10 | issues triées, guide testé, parcours et documentations fiables |
| Release (ultérieure) | #11, #12 | artefacts/smoke tests complets, baseline performance |

La **documentation seule** d'un contrat n'est pas une preuve de
`Result/Error`, des bindings, de CTest, des providers ou de la
conformance. L'issue de fondation demeure ouverte jusqu'à preuve
technique exécutée, mais elle est affectée à une équipe de fondation,
**jamais déléguée comme décision au contributeur de domaine**.

## Conditions d'ouverture d'un lot

Un lot est `status:ready` seulement lorsque les ports communs
nécessaires existent et passent leurs tests, que les obligations et
erreurs publiées du snapshot sont suffisamment définies, que la
capability et le niveau de support sont explicites, et qu'un
contributeur peut écrire uniquement le comportement spécifique
TLC-FC et ses acceptations. Le projet fournit les interfaces,
prototypes, tests génériques et instructions installables.
Les blockers scientifiques ne concernent que la fonctionnalité
touchée ; ne pas bloquer tous les lots du domaine par propagation
administrative.

## Discipline de décision

- Aucun contributeur ne choisit nanobind/pybind11, `Result/Error`,
  sérialisation, `ArrayView`, registry, provider, CI ou politique de
  release dans son lot fonctionnel.
- Les décisions de type `policy` sont revues une fois, versionnées
  et référencées par issue/ADR ; les composants partagés sont testés
  une seule fois dans des targets réutilisables, et les domaines
  réutilisent sans forks.
- Les issues de fondation suivent l'ordre de dépendance, pas
  une fermeture artificielle en masse. Un épic n'est pas un test.
- La CI grandit avec le code réel ; aucune matrice cartésienne
  en pré-implémentation.
