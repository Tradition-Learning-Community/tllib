# ADR-007 — Snapshot specs, specgen et conformité

**Statut : accepté et implémenté pour le socle du handoff V1.**

- Chaque release tllib cible un SHA immuable de tllib-specs.
- `handoff/catalog.json` fait autorité pour la population dynamique,
  sans plafond codé en dur ; consommation uniquement sous `handoff/`.
- `specs.lock.json` prévu pour SHA complet, version, hash du catalogue
  et méthode vérifiable ; pas de fetch ou update automatique.
- Codegen limité aux structures/métadonnées déterministes, jamais science.
- Artefacts générés utiles au build portent provenance ; deux générations
  indépendantes doivent être byte-identical.
- Nouveau TLC-FC = gap jusqu'à décision explicite ; aucun support implicite.
- Ambiguïté = blocker scientifique dans tllib-specs.
- Voir `docs/v1/SPECS-LOCK-AND-CONFORMANCE.md`, #254/#255.

## Preuves et décisions d'implémentation

- `specs.lock.json` verrouille le snapshot et le SHA-256 du catalogue. `tools/specs_pipeline.py` exige un checkout Git explicitement fourni, valide le lock, les packages, manifest/contract/acceptance/traceability et les dépendances, sans fetch caché.
- `generated/specs/feature_index.json` et `include/tllib/generated/feature_metadata.hpp` sont régénérés de façon déterministe ; le second est inclus par un consommateur CMake externe, sans autoriser d'implémentations runtime implicites.
- `conformance/decisions.json` documente 694 décisions liées au SHA et les rapports de couverture les vérifient intégralement, sans prétendre à 694 implémentations. Le mode `release-gate` refuse les implémentations non prouvées.
- Les preuves d'acceptation exigent un résultat JUnit CTest effectivement réussi et un fichier source de test dans tllib ; aucun package du handoff n'est exécuté. Le workflow ciblé épingle le checkout à un SHA, teste deux générations indépendantes et publie les rapports.
- Détails et commandes dans [SPECS-PIPELINE-IMPLEMENTATION.md](../v1/SPECS-PIPELINE-IMPLEMENTATION.md).
