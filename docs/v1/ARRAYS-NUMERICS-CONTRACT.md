# V1 — Données, ArrayView et qualité numérique

Références : #250, #251, #252, #253, #235 et #236.
**Aucune représentation multidimensionnelle ou backend n'est déclaré
requis par défaut : la preuve vient des 694 packages du snapshot ciblé.**

## Inventaire requis avant de stabiliser l'API

Un tableau de traçabilité maintenu par #250 doit couvrir les 36 domaines
**et chaque TLC-FC concerné**, avec chemin précis vers
`handoff/features/<ID>/contract.json` / `acceptance.json`.
Champs : usage réel (scalaire, séquence, dense, sparse, graphe, temps),
dtypes explicitement permis, dimensions/forme/ordre si normatifs,
contraintes de précision, mutation, sérialisation, ownership, device,
calibrage, opérations et dépendances numériques. Valeur `non_specifie`
signifie **aucune exigence prouvée**, pas « inventer un défaut ».
Les données structurées ne sont pas toutes des tenseurs.

## Contrat d'interface proposé

Si l'inventaire justifie `ArrayView`, commencer par une vue C++ non-owning
minimale et **sans allocation**. Un descriptor distinct précise :
pointeur ou handle non déréférençable directement selon device, types
élémentaires supportés par besoin prouvé, shape, strides **en octets**,
rank, taille, adresse/device (CPU par défaut uniquement si la donnée
est effectivement CPU), constness et validité/lifetime documentés.

Invariants à valider aux frontières : produit de dimensions sans overflow ;
stride/pointeur dans le buffer réellement autorisé ; alignement et
interprétation du dtype ; tableaux vides et strides nuls/negatifs explicités ;
aucun accès hors bornes ni alias mutable non autorisé.
`ArrayView` n'est jamais owner ; un objet propriétaire RAII, quand
nécessaire, maintient la vie mémoire. Un type GPU ne doit pas être exposé
par opportunisme.

NumPy : zéro copie seulement pour dtype/layout/alignement/mutabilité/
lifetime compatibles avec les garanties de la vue et le contrat utilisateur.
Sinon refuser ou réaliser une **copie annoncée et observable** ;
pas de copie silencieuse sous une promesse zéro copie.
DLPack : adopter le protocole officiel uniquement lorsque requis,
avec transfert d'ownership univoque et lifetime testé.
Pas de dépendance NumPy/PyTorch à l'intérieur du cœur C++.

## Calcul numérique et méthode scientifique

- Respecter les unités, domaines, tolérances, ordre et déterminisme
  seulement tels que publiés. Une tolérance par défaut ne crée **jamais**
  une approximation scientifique autorisée.
- Documenter dtype, arrondis, overflow, NaN/Inf, underflow, exactitude,
  non-associativité flottante et décisions de dégradation.
- Ne pas promettre identité bit-à-bit multi-plateforme si le contrat ne
  l'exige pas ; construire des oracles indépendants et des tolérances
  justifiées par contrat/analyse d'erreur, non un seuil opportuniste.
- Quand un RNG existe, graine, état, algorithme, ordre d'échantillonnage
  et traçabilité sont explicités **sans changer la science**.
- BLAS/LAPACK/FFT/sparse retenus uniquement par #253 après preuves,
  benchmarks reproductibles et revue licence/portabilité. Un backend
  différent doit conserver obligations d'acceptation, échec explicite
  sinon ; aucune substitution silencieuse.

## Gates

#250 : inventaire 36/36 avec références TLC-FC, pas une intuition.
#251 : tests natifs des invariants et durées de vie.
#252 : tests NumPy/DLPack, invalides, copies et destructeurs.
#253 : dossier de sélection et benchmark documenté ou conclusion
« aucune dépendance numérique supplémentaire nécessaire » démontrée.
Aucun des quatre n'est clos par ce document seul.
