# ADR 0001 — Architecture et frontière des dépôts

Statut : accepté.

## Décision

`tllib` utilise une architecture modulaire ports/adaptateurs.

- `core` définit les primitives publiques indépendantes des domaines.
- `shared` implémente uniquement les contrats structurels partagés publiés.
- `domains` contient les types et opérations propres à chaque domaine.
- `providers` définit les capacités externes injectées explicitement.
- `specs` gère la révision immuable de `tllib-specs`.
- `conformance` lit le handoff comme données non fiables et produit des
  preuves de couverture.
- `discovery` expose seulement les capacités explicitement enregistrées.
- `adapters` contient les intégrations concrètes.

`core` ne dépend d'aucun domaine. Un domaine ne dépend pas d'un adaptateur ou
d'une infrastructure concrète. Les dépendances entre domaines doivent passer
par un contrat partagé ou un port explicite.

## Frontière normative

`tllib-specs` reste l'unique autorité sur :

- la science et les définitions ;
- les identifiants TLC-FC ;
- les contrats et critères d'acceptation ;
- les statuts scientifique et d'exécution ;
- les contrats partagés ;
- la population publiée et sa version.

`tllib` décide uniquement de la représentation Python et des mécanismes
d'exécution nécessaires pour respecter ces contrats.

Le runtime ne dépend jamais de `maths/`, `registry/` ou d'un IR intermédiaire.
Il consomme le handoff publié au SHA enregistré dans `specs.lock.json`.

## Conséquences

- aucune découverte implicite de domaines ou de fournisseurs ;
- aucun comportement scientifique par défaut ;
- toute capacité conditionnelle échoue explicitement sans fournisseur ;
- toute fonctionnalité structurelle reste représentable sans fausse exécution ;
- une nouvelle entrée du catalogue amont apparaît comme écart tant qu'elle
  n'est pas explicitement qualifiée dans `tllib`.

Les règles d'import sont contrôlées par les tests d'architecture.
