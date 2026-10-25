# Pipeline scientifique V1 opérationnel — #254, #255, #241

Source normative verrouillée : tllib-specs, commit 07439babd59c657354e3200ed24c55e2e3eeb72c. Voir specs.lock.json et docs/v1/SPECS-LOCK-AND-CONFORMANCE.md.

## Snapshot et provenance

`specs.lock.json` est un verrou réel : dépôt canonique, SHA Git complet, version du modèle/schéma, chemin immuable `handoff/catalog.json`, SHA-256 **des octets du catalogue** et méthode de vérification/version. Il n'existe aucun update automatique de ce verrou.

L'outil `tools/specs_pipeline.py` fonctionne **hors ligne** sur un checkout Git explicitement fourni et propre. Il vérifie HEAD Git exact, l'identité de l'objet du catalogue, le hash, les versions, les 36 catalogues de domaine, les 694 bundles et les huit contrats partagés. Les effectifs 36/694/8 sont observés et non codés comme maxima. Il refuse doublons, paths absolus ou traversée, symlinks, JSON invalides/clés dupliquées, tailles et profondeurs excessives, versions/statuts non autorisés, dépendances manquantes ou cycliques, manifests/acceptances incohérents.

Seul `handoff/` est lu comme entrée : les chemins scientifiques historiques dans `maths/` et `registry/` restent de simples références de provenance, jamais exécutées ni chargées. Le runtime C++ ne lit aucun fichier specs. Les empreintes SHA-256 de packages et descriptors sont vérifiées en **forme**, pas recalculées par ce vérificateur indépendant ; l'intégrité Git du checkout propre est vérifiée, et le validateur amont conserve l'autorité sur son algorithme d'empreinte de packages.

## Génération des métadonnées

Commande : `python3 tools/specs_pipeline.py generate --specs /chemin/tllib-specs`.

Fichiers suivis dans le dépôt :
- `generated/specs/feature_index.json` : index canonique trié des IDs, domaines, versions, statuts, manifests et provenance du snapshot.
- `include/tllib/generated/feature_metadata.hpp` : table C++20 constexpr installée avec le package, y compris les constantes `specs_commit` et `catalog_sha256`.

Ils ne créent aucun handler, provider, enregistrement runtime, équation ou méthode scientifique. Une nouvelle fonctionnalité est une métadonnée, jamais une activation automatique. La CI compare deux générations indépendantes octet par octet, puis les compare aux fichiers commités. Le format est stable, sans date, horodatage ni champ aléatoire.

## Conformité et deux gates séparés

`conformance/decisions.json` est lié au SHA verrouillé et possède une décision explicite pour chacun des 694 TLC-FC. Aucune feature de domaine n'étant implémentée, 693 décisions sont `unimplemented` et `TLC-FC-30-EXPANSION-014` est `blocked-by-spec` (tllib#231 / tllib-specs#231). Cela ne prétend pas à 694 implémentations.

Les catégories du rapport sont : `covered`, `structural`, `provider-required`, `blocked-by-spec`, `unimplemented`, `invalid`. Chaque entrée conserve les statuts du catalogue, les identifiants d'acceptations, le motif de la décision et les preuves. Diagnostics stables : code, TLC-FC, chemin, attendu, observé.

Le **gate de décision** (`report`) exige exactement un enregistrement par TLC-FC présent, sans IDs périmés. Une nouvelle feature produit `MISSING_DECISION`, jamais un support implicite. Les sorties machine/humaines sont `coverage.json` et `coverage.md`, déterministes.

    python3 tools/specs_pipeline.py report --specs /chemin/tllib-specs --output build/specs-report

Pour qu'une décision `covered` (exécutable/conditionnelle) ou `structural` (structural_only) soit valide, **chaque acceptance test ID publié** doit être relié à une source de test tllib réelle et à un testcase **réellement réussi** dans un XML JUnit CTest fourni explicitement. Un texte `"passed"` sans suite CTest vérifiée est insuffisant. Les tests sont écrits dans tllib ; **aucun code de tllib-specs n'est exécuté**. Exemple :

    ctest --test-dir build/native-core --output-junit build/native-core/ctest.xml
    python3 tools/specs_pipeline.py report --specs /chemin/tllib-specs --test-results build/native-core/ctest.xml

Le **gate de release** (`release-gate`) refuse toute décision `unimplemented`, `blocked-by-spec`, `provider-required` ou `invalid`. **Il doit échouer actuellement** : le catalogue est entièrement inventorié, pas scientifiquement exécuté.

    python3 tools/specs_pipeline.py release-gate --specs /chemin/tllib-specs --output build/release-gate

Le workflow GitHub Actions `Pinned specs and catalogue conformance` fait un checkout **explicite** du SHA du lock, exécute les vérifications offline, régénère les métadonnées, contrôle le drift, produit le rapport et teste les entrées malformées, cycles, fraude de preuves et défaillances de provenance. Le workflow ne change jamais le lock et n'ajoute pas de matrice de backends scientifiques.

## Frontières

Cet outil construit le socle de conformité et le rapport de couverture reproductible. Il ne certifie aucune fonctionnalité TLC-FC sans oracle/test de domaine effectivement implémenté. Les 694 futures implémentations restent des travaux des lots fonctionnels ; les sources scientifiques demeurent sous l'autorité de tllib-specs. Le gate de release restera bloqué jusqu'à preuves complètes.
