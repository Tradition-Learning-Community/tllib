# V1 — Qualité scientifique, sécurité et compatibilité

Références : #13, #14, #249, #243, #12, #241, ADR-008/009.
Statut : politique de conception ; pas de tests ni d'attestations
prétendument réalisés.

## Science reproductible et falsifiable

Pour chaque calcul soumis à conformance : référence TLC-FC/contrat,
acceptations positives et négatives, entrées complètes, version de
spécifications, provenance, oracle indépendant si possible,
plateforme, toolchain, backend, précision et graines si applicable.
Ne jamais inventer une précision ou une tolérance de résultat parce
qu'un test échoue. Comparer à une preuve publiée ou escalader vers
tllib-specs. Mesurer stabilité, robustesse des cas limites,
invariants et erreurs avant micro-optimisation.
Conserver la distinction stricte : exactitude mathématique publiée,
approximation numérique autorisée, performance, et propriétés
scientifiques unresolved. Une optimisation ne change pas les
conditions d'acceptation.

## Menaces et contrôles

Entrées : JSON, chemins et manifests non fiables ; taille, profondeur,
symlinks, épuisement de ressources, overflow, encodage. Ne jamais
exécuter le handoff. Références externes non résolues par réseau caché.
Providers Python/natifs : entrée/sortie validées, timeout/cancellation,
erreur structurée, ownership et réentrance ; un provider in-process
n'est **pas** un bac à sable contre code hostile — exécution non fiable
nécessite un processus isolé conçu explicitement et ne fait pas
partie de la garantie du cœur V1.

C++ : RAII, vérification des bornes, durées de vie, conversions,
ASan/UBSan, fuzzing des parseurs à risque ; TSan uniquement là
où les tests de concurrence sont compatibles.
Supply chain : dépendances vérifiées, licences, SBOM à la release,
source/artefacts et empreintes vérifiables, credentials à portée
minimale, pas de secrets dans le repo, politique de divulgation.
Aucun badge ou workflow ne remplace les preuves.

## Compatibilité

Version `tllib` selon SemVer, distincte du modèle du handoff.
Chaque release déclare la paire (commit tllib, SHA/fingerprint specs),
les cibles officiellement testées et les capacités réellement
prises en charge. Aucun nouveau TLC-FC ne devient supporté par magie.
Avant 1.0 : API source publique modifiée seulement avec note de
migration, pas de promesse d'ABI C++ universelle. Après 1.0 :
SemVer gouverne les API publiques ; changement ABI traité comme
potentiellement breaking si ABI promise sur un périmètre explicitement
publié. ABI de plugins futurs : séparée, versionnée, pas supposée.
Compatibilité Python et metadata/wheels gérées explicitement.
Versions des contrats scientifiques gouvernées **par tllib-specs** ;
une modification scientifique requiert une nouvelle provenance,
diff et revue avant d'être consommée.

## CI progressive sans sur-ingénierie précoce

Phase **pré-implémentation** : markdown/lint de documents ciblés
si utile, liens et métadonnées, pas de job de build factice.
Quand #246/#249 existent : smoke natif/CTest ciblés.
Quand #257 existe : installation smoke Python.
Lorsque catalogue/runtime/conformance existent : validations par
impact et tests full catalogue sur main/release. Docs-only ne
doit pas compiler le runtime ; dépendances transverses du core
déclenchent les tests consommateurs ; jobs release prouvent tous
les artefacts réellement promis. Ne pas annoncer nightly/fuzz/
benchmarks verts avant construction et exécution.

## Critères de clôture

#13 : threat model + tests négatifs + audit supply chain et release.
#14 : matrice de compatibilité testable + exemples de migration.
#243 : workflows démontrant précisément la couverture annoncée.
#249 : commandes CTest/format/analyse réellement exécutées.
Toutes ces issues **restent ouvertes** jusqu'aux preuves attendues.
