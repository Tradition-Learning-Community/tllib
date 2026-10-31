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
Les règles de sélection d'une tâche, les preuves requises et les limites de support sont expliquées dans :
[registre](docs/v1/PREPARATION-STATUS.md) et
[gouvernance](docs/v1/READINESS-AND-GOVERNANCE.md), [parcours concrets](docs/v1/CONTRIBUTOR-QUICKSTART.md) et [revue/fusion](docs/v1/REVIEW-AND-MERGE.md).

## Respect et coopération

Contributions publiques courtoises, critiques techniques argumentées, aucune attaque personnelle, respect de la confidentialité des signalements de sécurité. En cas de comportement inapproprié ou de conflit d'intérêts, solliciter une revue indépendante par les mainteneurs désignés par l'ASBL. La discussion scientifique doit rester fondée sur les preuves et la traçabilité.

## Signaler un problème sans contribuer de code

Le formulaire **Défaut logiciel tllib** permet de signaler un bogue autonome dans ce dépôt, sans epic ou issue parent. Pour un problème scientifique normatif, utiliser les formulaires de `tllib-specs`. Une vulnérabilité exploitable est signalée selon [SECURITY.md](SECURITY.md), pas en issue publique.

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

## Exécuter les tests et installer les fondations

Les commandes de clone, build C++20, consommateur CMake installé, wheel Python native, typing, tests de parité, tooling/specgen et contrôle de conformité sont regroupées dans le [guide des parcours contributeurs](docs/v1/CONTRIBUTOR-QUICKSTART.md) ; les règles de [revue et fusion](docs/v1/REVIEW-AND-MERGE.md) sont communes.

**Environnement qualifié actuellement** : Ubuntu 24.04 x86-64, C++20 et CPython 3.12. CMake >= 3.27 ; le preset `dev` requiert Ninja. Le paquet Python `tllib` (version de préparation `0.1.0`) est installable depuis une wheel CMake locale et par installation editable ; il ne s'agit **pas** d'une release scientifique V1 ni d'une wheel distribuée sur PyPI. Les autres plateformes ne sont pas présumées supportées.

La CI de fondation effectue effectivement build C++/CTest, consommateur CMake externe, module CPython et parité structurelle, wheel/install propre, tests négatifs des specs, qualité et sanitizers sur les chemins modifiés. L'outil `tools/specs_pipeline.py` exige un checkout `tllib-specs` **exactement verrouillé** ; la conformité des 694 TLC-FC n'est pas acquise : 693 sont non implémentées et une feature reste bloquée par les specs. Les tests doivent être adaptés au changement ; les PR uniquement documentaires ne prétendent pas avoir exécuté CMake.

Les issues de domaine et lots restent à **qualifier individuellement** via `status:ready` : aucune décision d'architecture générale ne doit être laissée aux contributeurs. Les contributions documentation/QA/tooling peuvent être proposées sans travail C++ pour des tâches suffisamment autonomes et testables.

Pour signaler un problème logiciel indépendant, utiliser le formulaire **Défaut logiciel tllib**. Les questions normatives relèvent uniquement de `tllib-specs`.
