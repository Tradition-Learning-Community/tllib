# Security policy

`tllib` est le runtime Python qui consomme les handoffs publiés par
`tllib-specs`.

## Périmètre

Sont notamment concernés :

- chargement de handoff permettant traversal, symlink escape ou contenu non
  déclaré ;
- contournement du verrou de spécifications, SHA ou empreinte ;
- confusion d'identité TLC-FC ou de version ;
- activation implicite d'un provider ou appel réseau caché ;
- validation insuffisante des entrées/sorties d'un provider ;
- chaîne de build, dépendances ou publication compromise ;
- exposition de secrets dans les workflows ou artefacts.

Une erreur scientifique ou normative dans un handoff doit être signalée dans
`tllib-specs`. Une vulnérabilité propre au runtime est signalée ici.

## Signalement

Ne publiez pas de détails exploitables dans une issue publique. Utilisez le
signalement privé GitHub lorsqu'il est disponible, avec le commit affecté,
l'impact, les étapes de reproduction et, si connu, un correctif proposé.
