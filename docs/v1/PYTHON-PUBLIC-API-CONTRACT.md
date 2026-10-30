# Contrat transversal V1 — API Python et parité (#258)

**Statut : décision d'architecture normative pour le logiciel.** Source de vérité scientifique : le handoff immuable de tllib-specs. Ce document spécifie les conventions de la *façade*, pas une science nouvelle. Aucun binder ou code de domaine n'est laissé à choisir par les contributeurs.

## Arborescence et conventions

- Paquet importable `tllib` ; extension native interne `tllib._native` (nom logique, emplacement exact géré par #257). Les sous-modules publics futurs sont explicitement déclarés ; aucun import wildcard ni auto-enregistrement.
- Classes/énumérations publiques : `PascalCase` ; fonctions, méthodes, paramètres : `snake_case` ; constantes : `UPPER_SNAKE_CASE`. Les noms ne transforment ni identifiants TLC-FC ni obligations normatives.
- Toutes les fonctions publiques sont typées, documentées et couvertes par des stubs `.pyi` / `py.typed` livrés avec la wheel ; le package ne dépend pas de Python au runtime C++.
- Toute nouvelle exposition a une correspondance traçable vers le symbole C++ ou une justification `helper non normatif`. Les fonctions Python de confort peuvent gérer des structures, itérateurs, configuration et messages ; elles n'implémentent aucune équation normative, dispatcher ou règle de conformité.
- Le code public n'expose pas les références empruntées si leur propriétaire natif peut mourir avant la vue Python ; les champs immuables sont préférés aux handles non stables.

## Conversions normées pour toutes les features

| C++ | Python | Règle |
| --- | --- | --- |
| `FeatureId`, `DomainId` | objets typés comparables/hashables | conserver identifiant original sans normalisation |
| enums de statut publiés | `enum.Enum` / type exporté | ensemble fermé selon le snapshot, valeur inconnue refusée ou représentée explicitement comme inconnue selon contrat |
| value objects invariants | classes natives exposées en lecture | égalité et sérialisation conformes au C++ |
| `Result<T>` réussi | valeur native / objet Python équivalent | aucune wrapper `Result` nécessaire à l'utilisateur ; résultat typé |
| `Result<T>` erreur attendue | `TllibError` et sous-classes stables | préserver code, TLC-FC, provenance, contexte sans string parsing |
| `not implemented`/structural/conditional | erreur stable dédiée | **ne jamais** retourner `None` ou un résultat scientifique fictif |
| vues/buffers | NumPy/buffer/DLPack suivant #252 | copie/zero-copy annoncés ; lifetime et mutabilité préservés |
| optional | `None` seulement si optional explicite | `None` jamais substitut à `unresolved` |

## Erreurs publiques

Racine `TllibError(Exception)` avec attributs readonly `code`, `feature_id` (optionnel), `specs_provenance` (optionnel), `context` structuré et sans secret. Sous-classes convenues : `ValidationError`, `FeatureUnavailableError`, `ProviderRequiredError`, `ProviderExecutionError`, `IncompatibleSpecsError`, `CancelledError`, `IndeterminateOutcomeError`. Le numéro/code interne demeure la valeur faisant autorité pour les comparaisons ; les messages sont descriptifs et peuvent être localisés. Les noms ici désignent des **catégories logicielles**, non de nouveaux statuts scientifiques du catalogue. Le mapping exact des codes natifs est centralisé dans `set_error` du pont natif, testé en #258 ; les codes et contextes sont dérivés de `Error` et de `stable_code`, jamais des messages. Le champ `category` explicite la catégorie logicielle.

## Parité reproductible

Pour chaque comportement exposé : mêmes entrées et mêmes spécifications verrouillées ; comparer sortie C++ / sortie Python en représentation canonique ou selon un oracle conforme ; comparer erreurs structurées et états des providers ; tester invalides/limites, ownership, cancellation, copies. Une différence de tolérance ne peut être acceptée sans obligation normative ou démonstration numérique contrôlée. Tests `parity` pilotés par un manifeste machine-readable de correspondance API-symboles/TLC-FC et non par une liste copiée manuellement. Le harness de parité structurelle a été effectivement construit et testé en #258 : `tests/parity/manifest.json`, `identity_cli.cpp` et `test_parity.py`, avec entrées positives et invalides, et API/stubs vérifiés. La parité scientifique des TLC-FC ne sera vérifiée que lors de chaque implémentation réelle.

## Concurrence

Les wrappers C++ ne relâchent le GIL que sur chemins natifs prouvés sûrs ; callbacks Python reprennent les contraintes GIL, durée de vie et réentrance. Free-threading et stable ABI sont expérimentaux jusqu'aux preuves #256/#259. Un provider Python n'est jamais exécuté depuis un destructeur C++ ou sous lock interne du runtime.

## Critère de clôture #258

Ce document fixe les conventions de tous les domaines. les stubs, le mapping Error/Result effectif et le harness commun ont été testés en PR #277. Aucun test de domaine scientifique n'est revendiqué. Aucun domaine ne doit concevoir son propre mapping.
