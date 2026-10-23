# ADR-005 — Arrays, mémoire et interop

**Statut : direction acceptée ; API détaillée après inventaire et tests.**

- Pas de nouvel ndarray généraliste tllib.
- Si requis par le catalogue : vue native minimale data/handle, dtype,
  shape, strides, device, constness, lifetime ; ownership non implicite.
- NumPy/buffer protocol côté Python ; DLPack lorsque justifié.
- Zéro copie seulement si layout/aliasing/ownership/lifetime compatibles,
  copie explicite et observable sinon.
- Backends numériques choisis après inventaire traçable des 36 domaines.
- Aucun critère de précision, tolérance ou dimension scientifique inventé.
- Voir `docs/v1/ARRAYS-NUMERICS-CONTRACT.md` et #250–#253.
