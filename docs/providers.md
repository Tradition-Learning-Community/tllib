# Injection explicite de fournisseur

Les opérations qui nécessitent une ressource externe reçoivent toujours leur
fournisseur en argument. `tllib` ne recherche ni fournisseur global, ni
adaptateur par défaut, et ne retourne jamais de valeur de repli.

1. L'application construit un adaptateur qui implémente `Provider`.
2. L'adaptateur déclare précisément ses `capabilities`.
3. L'application l'injecte dans l'opération avec le type d'entrée, le type de
   sortie et un délai positif obligatoires.
4. L'opération appelle `invoke_provider`; elle traite les erreurs explicites
   (`ProviderRequiredError`, incompatibilité, timeout, exception et résultat
   invalide) plutôt que de poursuivre avec un comportement implicite.

```python
from tllib.providers import CapabilityId, invoke_provider

result = invoke_provider(
    provider,
    CapabilityId("master.lookup"),
    "Ada",
    input_type=str,
    result_type=Master,
    timeout_seconds=2.0,
)
```

Le fournisseur doit respecter le délai transmis et lever `TimeoutError` quand
il expire. Les doubles de fournisseurs sont réservés à `tests/fakes/`; ils ne
font pas partie du paquet d'exécution.
