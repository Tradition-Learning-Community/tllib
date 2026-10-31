# V1 — Parcours contributeurs vérifiables (phase C)

Ce guide s'applique aux **fondations de préparation** de `tllib`, et non à une V1 scientifique publiée. Le runtime de référence est C++20 ; la façade Python utilise le même runtime natif. Les 36 domaines scientifiques n'ont pas encore d'algorithme implémenté. Les commandes ci-dessous sont celles des workflows GitHub Actions et des fichiers du dépôt ; les exécutions positives **observées** sont sur Ubuntu 24.04 x86-64 (GCC et CPython 3.12). Les autres environnements nécessitent leur propre qualification, voir [PLATFORMS-2027.md](PLATFORMS-2027.md). L'environnement d'édition de cette phase C ne peut pas cloner GitHub depuis le shell : aucune nouvelle validation locale indépendante n'est prétendue.

## 0. Choisir une issue et vérifier son autorité

1. Parcourir les [issues](https://github.com/Tradition-Learning-Community/tllib/issues) et la [taxonomie](READINESS-AND-GOVERNANCE.md). `status:ready` est réservé aux tâches individuellement prouvées ; sans ce label, une tâche n'est **pas** présumée prête.
2. Les issues #15–#50 sont des epics domaine, #53–#230 sont des lots TLC-FC ; les epics ne sont pas automatiquement assignables comme tâches.
3. Pour un lot, lire `specs.lock.json` (actuellement `07439babd59c657354e3200ed24c55e2e3eeb72c`), puis `handoff/catalog.json`, `handoff/domains/<domaine>/catalog.json` et les fichiers `contract.json`, `acceptance.json`, `manifest.json`, `traceability.json` du package certifié. Ne jamais interpréter une formule originale à la place des obligations du handoff.
4. Une ambiguïté **normative** relève de [tllib-specs](https://github.com/Tradition-Learning-Community/tllib-specs/issues/new/choose). Dans `tllib`, ne créer qu'un blocker logiciel ciblé. L'issue #231 empêche `TLC-FC-30-EXPANSION-014` dans #177, pas tout le domaine Expansion.
5. Aucun changement d'architecture, d'interface commune ou de tolérance scientifique ne se décide dans une PR de lot.

## 1. Parcours C++20 — build, tests et consommateur installé

Prérequis : Git, CMake **>=3.27**, un compilateur C++20, et Ninja pour les presets (`CMakePresets.json`). Depuis un clone propre :

```sh
git clone https://github.com/Tradition-Learning-Community/tllib.git
cd tllib
cmake --preset dev
cmake --build --preset dev
ctest --preset dev --output-on-failure
cmake --install build/dev --prefix /tmp/tllib-prefix
cmake -S tests/consumer -B build/consumer -DCMAKE_PREFIX_PATH=/tmp/tllib-prefix
cmake --build build/consumer
build/consumer/tllib_external_consumer
```

La CI utilise également la variante sans preset `cmake -S . -B build/native-core -DBUILD_TESTING=ON`, puis build, CTest et consommateur installé. Les headers publics sont sous `include/tllib/{core,shared,runtime,providers}` ; l'export CMake s'appelle `tllib::core`. La cible est actuellement header-only et ne contient pas d'implémentation TLC-FC. Voir [ARCHITECTURE.md](ARCHITECTURE.md), [SHARED-CXX20-FOUNDATION.md](SHARED-CXX20-FOUNDATION.md) et [FOUNDATION-BUILD-SMOKE.md](FOUNDATION-BUILD-SMOKE.md).

Pour du code C++ ou runtime, ajouter des tests CTest et vérifier les erreurs stables, le registry, les providers explicites, le lifetime et la cancellation. Ne pas créer de logique scientifique Python distincte.

## 2. Parcours Python — wheel CMake, édition et typage

**Support prouvé actuel : CPython 3.12 sur Ubuntu 24.04 x86-64**, `requires-python >=3.12,<3.13` (voir `pyproject.toml`). À partir du clone :

```sh
python3.12 -m venv .venv
. .venv/bin/activate
python -m pip install 'scikit-build-core>=0.11,<1' build
python -m build --wheel --no-isolation
python -m venv /tmp/tllib-wheel-check
/tmp/tllib-wheel-check/bin/python -m pip install --no-index --no-deps dist/tllib*.whl
(cd /tmp && /tmp/tllib-wheel-check/bin/python -c "import tllib; print(tllib.__version__)")
python -m pip install -e . --no-build-isolation
python -c 'import tllib; print(tllib.ProviderRegistry)'
```

La compilation native CPython peut également être testée par CTest :

```sh
cmake -S . -B build/python-provider -DBUILD_TESTING=ON -DTLLIB_BUILD_PYTHON_PROVIDER_BRIDGE=ON
cmake --build build/python-provider --parallel 2
ctest --test-dir build/python-provider -R 'tllib_python_(provider_bridge|identity_parity)' --output-on-failure
```

La CI de wheel vérifie aussi `tests/python/test_provider_bridge.py`, `test_buffers.py` (avec NumPy) et `test_parity.py` dans un environnement propre. Les fichiers `bindings/python/tllib/__init__.pyi` et `py.typed` décrivent la surface typée ; `tllib._native` maintient la source C++ de vérité. Les wrappers Python ne possèdent pas les TLC-FC. Consulter [PYTHON-WHEEL-PACKAGING.md](PYTHON-WHEEL-PACKAGING.md), [PYTHON-CXX-PARITY.md](PYTHON-CXX-PARITY.md) et [PYTHON-BUFFER-INTEROP.md](PYTHON-BUFFER-INTEROP.md).

## 3. Parcours tooling, snapshot et conformité

Un checkout **local, propre et exactement au SHA du lock** de `tllib-specs` doit être fourni ; les outils ne téléchargent ni ne mettent à jour la science. Le checkout dans l'exemple est en lecture seule :

```sh
git clone https://github.com/Tradition-Learning-Community/tllib-specs.git /tmp/tllib-pinned-specs
git -C /tmp/tllib-pinned-specs checkout --detach 07439babd59c657354e3200ed24c55e2e3eeb72c
python3 tools/specs_pipeline.py verify --specs /tmp/tllib-pinned-specs
python3 tools/specs_pipeline.py check-generated --specs /tmp/tllib-pinned-specs
python3 tools/specs_pipeline.py report --specs /tmp/tllib-pinned-specs --output build/specs-report
python3 -m unittest discover -s tests/specs -p 'test_*.py' -v
python3 tools/compatibility.py
```

Le `release-gate` doit **échouer actuellement** tant que 693 TLC-FC restent `unimplemented` et `TLC-FC-30-EXPANSION-014` `blocked-by-spec`. Une réussite du contrôle de catalogue **n'est pas** une conformité scientifique. `generate` et `specs_sync.py` ont une sortie déterministe ; la synchronisation se fait hors ligne, avec lock candidat séparé et revue scientifique/compatibilité, jamais automatiquement. Voir [SPECS-PIPELINE-IMPLEMENTATION.md](SPECS-PIPELINE-IMPLEMENTATION.md), [SPECS-SYNC-MIGRATION.md](SPECS-SYNC-MIGRATION.md) et [CI-OPERATIONS.md](CI-OPERATIONS.md).

## 4. Parcours documentation, QA et sécurité — sans C++ obligatoire

Les corrections de liens, guides, modèles d'issues, tests négatifs **Python pur**, rapports, fixtures de tooling et audits de scripts peuvent être proposées sans compiler de code C++, lorsque l'issue est autonome et testable. Les commandes ciblées existantes sont :

```sh
python3 -m unittest discover -s tests/quality -p 'test_*.py' -v
python3 -m unittest discover -s tests/specs -p 'test_*.py' -v
python3 tools/compatibility.py
python3 tools/quality_check.py --base HEAD^
```

La dernière commande requiert les versions d'outillage documentées dans [QUALITY-LOCAL.md](QUALITY-LOCAL.md), et `HEAD^` n'est utile qu'après un commit. Un changement exclusivement documentaire ne déclenche pas de compilation CMake dans la CI filtrée : vérifiez **manuellement** les liens, ancres, commandes et orthographe ; indiquez explicitement les tests non exécutés. Les bugs logiciels utilisent le [formulaire dédié](https://github.com/Tradition-Learning-Community/tllib/issues/new/choose), sans ticket de domaine artificiel. Les vulnérabilités ne se publient pas en issue publique : [SECURITY.md](../../SECURITY.md).

## 5. PR, revue et clôture

1. Travailler sur une branche dédiée ; un commit par modification logique, avec sign-off personnel DCO : `git commit -s -m "docs: ..."`.
2. Ouvrir une PR vers `main` avec l'issue autonome, le parent et les dépendances ; renseigner le snapshot et les TLC-FC **uniquement si applicables**.
3. Donner les commandes réellement exécutées, résultats, limites et preuves (CTest, install externe, wheel, conformance). Ne jamais déclarer `ready` ou `covered` par simple documentation.
4. Appliquer la revue technique et scientifique appropriée décrite dans [REVIEW-AND-MERGE.md](REVIEW-AND-MERGE.md). Les contrôles CI filtrés ne sont pas remplacés par un statut déclaré manuellement.
5. Fermer une issue seulement lorsque tous ses critères d'acceptation sont satisfaits, en citant PR, commit et contrôles. Une PR partielle ne ferme pas le ticket.

**Limites de preuve (31 octobre 2026)** : GitHub Actions a vérifié la compilation native, le consommateur CMake, la wheel CPython 3.12, la parité structurelle, les tests négatifs de specs, la conformité et la qualité sur Linux. Cela ne qualifie pas Windows/macOS ni une couverture TLC-FC réelle. Toute plateforme non testée reste indiquée « non vérifiée ».
