# V1 — Verrouillage du handoff, génération et conformité

Références : #254, #255, #240, #241, #244, #14.
Snapshot actuellement mentionné dans le backlog :
`07439babd59c657354e3200ed24c55e2e3eeb72c`.
Ce document **ne crée pas** un `specs.lock.json` exécutable et ne
déclare pas ce snapshot accepté par le futur validateur tllib.

## Frontière d'autorité

`tllib-specs/handoff/` est la seule entrée de la chaîne de
consommation logicielle. La population est lue dynamiquement depuis
`handoff/catalog.json`, pas codée en dur : le snapshot observé contient
36 domaines, 694 TLC-FC et huit contrats partagés, **non pas des maxima
autorisés dans le logiciel**. `registry/`, `maths/` et les chemins de
traçabilité historiques ne sont jamais ouverts par le runtime ou specgen.

Ordre d'autorité des artefacts d'un bundle : contract > acceptance >
contrats partagés référencés > manifest > README > examples >
traceability. Aucune équation ou provider n'est généré.
Le runtime ne lit aucun fichier du dépôt specs.

## Schema minimal proposé pour specs.lock.json

- `schema_version` du lock tllib ;
- `repository` = `Tradition-Learning-Community/tllib-specs` ;
- `commit` = SHA Git complet, jamais branche flottante ;
- `handoff_catalog_path` = `handoff/catalog.json` ;
- `catalog_sha256` = SHA-256 des **octets du fichier** catalog.json
  du snapshot vérifié (ne pas confondre avec fingerprint interne) ;
- `model_version` et `catalog_schema_version` lus du catalogue ;
- `verification` : version et algorithme de la procédure de validation.

Aucune date volatile dans l'identité ; les dates de production vont
dans le rapport de provenance, pas dans une empreinte déterministe.
Toute mise à jour du lock est PR dédiée, auditable et **jamais**
automatique. Interdire un SHA absent, un chemin non conforme, un hash
incohérent, une version incompatible et un snapshot incomplet.

## Algorithme de vérification visé

1. Lire localement une copie immuable explicitement fournie du handoff.
   Ne pas cloner automatiquement, ne pas suivre symlinks hors racine.
2. Vérifier SHA du commit par provenance Git vérifiable et intégrité
   content-addressed du catalogue (sha256 des octets).
3. Valider schémas, population, versions, empreintes, références et
   dépendances croisées **avec les outils publiés** de tllib-specs
   ou un consommateur équivalent indépendant, jamais exécuter un
   champ de package comme du code.
4. Refuser doublons, paths absolus/`..`, symlink escape, volumes
   excessifs et chemins non prévus. Limits définies et testées par #13.
5. Rapporter une erreur structurée + chemin + ID + provenance ; aucun
   fallback vers `main` ou un autre snapshot.
6. Génération canonique ordonnée, encodage stable, aucune horodatation ;
   deux générations indépendantes = octets identiques ; drift = échec.
7. Un nouvel ID, statut ou contrat est rapporté comme `gap`, jamais
   activé par simple découverte.

## Gate scientifique de release

Chaque TLC-FC du catalogue cible une décision explicite :
`executable` + conformance ; `conditionally_executable` + provider
explicite et preuve ; `structural_only` ou unresolved + représentation
sans fausse exécution ; autre statut publié + refus conforme.
Les cas d'acceptation applicables et comportements interdits sont
testés, avec oracles indépendants lorsque pertinents.
Le rapport associe commit tllib, commit specs, hash catalogue,
versions d'outils, plateforme, IDs, preuves, décisions, limitations.
Une couverture d'inventaire à 100 % ne signifie pas que 100 %
des fonctionnalités calculent un résultat.

Blocage isolé : tllib#231 / tllib-specs#231 concerne uniquement
TLC-FC-30-EXPANSION-014, domaine #40, lot #177. Aucun argument
ou règle scientifique ne peut être ajouté pour lever ce blocage.
