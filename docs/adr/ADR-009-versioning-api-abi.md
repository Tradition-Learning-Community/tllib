# ADR-009 — Versioning, API et ABI

**Statut : accepté comme politique V1.**

- SemVer pour tllib, distinct des versions normatives tllib-specs.
- Support déclaré par paire (commit tllib, SHA/fingerprint specs).
- Stabilité source C++ publique gérée par dépréciation/migration.
- Pas de garantie ABI C++ universelle pendant 0.x ; ABI/plugin stable
  future seulement à frontière explicitement versionnée.
- Python : dépréciations, types, wheels et plateformes publiés
  dans matrice de support.
- Nouveau contrat/TLC-FC specs : revue/diff explicite, jamais
  implémentation présumée.
- Chaque breaking change possède note de migration/release.
- Voir `docs/v1/SECURITY-QUALITY-COMPATIBILITY.md`, #14, #244.
