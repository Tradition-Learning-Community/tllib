# Runtime natif, providers et concurrence V1 — implémentation

Statut : implémentation C++20 de l'infrastructure commune des issues #238 / #259, port providers natif de #239. Autorité scientifique : [tllib-specs@07439bab](https://github.com/Tradition-Learning-Community/tllib-specs/tree/07439babd59c657354e3200ed24c55e2e3eeb72c/handoff). Aucun provider scientifique ni fonctionnalité TLC-FC réelle n'est enregistré dans ce composant.

## Headers et garanties

| API | Thread-safety et propriété |
| --- | --- |
| `core::FeatureId/DomainId/Version/Fingerprint` | Value objects possédés ; lectures concurrentes sur objets non mutés ; C++ ne garantit pas les mutations concurrentes. |
| `runtime::CancellationSource` | `std::stop_source` interne, request_stop sûr depuis plusieurs threads ; token partagé par valeur. |
| `runtime::ExecutionContext` | Par appel, passé par référence const ; ne pas muter options/deadline/executor pendant l'appel. Executor partagé et fourni explicitement par l'appelant, jamais démarré automatiquement. |
| `providers::ProviderRegistry::Builder` | Mutable, **non thread-safe** ; inscriptions uniquement avant freeze. |
| `providers::ProviderRegistry` | Gelé ; lookup concurrent sûr ; plusieurs appels provider en parallèle seulement si descriptor.concurrent_safe=true ; sinon rejet `PROVIDER_BUSY` par atomic_flag sans attendre sous un verrou. |
| `runtime::FeatureRegistry::Builder` | Mutable, **non thread-safe** ; registration explicite et validation avant freeze. |
| `runtime::FeatureRegistry` | Gelé ; lookups/dispatch possibles en parallèle, mais une feature dont concurrent_safe=false rejette la concurrence (`FEATURE_BUSY`). Le callback et ses données privées doivent respecter sa propre déclaration de sûreté. |
| `runtime::ProviderAccess` | Exclusif à une invocation ; pas de partage ni de persistance au-delà du retour du handler. |
| `Provider` / `FeatureHandler` | Objets conservés par shared_ptr<const>, jamais invoqués sous un verrou runtime. La constness ne synchronise pas les états mutables internes ; l'auteur garantit l'option concurrent_safe. |

Les appels sont **synchrones** et ne créent aucun thread, pool, singleton, global state mutable scientifique ou réseau. Les callbacks natifs sont invoqués sans lock arbitraire et leurs exceptions sont converties en erreurs structurées. Les providers de test ne sont jamais des providers scientifiques par défaut.

## Utilisation (pseudocode C++)

1. Créer un `ProviderRegistry::Builder`, enregistrer des `ProviderRegistration` avec identités de capability explicites, une version d'interface, contrats input/output, un objet `Provider` propriétaire et les deux validateurs, puis `freeze()`.
2. Créer un `FeatureRegistry::Builder(snapshot_fingerprint)`, enregistrer chaque `FeatureImplementation` avec ID, domaine, version package, fingerprint du snapshot, statuts package/scientifique/exécution, provenance, opération, dépendances et éventuel handler ; puis `freeze()`.
3. `FeatureRegistry::dispatch(invocation, providers, execution_context)` ne trouve que les fonctionnalités explicitement enregistrées. Les fonctionnalités structural_only / unsupported sont refusées ; les conditionnelles exigent des capabilities déclarées et un appel effectif via `ProviderAccess`.
4. Pour chaque opération, les validateurs d'entrée et de sortie sont **obligatoires** sur les capacités et features exécutables. Ils sont fournis par l'implémentation conforme au contrat de la fonctionnalité, pas inventés par le runtime.
5. Le snapshot est contrôlé à l'inscription ; aucune fonctionnalité de tllib-specs n'est supportée automatiquement.

## Défaillances, cancellation et délai

- Avant le callback : `ExecutionContext::check()` refuse token stoppé (`CANCELLED`) ou deadline expirée (`TIMEOUT`). Aucune opération de provider n'est lancée dans ce cas.
- Après un callback de provider ou d'implémentation : cancellation/expiration est `OUTCOME_INDETERMINATE` car des effets peuvent déjà avoir eu lieu. Aucun retry automatique ; réconciliation requise. Un deadline **ne préempte pas** un callback bloquant ; seul un provider coopératif peut honorer un budget en cours d'appel.
- Provider manquant/incompatible : `PROVIDER_REQUIRED` / `PROVIDER_INCOMPATIBLE`. Entrée/sortie invalide : `INVALID_PROVIDER_INPUT` / `INVALID_PROVIDER_OUTPUT`. Exception de callback : `OUTCOME_INDETERMINATE`, sans exposer de texte d'exception sensible.
- Les erreurs sont des `Result<T>` sans sortie partielle, avec TLC-FC, fingerprint specs, correlation_id et `stable_code`. Le registre ne met pas en cache de valeur fictive ou de résultat non validé.
- Une exécution conditionnelle ne peut pas retourner un succès si elle n'a pas invoqué chaque capability déclarée.
- Toute dépendance TLC-FC doit être inscrite ; l'absence, les doublons et les cycles sont rejetés avant gel. Le runtime ne crée aucun comportement inter-domaines ni ordre scientifique par défaut.

## Python et limites

Le port `Provider` est indépendant de Python. Une adaptation Python ultérieure devra conserver son objet callback, acquérir le GIL, convertir les erreurs sans fuite d'exception C++ et respecter les durées de vie. Ce binding effectif dépend des travaux #256/#257/#258 : **il n'est pas implémenté par cette PR**. Il n'existe aucun provider externe concret, aucune découverte automatique ni fallback.

Le contrat de types pour les identités de capabilities est opaque et explicite, jamais fabriqué depuis un nom de domaine. Le [catalogue des frontières](PROVIDER-BOUNDARY-INVENTORY.md) compte 694 fonctionnalités et leurs statuts sans leur assigner de provider par magie.

## Validation

```sh
cmake -S . -B build/native-core -DBUILD_TESTING=ON
cmake --build build/native-core --parallel 2
ctest --test-dir build/native-core --output-on-failure
```

`tests/runtime_provider_test.cpp` utilise uniquement des doubles locaux pour les cas de succès, erreurs, collision, version, dépendances, absence de provider, output invalide, exception, cancellation, deadline et chevauchement. Le workflow natif existant couvre ces tests et l'installation CMake/consommateur externe ; aucune matrice CI inutile n'est introduite.
