# Phase A — Package Python natif local (#257)

Ce dépôt contient un seul cœur C++20, utilisé à travers `tllib._native`.
Le pont provider CPython existant est conservé, sans nouvel algorithme scientifique.
Le binder pour les futurs types est traité séparément en #256.

Depuis la racine, avec un environnement Python CPython et un CMake >=3.27 :
```sh
python -m pip install 'scikit-build-core>=0.11,<1' build
python -m build --wheel --no-isolation
python -m venv /tmp/tllib-clean
/tmp/tllib-clean/bin/pip install --no-index --no-deps dist/tllib*.whl
(cd /tmp && /tmp/tllib-clean/bin/python -c 'import tllib; print(tllib.__version__)')
python -m pip install -e . --no-build-isolation
```

`pyproject.toml` est à la racine car il pilote le projet CMake complet.
L'extension compilée et les stubs `.pyi`/`py.typed` sont installés par
CMake et non importés par hasard depuis `bindings/python`. Les wheels
sont liées à la version CPython/plateforme construite (pas de promesse abi3).
Le numéro `0.1.0` est un numéro de préparation SemVer 0.x, **pas** une
garantie de stabilité ABI ni une publication V1 scientifique.
Le build C++ autonome continue de fonctionner avec l'option Python OFF.
Aucun téléchargement réseau n'est déclenché par le build CMake ordinaire.
