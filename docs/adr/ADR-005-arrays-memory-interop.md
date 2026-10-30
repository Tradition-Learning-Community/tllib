# ADR-005 — Arrays, mémoire et interop
**Statut : accepté pour la préparation V1 (#251).**

L'inventaire #250 et les décisions #253 montrent des vecteurs courts, des matrices CPU
1D/2D et des carriers structurels, pas un moteur de tenseurs ni un device GPU.
Le cas ordinaire utilise `std::span`, `std::array` et `std::vector` C++20.
Pour les frontières nécessitant des strides, `tllib::core::ArrayView` est une
vue **CPU uniquement**, non-owning, sans allocation de données, pour les rangs 1/2,
avec `int32` et `float64` natifs comme premier ensemble technique
(non une obligation de dtype scientifique). Les strides sont en **octets**.

Le constructeur vérifie rank/shape, débordements, capacité de l'allocation complète,
origine, alignement et indices; il classe row/column/strided. Les buffers stridés
en lecture seule sont admis lorsque l'étendue totale est prouvée. Les vues modifiables
doivent être contiguës (C/F), les vues modifiables stridées et aliasées sont refusées.
Aucun stockage ne retient le propriétaire; l'appelant garantit le lifetime et
l'absence de modification concurrente. L'API ne prévient pas une libération
extérieure et ne rend pas `std::span` propriétaire. Les copies de données sont
hors de cette API, et doivent être explicites dans les adaptateurs de frontière.

Interop Python (#252) : le Python buffer protocol est une frontière à part;
ses `nbytes` logiques ne prouvent pas l'étendue physique d'un slice stridé.
Ne jamais traiter un tel `nbytes` comme la longueur d'une allocation.
Les vues non contiguës sont refusées si l'étendue physique n'est pas attestée.
Interop DLPack / GPU différée : aucune opération scientifique du snapshot
ne l'exige. Pas de nouveau tensor framework.
