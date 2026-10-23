# ADR-009 — Versioning, API et ABI

**Statut : accepté comme politique V1.**

- SemVer pour tllib.
- compatibilité explicite avec tllib-specs.
- stabilité source C++ gérée par dépréciation.
- pas de promesse d'ABI C++ globale pendant 0.x.
- future surface ABI stable restreinte pour plugins/extensions.
- Python suit une politique de dépréciation cohérente.
- toute rupture possède migration et release note.
