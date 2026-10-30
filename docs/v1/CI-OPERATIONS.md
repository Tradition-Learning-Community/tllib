# CI V1 des fondations — parcours contributeur (#243)

**Périmètre validé :** fondations C++20 et CPython 3.12 sur
`ubuntu-24.04` x86-64 ; aucun domaine TLC-FC scientifique n'est
implémenté ni rendu conforme par ce workflow. Les autres OS/architectures
restent candidats non qualifiés ([matrice](PLATFORMS-2027.md)).

## Routage réel des modifications

| Modifications de la PR | CI appelée | Ce qui n'est pas lancé |
| --- | --- | --- |
| `docs/**` seulement | Aucun job de compilation natif ; preuve de routage `test_ci_scopes.py` | CMake, wheel, conformité, sanitizers |
| `include/tllib/**`, `tests/*.cpp`, `CMakeLists.txt` | `native-core` (CTest/consommateur, providers, ASan/UBSan), `python-wheel`, `quality` | Pas de matrice OS non qualifiée |
| `bindings/python/**`, `tests/python/**` | `native-core`, `python-wheel`, `quality` | Pas de release PyPI |
| `tools/specs_pipeline.py`, `tools/specs_sync.py`, `tests/specs/**` | `pinned-specs` et `quality` | Pas d'implémentation de domaines |
| `specs.lock.json`, `generated/specs/**`, `conformance/**` | `pinned-specs` | Pas de compilation C++ par ces seuls changements |
| `spikes/binders/**` | `binder-spike` ; étude isolée | Pas d'adoption automatique du binder |
| `.github/workflows/X.yml` | Le workflow X lui-même, grâce à son path filter | Aucun contournement silencieux du contrôle correspondant |

Les filtres réels sont testés dans
`tests/quality/test_ci_scopes.py` pour documentation seule, core,
Python, pipeline specs et modifications de chaque workflow. La CI
de fondation n'exécute pas de matrice cartésienne par commit.

## Commandes locales

```sh
cmake -S . -B build/native -DBUILD_TESTING=ON
cmake --build build/native --parallel 2
ctest --test-dir build/native --output-on-failure
python3 -m unittest discover -s tests/specs -p 'test_*.py' -v
python3 -m unittest discover -s tests/quality -p 'test_*.py' -v
python3 tools/compatibility.py
python3 tools/quality_check.py --base HEAD^
```

Le dernier contrôle utilise Ruff 0.14.1 et clang-format 18.1.8,
et la CI lance clang-tidy-18 sur une unité C++ réelle. Les commandes
CMake n'utilisent aucun téléchargement réseau implicite. Pour les tests
du handoff, fournir le checkout exact du SHA figurant dans
`specs.lock.json` comme indiqué dans [le pipeline](SPECS-PIPELINE-IMPLEMENTATION.md).

## Durées mesurées, non contractuelles

Sur un passage réussi de PR #280 (Linux GitHub Actions, 30 octobre 2026) :

| Job | Temps d'exécution observé | Preuve |
| --- | ---: | --- |
| Source quality (lint, format, analyse, tests négatifs) | 12 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233488/job/124047513041) |
| C++20 CTest + consommateur externe | 11 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233493/job/124047513251) |
| Python provider/structural parity | 9 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233493/job/124047513285) |
| C++ ASan/UBSan | 17 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233493/job/124047512936) |
| Wheel et installation CPython 3.12 | 20 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233507/job/124047513078) |
| Snapshot pinned, génération, conformité/diff | 19 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233555/job/124047513918) |
| Spike binder (déclenché par modification de son workflow) | 32 s | [job](https://github.com/Tradition-Learning-Community/tllib/actions/runs/41051233501/job/124047513216) |

Ces mesures sont les durées d'un passage, **pas** des seuils de
performance, de SLA ou des garanties futures. Les jobs concurrents
n'ont pas un temps global égal à leur somme.

## Permissions et release

Les actions `checkout`, `setup-python` et `upload-artifact`
sont épinglées à des SHA de commit vérifiés. Les jobs emploient
`contents: read` et `persist-credentials: false`. Aucun cache
n'est utilisé pour attester la conformité ; aucun secret ou token
d'écriture n'est requis. Les dépendances Python de développement
sont installées explicitement.

Les jobs sont conditionnés à l'impact ; une branche protégée ne
doit pas rendre obligatoires des checks qui n'existent pas pour une
PR documentaire seule sans stratégie de vérification appropriée.
La configuration effective des règles de protection GitHub nécessite
une vérification administrative distincte.

Le gate `release-gate` du snapshot doit encore refuser la release :
les domaines scientifiques ne sont pas implémentés. Les roues de
release multi-OS, SBOM/signature, fuzzing prolongé et ABI stable
relèvent de #11 et des qualifications futures, **pas** d'une
fausse réussite de la phase B.
