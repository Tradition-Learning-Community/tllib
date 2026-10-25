# Tâche 1 — Inventaire de données et arbitrage numérique V1

Issues : #250, #253. Snapshot normatif : `Tradition-Learning-Community/tllib-specs@07439babd59c657354e3200ed24c55e2e3eeb72c`.

## Périmètre et preuve de population

Le catalogue `handoff/catalog.json` du snapshot (blob Git `fbe69309402d9f261a16769da62710104f311b11`) a été lu et parsé : **36 domaines, 694 fonctionnalités distinctes, huit contrats structurels**. L'[index TLC-FC](SCIENTIFIC-DATA-TRACEABILITY.md) relie toutes les fonctionnalités aux `contract.json` et `acceptance.json` **dans le dépôt source**. Aucune copie normative n'est maintenue dans `tllib`.

Le modèle publié distingue explicitement les collections `scalar`, `sequence`, `map`, `ordered_map`, `optional`, etc. **`scalar` est une cardinalité/forme de collection et ne signifie pas nombre flottant.** Une séquence opaque ne prouve pas l'existence d'une opération vectorielle. Les représentations source, l'ordre et les contraintes locales doivent être conservés.

## Matrice des besoins établis et limites des preuves

| Constat | Classe | Sources | Implication |
|---|---|---|---|
| Identité TLC-FC, références scientifiques, collections, opaque, erreurs, traçabilité et enveloppes | Normatif structurel | `handoff/README.md`, huit `handoff/shared/` et dépendances du catalogue | Réutiliser les huit contrats, sans inventer de type numérique pour les payloads opaques. |
| Cardinalité, ordre, unicité, relations clés/valeurs lorsqu'ils sont présents | Normatif **local** | `handoff/features/<ID>/contract.json#operations[*].inputs/outputs[*].collection` | Appliquer champ par champ, sans supposer qu'une collection est un tenseur. |
| Contraintes de mutabilité, rétention, durée de vie, copie, allocation, déterminisme | Normatif ou liberté d'implémentation **selon la valeur exacte** | `contract.json#operations[*].runtime_contract` et `determinism` | Respecter `required`, `forbidden`, `implementation_defined`, `not_required`, `not_constrained`, `not_applicable` : ne pas fusionner les états. |
| Traitement opaque sans évaluation numérique | Normatif pour les TLC-FC correspondantes | `TLC-FC-05-DYNAMICS-001/contract.json` : `D001-FOR-001`, `D001-FOR-002`; `acceptance.json` : `DYN-001-OPAQUE-BOUNDARY` | Ne pas calculer les bornes, ni inventer une tolérance ou un solveur. |
| Collections ordonnées, maps de références et payloads opaques | Normatif pour les TLC-FC correspondantes | `TLC-FC-05-DYNAMICS-001/contract.json` (`bounds`), `TLC-FC-11-CAPACITIES-001/contract.json` (`object_payloads`, `provenance`) | Besoin de structures associatives/ordonnées, non de BLAS. |
| Existence globale de matrices denses, tenseurs, sparse, FFT, BLAS/LAPACK, GPU | **Non déterminée par cette revue** | Index 694/694 ; audit exhaustif de contenu encore non réalisé | Ne **pas** transformer l'absence de preuve en preuve d'absence. |
| Dtypes, rank/shape numériques, précision, tolérances, performance chiffrée par fonctionnalité | **Non déterminés globalement** | À examiner pour chaque `contract.json` et `acceptance.json` concernés | Choix différé, aucune valeur par défaut scientifique ajoutée. |

La revue a notamment examiné les champs de contrats de `TLC-FC-00-MASTER-005`, `TLC-FC-05-DYNAMICS-001/002` et `TLC-FC-11-CAPACITIES-001/002`. La **population** 694/694 est vérifiée au niveau catalogue ; l'**audit sémantique** de tous les contrats/acceptations n'est **pas** déclaré effectué. Les extractions intermédiaires antérieures n'ont jamais constitué une validation complète et ne sont pas recopiées ici.

## Évaluation des solutions numériques (#253)

