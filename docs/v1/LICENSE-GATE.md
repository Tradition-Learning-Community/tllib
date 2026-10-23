# Statut du préalable légal — tllib V1

## Décision de gouvernance (issue #263)

**Tradition Learning Community ASBL** gouverne et maintient `tllib`
en tant que projet open source. L'association a demandé l'adoption de
la licence **Apache License 2.0**, cohérente avec celle déjà publiée
dans `tllib-specs`.

Le dépôt publie :
- [LICENSE](../../LICENSE) : texte complet Apache-2.0, repris à
  l'identique du fichier de licence de `tllib-specs` ;
- [NOTICE](../../NOTICE) : attribution du projet et droits des tiers ;
- [DCO](../../DCO) : certification des contributions sous DCO v1.1 ;
- [GOVERNANCE.md](../../GOVERNANCE.md) : contrôle du projet, droits
  d'auteur et politique de revue ;
- [CONTRIBUTING.md](../../CONTRIBUTING.md) : procédure des contributeurs
  et sign-off ;
- [SECURITY.md](../../SECURITY.md) : remontée confidentielle des incidents.

**Licence et contribution :** les PR externes peuvent être accueillies
après intégration de ces fichiers sur `main` et acceptation des règles
de revue. Aucun CLA ou cession automatique des droits n'est exigé.
Les droits d'auteur des contributions restent attribués à leurs auteurs
sans accord distinct. La structure associative du projet n'est pas
une cession de droits par les contributeurs.

**Vérifications et limites :**
- `tllib-specs` publie déjà Apache-2.0 et un guide scientifique ;
  il n'est pas nécessaire de modifier son contenu normatif.
- Les fichiers de source/paquet installables de `tllib` n'existent
  pas encore : lors de leur création, ils devront exposer SPDX
  `Apache-2.0`, inclure LICENSE/NOTICE et conserver les notices tierces.
- Le dépôt nettoyé ne porte actuellement aucun runtime de domaine ;
  l'historique, le contenu réutilisé et les dépendances futures
  restent sujets à provenance/licensing review lorsqu'ils sont
  réintroduits. Ce document ne prouve pas la chaîne de propriété
  des anciens commits ou des travaux de tiers.
- L'ASBL doit conserver ses propres preuves statutaires/de délégation
  de droits ; la déclaration du propriétaire du projet ne constitue
  pas un audit légal indépendant.

## Ne pas confondre les gates

La gate **licence/contribution** #263 peut être close après fusion et
contrôle des fichiers de licence, provenance et gouvernance ci-dessus.
Cela ne clôt ni #247 (licences des dépendances réelles), ni #51
(parcours contributeur testé), ni #261 (labels, jalons et ready
appliqués), ni #11 (packaging/release).

Cette gate ne nécessite aucune implémentation scientifique ou CI lourde.
