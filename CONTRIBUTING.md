# Contribuer à tllib

**Tradition Learning Community ASBL** porte et gouverne le projet open source `tllib`, publié sous **Apache-2.0**. Les contributions de personnes externes sont bienvenues dans les domaines scientifique, C++, Python, tooling, documentation et QA, à condition de suivre les frontières d'autorité et les critères de préparation. Voir [LICENSE](LICENSE), [NOTICE](NOTICE) et [GOVERNANCE.md](GOVERNANCE.md).

## Licence et certification des contributions (DCO)

- Les contributions destinées à `tllib` sont proposées sous **Apache-2.0**, sauf accord séparé explicitement approuvé. N'incluez pas d'œuvre de tiers incompatible ou sans autorisation.
- Chacun signe **ses propres commits** au titre du [Developer Certificate of Origin v1.1](DCO) : `git commit -s -m "..." `. Cela ajoute `Signed-off-by: Nom <adresse>` dans le message. Pour un commit déjà créé, `git commit --amend -s` si c'est votre commit ; ne jamais signer au nom d'autrui.
- Le sign-off atteste l'origine et les droits nécessaires : **il ne transfère pas le droit d'auteur à l'ASBL**. L'ASBL gère le projet et ses publications ; chaque personne conserve ses droits sans cession écrite séparée.
- Les noms/adresses figurant dans l'historique Git sont publics ; choisissez une adresse appropriée à cet usage, éventuellement une adresse `noreply` GitHub. Ne fournissez pas de données personnelles inutiles.
- **Pas de CLA ni de cession de droits obligatoire par défaut**. Une éventuelle cession particulière est un acte explicite, non implicite dans la PR.
- Les relecteurs doivent vérifier les sign-offs et notices de licences à la revue. Il n'existe pas encore de CI DCO automatisée, et un contrôle humain ne doit pas être présenté comme automatisé.


`tllib` est en **phase pré-implémentation V1**. Ne démarrer aucun domaine
sans issue autonome `status:ready` et toutes les dépendances satisfaites.
Les politiques de préparation sont proposées à l'adoption :
[registre](docs/v1/PREPARATION-STATUS.md) et
[gouvernance](docs/v1/READINESS-AND-GOVERNANCE.md).

## Respect et coopération

Contributions publiques courtoises, critiques techniques argumentées, aucune attaque personnelle, respect de la confidentialité des signalements de sécurité. En cas de comportement inapproprié ou de conflit d'intérêts, solliciter une revue indépendante par les mainteneurs désignés par l'ASBL. La discussion scientifique doit rester fondée sur les preuves et la traçabilité.

## Avant toute contribution

1. Lire [le contrat produit](docs/v1/PRODUCT-CONTRACT.md), #52 et les ADR.
2. Vérifier le dépôt autoritaire : science dans `tllib-specs`,
   logiciel et API dans `tllib`.
3. Sélectionner une issue réellement autonome et non bloquée ;
   un epic domaine n'est pas une tâche prête par lui-même.
4. Pour les tâches normatives-consommatrices, utiliser le snapshot
   `tllib-specs` verrouillé et les packages autonomes de `handoff/`.
5. Lire `contract.json`, `acceptance.json`, les contrats partagés ;
   ne jamais inventer formule, valeur, provider ou comportement manquant.

## Parcours

- **C++** : core, données, runtime, providers, domaines, performance ;
  références : [build](docs/v1/DEPENDENCIES-BUILD-POLICY.md),
  [concurrence](docs/v1/CONCURRENCY-PYTHON-API.md).
- **Python/bindings** : API et typing, NumPy/DLPack, erreurs, parité ;
  [contrat Python](docs/v1/CONCURRENCY-PYTHON-API.md).
- **Tooling Python** : snapshot/specgen/conformance/migration ;
  [contrat specs](docs/v1/SPECS-LOCK-AND-CONFORMANCE.md).
- **Documentation, QA et sécurité** : tests, preuves, audit,
  [qualité](docs/v1/SECURITY-QUALITY-COMPATIBILITY.md).
- **Recherche scientifique** : seulement dans `tllib-specs` par
  décision normative revue, pas en modifiant un contrat localement.

## Pull requests

Une PR, une issue autonome. Préciser :
- issue et dépendances ; périmètre exact/TLC-FC ;
- SHA complet du snapshot de specs si applicable ;
- obligations d'acceptation (y compris négatives) et changements ;
- commandes de tests **réellement exécutées**, résultats et limites ;
- analyse ownership, concurrence, précision, compatibilité et sécurité
  selon le changement ;
- preuve de parité C++/Python lorsqu'applicable ;
- blockers scientifiques renvoyés vers `tllib-specs`.

Une PR de domaine ne peut introduire ni politique d'architecture locale,
ni tolérance numérique arbitraire, ni fallback provider, ni moteur
scientifique Python alternatif.

## Exécuter les tests

**Il n'existe actuellement pas encore de configuration native CMake,
de wheels ni de suite CTest exécutables**. Les commandes futures
seront publiées et validées par #246/#249/#257 ; les inventer ici
induirait le contributeur en erreur. Les tests documentaires peuvent
être revus sans démarrer une CI de compilation.