| Candidat | Utilité seulement si… | Coûts/risques à évaluer | Décision V1 |
|---|---|---|---|
| C++20 standard | Opérations de conteneurs, références, contrôle structurel et arithmétique simple suffisent | Précision, overflow et garanties des conteneurs selon contrats | **Base technique existante**, pas un « backend scientifique » garanti. |
| BLAS / LAPACK | Contrat impose ou rend nécessaires algèbre linéaire dense / décomposition | ABI, type entier, licence du fournisseur, reproductibilité/ordre, plateformes, linkage CMake, performance mesurée | **Non retenu à ce stade** ; condition de réexamen : TLC-FC + opération + mesures. |
| Eigen | Besoin démontré de types/opérations matriciels ou solveurs adaptés | Licence et version, compilation/templates, ABI, politiques d'alignement, build et coût d'intégration | **Non retenu à ce stade**. |
| FFT | Transformation fréquentielle exigée par une ou plusieurs TLC-FC | Exactitude, normalisation, licence de la bibliothèque choisie, plateforme et mesures | **Non retenu à ce stade**. |
| Sparse / graphes | Structure creuse ou algorithme de graphe effectivement demandé | Format, ordre d'itération, déterminisme, taille, compatibilité, maintenance | **Non retenu à ce stade** ; références/relations structurées ne prouvent pas sparse numérique. |
| GPU / framework tensoriel | Contrat impose ou performance validée nécessite device/accélération | Drivers, mémoire/lifetime, portabilité, architecture de provider, coûts transitifs | **Non retenu à ce stade**. |

**Décision ferme et limitée : aucune nouvelle dépendance numérique n'est introduite dans le cœur minimal pendant la préparation V1.** Il ne s'agit pas d'affirmer que les 694 contrats n'auront jamais besoin d'un backend : une intégration ultérieure exige une fiche traçable TLC-FC, conformité scientifique, licence SPDX/obligations, maintenance, plateformes, CMake, transitivité, benchmarks reproductibles et caractère opt-in si local. Aucun benchmark de backend n'a été exécuté en l'absence de candidat fondé sur un besoin vérifié.

## Exigences transmises aux tâches d'implémentation

- **#235, #237** : construire uniquement les primitives et huit structures réutilisables nécessaires aux contrats ; conserver exactement identités, erreurs, ordre, opaque et unresolved. Ne pas interpréter scientifiquement les champs.
- **#251** : ne définir `ArrayView`, des dtypes numériques et un propriétaire mémoire que lorsque l'analyse d'un besoin TLC-FC les justifie ; l'ADR-005 interdit un ndarray maison généralisé.
- **#254, #255** : valider ensuite le snapshot et générer métadonnées/liaisons sans remplacer la source normative. Le présent index n'est ni `specs.lock.json` ni un générateur.
- **#253** : rouvrir le dossier de sélection si une fonctionnalité prouve le besoin concret d'une opération numérique non couverte ; évaluer en premier le cœur minimal, puis le backend optionnel.
- **Contributeurs des domaines** : appliquer `contract.json` et `acceptance.json` de l'identifiant, pas les exemples, les noms de domaines ou le présent rapport comme nouvelles normes.

## Contrôles et conclusion

Contrôles réellement observés : accès aux deux dépôts ; SHA `tllib-specs/main` égal au snapshot ; catalogue JSON lu avec 36 domaines, 694 IDs uniques, huit contrats ; index 694 lignes construit à partir des chemins du catalogue. Cohérence vérifiée avec `docs/adr/ADR-002-build-toolchain-and-dependencies.md`, `ADR-005-arrays-memory-interop.md`, `docs/v1/DEPENDENCIES-BUILD-POLICY.md` et `docs/v1/ARRAYS-NUMERICS-CONTRACT.md`.

**Limite bloquante pour la clôture formelle de #250** : les 694 acceptations et contrats n'ont pas été audités un par un sur les besoins numériques. Par conséquent le critère « chaque besoin est relié aux TLC-FC » ne peut pas être certifié exhaustivement ; l'index fournit un accès complet mais ne prouve pas l'absence de besoins non détectés. **#253** doit conserver ouverte toute prétention de sélection définitive sans cet audit et les mesures conditionnelles. En attendant, la règle d'absence de dépendances ajoutées est applicable immédiatement.

Aucun C++, aucune CI/CD et aucune spécification scientifique n'ont été modifiés par ce dossier.
