# Registre explicite des implémentations TLC-FC

`tllib.discovery` ne recherche aucun module automatiquement. L’application
construit des `FeatureImplementation` immuables, les groupe dans un
`DomainImplementation` immuable, puis les enregistre explicitement avec le
catalogue de handoff correspondant.

```python
from pathlib import Path

from tllib.discovery import (
    DomainImplementation,
    FeatureImplementation,
    ImplementationRegistry,
    load_catalog,
)

catalog = load_catalog(Path("../tllib-specs/handoff/catalog.json"))
registry = ImplementationRegistry(catalog)
registry.register(
    DomainImplementation(
        "master",
        (
            FeatureImplementation(
                "TLC-FC-00-MASTER-001",
                "1.0.0",
                "my_application.master.describe_threshold",
            ),
        ),
    )
)
```

L’enregistrement refuse immédiatement les doublons, les identifiants absents
du catalogue, les features rattachées au mauvais domaine et les versions de
package incompatibles. Utilisez `list_implementations`, `find_implementation`
et `compare_to_catalog` pour inspecter le registre. La comparaison signale les
features manquantes et, pour les domaines déclarés, les sous-ensembles partiels.
Elle ne crée ni implémentation ni valeur de repli.
