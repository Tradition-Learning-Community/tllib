# ADR 0002 — API publique, types et erreurs

Statut : accepté.

## Principes

L'API publique représente le handoff sans exposer l'organisation interne des
fichiers de tllib-specs.

- les identités TLC-FC utilisent FeatureId ;
- les domaines utilisent DomainId ;
- les versions utilisent Version ;
- les statuts scientifique et d'exécution utilisent des enums fermées ;
- les erreurs ont un code stable et peuvent porter le TLC-FC concerné ;
- les résultats sont immuables ;
- la sérialisation JSON est déterministe ;
- aucune donnée non validée ne devient implicitement une identité ou un statut.

Les API sont synchrones par défaut. Une API asynchrone ne sera ajoutée que
lorsqu'un contrat runtime le justifie ; elle ne doit pas changer la sémantique
du handoff.

## Erreurs communes

Le cœur expose ValidationError, ProviderRequiredError,
FeatureNotExecutableError, VersionIncompatibleError et
InvariantViolationError.

Une erreur liée à une fonctionnalité doit transporter son FeatureId quand
l'appelant dispose de cette information.

## Compatibilité

Les symboles exportés depuis tllib.__init__ constituent la surface publique.
Les modules internes peuvent évoluer tant que cette surface et les contrats
documentés restent compatibles. Toute rupture publique exige une décision de
version et une migration explicite.
