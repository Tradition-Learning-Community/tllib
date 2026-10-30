# Adaptateur Python vers le registre de providers C++20 — #239

Cette interface complète le **port provider natif** de tllib, sans constituer une seconde implémentation du runtime ou une bibliothèque scientifique Python. Les données scientifiques et opérations autorisées restent gouvernées par les contrats de [tllib-specs](https://github.com/Tradition-Learning-Community/tllib-specs/tree/07439babd59c657354e3200ed24c55e2e3eeb72c/handoff).

## Architecture

- **C++** : `tllib::providers::ProviderRegistry` est seul responsable de l'inscription explicite, du gel, des refus de collisions, de la version, de la validation input/output, des erreurs stables et du contrôle de concurrence.
- **Adaptateur** : `bindings/python/native/provider_bridge.cpp` est une très fine couche optionnelle sur l'API C officielle de CPython. Elle n'est **pas** une décision de binder général et ne remplace pas le spike comparatif nanobind/pybind11 de #256 ; ce dernier reste ouvert.
- **Façade typée** : `bindings/python/tllib/__init__.py` expose `ProviderRegistration`, `ProviderRegistry`, `ProviderRequest`, `ProviderResponse`, `CancellationSource` et `TllibError`. Les stubs PEP 561 sont fournis.
- **Aucun enregistrement implicite** : la liste fournie à `ProviderRegistry([...])` est le seul point d'injection. Une liste vide ne crée aucun provider par magie. Les identités de capability, les références aux contrats et les versions sont explicites.
- **Pas de sérialisation scientifique ajoutée** : les payloads sont des `bytes` opaques ; les validateurs sont **obligatoires**, fournis par l'utilisateur/domaine qui implémente un contrat approuvé. Les callbacks utilisés par les tests ne sont que des doubles.

## Signature du port

Chaque `ProviderRegistration` contient le code de capability, sa version d'interface, un identifiant provider, les références de contrats input/output, la provenance, la fonction Python et ses deux validateurs.

Le callback reçoit exactement `(feature_id: str, operation_id: str, payload: bytes, correlation_id: str, specs_fingerprint: str)` et retourne `(output_contract: str, payload: bytes)`. Les validateurs reçoivent `bytes` et renvoient exactement `bool`, sans coercition arbitraire. `ProviderRegistry.invoke(request, cancellation=..., timeout_ms=...)` retourne un `ProviderResponse` seulement si le résultat a passé les validations natives.

Les erreurs attendues deviennent `TllibError` avec `code` stable, `feature_id`, `specs_provenance` et `context`. Les exceptions Python levées par les callbacks ne franchissent **pas** l'ABI C++ et leur texte n'est pas divulgué ; le code `OUTCOME_INDETERMINATE` exige une réconciliation avant retry après effets potentiels. Erreurs d'entrée/sortie, provider absent/incompatible, cancellation, deadline et refus d'accès concurrent restent distincts.

## GIL, durée de vie, concurrence

Le module relâche le GIL pendant la traversée du registre C++, puis le réacquiert dans le callback et les validateurs Python. Aucun verrou C++ arbitraire n'est détenu pendant ces appels. `ProviderRegistry` possède des références fortes aux fonctions jusqu'à sa destruction ; les callbacks ne sont pas exécutés depuis un destructeur. Un provider `concurrent_safe=False` refuse une réentrance ou un deuxième appel simultané avec `PROVIDER_BUSY`.

Une cancellation **avant** l'appel entraîne `CANCELLED`. Une deadline expirée **avant** l'appel entraîne `TIMEOUT`. Une demande après début d'exécution, ou une deadline échue pendant le callback, entraîne `OUTCOME_INDETERMINATE` après son retour, **sans** feindre une interruption d'un travail bloquant. Aucune relance automatique.

Le pont est destiné à l'interpréteur CPython principal dans ce jalon. L'usage des sous-interpréteurs, les builds free-threaded et les ABI stables ne sont **pas** déclarés compatibles avant les tests spécifiques de la phase B. Ce code n'isole pas un provider non fiable : les callbacks exécutent du Python in-process.

## Construction et tests

La bibliothèque C++ pure se construit normalement et ne cherche **pas** Python.

Pour le pont optionnel (CPython 3.9+ et headers de développement installés) :

```sh
cmake -S . -B build/python-provider -DBUILD_TESTING=ON -DTLLIB_BUILD_PYTHON_PROVIDER_BRIDGE=ON
cmake --build build/python-provider --parallel 2
ctest --test-dir build/python-provider --output-on-failure
PYTHONPATH=build/python-provider/python python3 -c 'import tllib; print(tllib.ProviderRegistry)'
```

Le workflow `Native core C++20` exécute le test Python contre la **vraie extension C++** ; les tests vérifient callback, paramètres et payloads NUL compris, erreurs identiques au registre natif, validation input/output, ownership par weakref, callback qui lève une exception, cancellation avant/après démarrage, deadline, refus concurrent et réentrance.

## Périmètre et dépendances laissés ouverts

- #239 : adaptateur Python d'un port provider **effectif**, sans provider scientifique, avec tests d'intégration. Ce travail ne rend aucune des 694 features exécutable par défaut.
- #256 : choix final du binder **non effectué** ; les deux prototypes nanobind/pybind11, benchmarks et décision ADR-004 restent à produire.
- #257 : wheels et package Python complets non réalisés ici ; seul le module optionnel de développement est construit par CMake. 
- #258 : extension de l'API Python globale, typing complet, mapping des autres objets C++ et tests de parité par domaine restent à effectuer. Le port provider est typé sans prétendre couvrir cette API générale.

La façade de ce jalon ne contient ni algorithme scientifique ni calcul de domaine ; les règles de validation sont apportées par les implémentations approuvées de chaque future feature.
