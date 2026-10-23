# ADR-006 — Runtime, registry, providers et dispatch

**Statut : accepté.**

- Registry déterministe ; chaque TLC-FC avec statut, version, provenance.
- Dispatcher préserve le contrat scientifique.
- ExecutionContext explicite et cancellation coopérative.
- Providers injectés explicitement par CapabilityId ;
  aucun provider scientifique par défaut ni réseau caché.
- Future ABI/plugin à frontière dédiée, non présumée compatible.
- Concurrence : ni pool global caché ni partage sûr par défaut
  d'objets mutables ; contrats par type et par opération.
- Voir `docs/v1/CONCURRENCY-PYTHON-API.md` et #259.
