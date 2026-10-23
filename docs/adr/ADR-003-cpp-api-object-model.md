# ADR-003 — API C++, modèle objet, erreurs et ownership

**Statut : accepté.**

- POO dès V1, composition/value types avant héritage profond.
- types fondamentaux immuables/invariant-safe.
- polymorphisme seulement aux points de variation réels.
- RAII ; unique_ptr par défaut ; shared_ptr seulement si nécessaire.
- vues non-owning pour données d'entrée.
- erreurs attendues via Result<T> + Error structurée.
- exceptions réservées aux erreurs exceptionnelles/programming failures.
- petite surface publique namespacée ; PImpl possible si utile.
