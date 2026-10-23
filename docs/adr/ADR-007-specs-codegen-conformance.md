# ADR-007 — Snapshot specs, specgen et conformité

**Statut : accepté ; implémentation lock/générateur non encore livrée.**

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
