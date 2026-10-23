# Definition of Done — tllib V1

V1 est publiée uniquement si toutes les sections sont vraies sur le même commit
`tllib` et le même snapshot `tllib-specs`.

## Specs
- snapshot immuable + fingerprint vérifié ;
- 100 % domaines/features découverts dynamiquement ;
- aucun support implicite.

## Runtime
- API C++ installable/documentée ;
- 8/8 shared contracts conformes ;
- registry/dispatcher/providers opérationnels ;
- aucun runtime read de sources internes tllib-specs.

## Chaque TLC-FC
- identité/provenance/statut connus ;
- décision runtime explicite ;
- acceptance/conformance liée ;
- aucune science inventée.

### Executable
- implémentation native ;
- acceptance réussie ;
- erreurs/invariants testés.

### Conditional
- capability/provider contract ;
- validation entrée/sortie ;
- absence de provider = erreur stable.

### Structural/unresolved
- représentation/validation ;
- inspection/sérialisation ;
- exécution refusée explicitement ;
- unresolved reste unresolved.

## Python
- wheels supportées installables ;
- API typée/documentée ;
- erreurs natives traduites ;
- NumPy/DLPack lorsque requis ;
- parity tests.

## Qualité/sécurité/performance
- GCC/Clang/MSVC sur plateformes supportées ;
- warnings/format/static analysis ;
- ASan/UBSan ;
- fuzz targets critiques ;
- benchmark baseline pour chemins critiques ;
- threat model, dépendances/licences/SBOM ;
- aucun secret.

## Packaging/docs/release
- package C++ consommable via CMake ;
- paquet source reproductible ;
- wheels Linux/Windows/macOS selon matrice supportée ;
- tests sur artefacts installés ;
- architecture/ADR/guides/API docs publiés ;
- rapport final avec SHAs, population, conformance, toolchains, artefacts,
  SBOM/attestations et limitations héritées des specs.
