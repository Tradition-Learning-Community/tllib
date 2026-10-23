# Contrat transversal V1 — Providers, capabilities et adaptation Python (#239)

**Autorité d'architecture : tllib** ; **autorité scientifique : tllib-specs**. Tout comportement normatif du provider vient du handoff. Ce document n'invente ni algorithme ni politique scientifique de repli.

## Frontière native obligatoire

- `CapabilityId` : identité opaque, versionnée, distincte de `FeatureId` ; validation au runtime. Association TLC-FC -> capability réalisée explicitement depuis les contrats publiés ; ne pas dériver les IDs d'un nom de module ou d'une chaîne arbitraire.
- `ProviderDescriptor` immuable : `capability_id`, version de l'interface, identifiant stable du provider, schéma d'entrée/sortie ou références contractuelles, capacités déclarées, provenance/configuration non secrète. Déclarer n'est pas une preuve d'exécution.
- `ProviderRegistry` : inscription explicite par builder/configuration avant gel ; doublons incompatibles et collisions refusés ; pas de chargement par réflexion/import/side effects ; aucun provider réseau/ML par défaut.
- `ProviderRequest` porte TLC-FC, opération publiée, données déjà validées, `ExecutionContext` de l'appel, identifiant de corrélation et version specs. `ProviderResponse` est validé par le runtime avant de sortir du port ; un résultat malformé n'est pas une valeur par défaut.
- Durée de vie : le runtime conserve les objets providers propriétaires pendant les appels ; aucun callback après destruction ; aucun pointeur/vues entrantes conservés au-delà de l'appel sans transfert explicite.
- **Aucun plugin tiers in-process n'est sandboxé**. Si l'on doit exécuter du code hostile, il faut une séparation de processus définie hors cœur et une analyse de risque.

## Dispatch et défaillances

1. Résoudre la feature au snapshot strict et vérifier `execution_status`.
2. Pour `conditionally_executable` uniquement, résoudre l'ensemble des capabilities **déclarées**, sans découverte implicite.
3. Refuser l'absence/discordance via `provider_required` / `provider_incompatible` avec TLC-FC et provenance ; ne jamais convertir en `structural_only` ni en résultat calculé.
4. Valider intégralement les entrées, appel borné par cancellation et budget **uniquement lorsque le provider peut les honorer** ; pas de faux timeout sur appel bloquant non interruptible.
5. Capturer les erreurs providers : exception, erreur native, timeout, cancellation, résultat invalide ; diagnostic structuré et sans fuite de secret. Réconciliation obligatoire quand effets externes indéterminés : interdiction du retry aveugle.
6. Valider schéma/sémantique observable de la réponse ; aucune valeur fallback, conversion silencieuse ou provider implicite.
7. Le runtime journalise seulement métadonnées de diagnostic non sensibles ; pas de réseau, télémétrie ou export automatisés cachés.

## Port C++ et port Python

- Port C++ public conceptuel : `Provider::invoke(const ProviderRequest&, const ExecutionContext&) -> Result<ProviderResponse>` ; nom final de types aligné en #235/#238. Pas de `std::function` capturant des références expirantes dans le registre gelé.
- Adaptation Python centralisée dans les bindings : contrôle GIL, conversion `Result/Error` selon `PYTHON-PUBLIC-API-CONTRACT.md`, ownership du callable, propagation d'exceptions sans franchir l'ABI C++, prévention des deadlocks. Aucun domaine ne code sa propre adaptation Python.
- Même `capability_id`, inputs/outputs, validations et erreurs pour les deux langages ; tests du même jeu de fixtures. Fake provider autorisé **seulement pour tests** : il prouve l'interface, pas la validité scientifique d'un fournisseur concret.
- Version provider incompatible : refuser explicitement ; ne pas supposer compatibilité d'un numéro de package scientifique.
- Injection explicite par appel/contexte/registre gelé ; ne pas utiliser variable d'environnement opaque comme découverte de provider. Privilégier configuration transparente, sans secrets persistants en logs.

## Reproductibilité et sûreté

Les providers peuvent être non déterministes ou externes : conserver provenance du provider, version, configuration autorisée, état/seed si normatif ; distinguer l'oracle structurel de l'oracle scientifique. La CI ne requiert **aucun service externe réel** pour tester les ports communs. Tests négatifs : absent, doublon, version incompatible, output illégal, callback Python échouant, cancellation avant/après effets, exceptions, mauvais lifetime et concurrence interdite.

## Gate de fermeture #239

Le contrat est centralisé ici. La tâche #239 reste un **travail de fondation du projet** jusqu'à ce que l'interface native, registre, adaptateur Python et tests C++/Python du port commun fonctionnent. Les lots TLC-FC n'implémenteront alors que les capacités approuvées applicables à leur feature, sans concevoir les ports.
