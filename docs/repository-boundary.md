# Responsabilités de `tllib-specs` et `tllib`

| Sujet | `tllib-specs` | `tllib` |
| --- | --- | --- |
| Science, définitions, équations | Autorité | Ne modifie pas |
| Identifiants TLC-FC | Autorité | Consomme |
| Handoff, contrats, acceptation | Publie et certifie | Charge et vérifie |
| Statuts scientifique/exécution | Autorité | Représente fidèlement |
| Contrats partagés | Définit/versionne | Implémente en types Python |
| Catalogue des domaines/features | Autorité | Compare au support runtime |
| API Python | Hors périmètre | Autorité |
| Providers externes | Déclare le besoin | Définit l'interface/injection |
| Algorithmes runtime | Seulement si normatifs dans le handoff | Implémente sans invention |
| Packaging/PyPI | Hors périmètre | Autorité |
| CI de spécification | Autorité | Ne duplique pas |
| CI runtime | Hors périmètre | Autorité |

## Flux

1. `tllib-specs` publie un snapshot validé.
2. `tllib` épingle son SHA et l'empreinte du catalogue.
3. `tllib` lit uniquement le handoff comme contrat d'implémentation.
4. Une évolution amont est comparée avant toute mise à jour du verrou.
5. Une ambiguïté ou contradiction normative est renvoyée à `tllib-specs` ;
   elle n'est pas résolue localement dans `tllib`.

Les issues d'implémentation doivent vivre dans `tllib`. Les issues
`tllib-specs` qui concernent la bibliothèque servent de suivi amont et sont
clôturées lorsque la preuve de conformité existe dans le dépôt `tllib`.
