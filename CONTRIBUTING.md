# Contributing to `tllib`

## Prérequis

- Python 3.10 ou supérieur ;
- `uv` ;
- Git.

Installez l'environnement depuis un clone propre :

```bash
uv sync --locked --dev
```

## Frontière avec `tllib-specs`

Avant tout changement, respecter `docs/repository-boundary.md`.

- `tllib-specs` définit la sémantique et les obligations observables.
- `tllib` implémente ces obligations en Python.
- Ne jamais lire `maths/` ou `registry/` comme dépendance runtime.
- Ne jamais compléter une ambiguïté scientifique par une valeur par défaut.
- Toute fonctionnalité doit rester liée à son identifiant TLC-FC et au SHA des
  spécifications consommées.

## Contrôles

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv build
```

La couverture est contrôlée par pytest et ne doit pas diminuer sans décision
explicite.

## Verrou des spécifications

`specs.lock.json` enregistre le dépôt canonique `tllib-specs`, le SHA, la
version du modèle, l'empreinte du catalogue et une date informative.

Pour vérifier le verrou :

```bash
TLLIB_SPECS_ROOT=/chemin/vers/tllib-specs uv run python -m tllib.specs verify
```

Une mise à jour du verrou doit être séparée, révisable et précédée d'une
comparaison de la révision amont. Ne changez jamais le verrou uniquement pour
faire disparaître une erreur.

## Pull requests

Une PR doit indiquer :

- l'issue concernée ;
- le SHA de `tllib-specs` lorsqu'un contrat est consommé ;
- les identifiants TLC-FC concernés ;
- les tests et commandes exécutés ;
- les limites ou fournisseurs requis ;
- toute question scientifique laissée ouverte.

Les changements d'architecture ou d'API doivent mettre à jour l'ADR
correspondant.
