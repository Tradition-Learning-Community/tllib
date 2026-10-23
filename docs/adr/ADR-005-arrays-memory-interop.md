# ADR-005 — Arrays, mémoire et interop

**Statut : accepté.**

- pas de nouvel ndarray généraliste tllib.
- vue native minimale : data/handle, dtype, shape, strides, device, mutability.
- NumPy/buffer protocol côté Python.
- DLPack lorsque pertinent.
- zéro copie lorsque lifetime/layout le permettent, copie explicite sinon.
- backends numériques choisis après inventaire des 36 domaines.
