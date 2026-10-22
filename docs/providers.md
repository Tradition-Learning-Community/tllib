# Injection explicite de fournisseurs

Les capacités conditionnelles utilisent exclusivement des fournisseurs injectés
par l'application. tllib ne découvre aucun fournisseur, n'effectue aucun appel
réseau caché et ne fournit aucune valeur scientifique de repli.

## Contrat

Un Provider déclare explicitement ses CapabilityId et reçoit un
ProviderCallContext contenant :

- le délai demandé ;
- le FeatureId lorsqu'il est connu ;
- un jeton d'annulation coopératif optionnel.

Les entrées sont validées avant l'appel et les sorties avant leur utilisation.

```python
from tllib import FeatureId
from tllib.providers import CapabilityId, invoke_provider

result = invoke_provider(
    provider,
    CapabilityId("master.lookup"),
    "Ada",
    input_type=str,
    result_type=Master,
    timeout_seconds=2.0,
    feature_id=FeatureId("TLC-FC-00-MASTER-001"),
)
```

## Registre

ProviderRegistry est volontairement explicite. Un provider doit être enregistré
par l'application et deux providers ne peuvent pas revendiquer silencieusement
la même capacité.

Les doubles de tests restent sous tests/fakes et ne font pas partie du paquet
runtime.
