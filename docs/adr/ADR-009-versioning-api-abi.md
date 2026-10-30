# ADR-009 — Versioning, API et ABI

**Statut : accepté et vérifié pour les fondations 0.1.0 ; release V1 non publiée.**

- SemVer `0.1.0` pour CMake et wheel ; Python CPython 3.12 déclaré
  en metadata tant que seul cet interpréteur dispose de preuves.
  Versions des specs totalement distinctes.
- Paire tllib/specs vérifiée par `tools/compatibility.py`, SHA/empreinte
  verrouillés et métadonnées générées concordantes.
- Stabilité source C++ publique gérée par dépréciation/migration.
- Pas de garantie ABI C++ universelle pendant 0.x ; ABI/plugin stable
  future seulement à frontière explicitement versionnée.
- Python : dépréciations, types, wheels et plateformes publiés
  dans matrice de support.
- Nouveau contrat/TLC-FC specs : `tools/specs_sync.py` produit un diff
  déterministe et plan de migration, toute différence exige une revue ;
  aucune mise à jour de lock ou implémentation présumée.
- Une dépréciation documente symbole, version d'annonce, remplacement
  et période de retrait ; chaque breaking change exige une note de
  migration/release dans la PR. L'API 0.x n'a aucune ABI universelle.
- Voir `docs/v1/SECURITY-QUALITY-COMPATIBILITY.md`, #14, #244.
