# ADR-006 — Runtime, registry, providers et dispatch

**Statut : accepté.**

- registry explicite et déterministe.
- chaque TLC-FC connaît statut, version, provenance et implémentation.
- dispatcher sans modification de sémantique.
- ExecutionContext explicite.
- providers injectés par CapabilityId.
- aucun provider scientifique par défaut, aucun réseau caché.
- conception compatible avec une future ABI/plugin dédiée.
