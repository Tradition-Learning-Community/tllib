# Rapport de conformité des Feature Handoff Packages

Le chargeur `tllib.conformance` lit uniquement les packages sous
`handoff/features/`. Il refuse les liens symboliques, les sorties du répertoire
racine, les fichiers de plus de 1 Mo, le JSON invalide et les scénarios dont les
champs requis ne sont pas publiés. Les scénarios chargés sont immuables.

Depuis la racine de `tllib`, lorsque `tllib-specs` est un dépôt frère :

```powershell
python -m tllib.conformance --report build/conformance.json
```

Pour une exportation placée ailleurs, indiquez explicitement sa racine
`handoff/` :

```powershell
python -m tllib.conformance --handoff C:\chemin\vers\handoff --report build/conformance.json
```

Le rapport est un JSON déterministe : il ne contient ni horodatage ni donnée
volatile. Chaque scénario contient son identifiant TLC-FC, son opération, son
état et une justification.

- `covered` exige une `ImplementationBinding` explicite qui cite le scénario ;
- `not_covered` signifie que l’implémentation TLC-FC est enregistrée, mais que
  ce scénario n’est pas encore associé à un test ;
- `blocked` signifie qu’aucune implémentation TLC-FC n’est enregistrée, ou
  qu’un blocage explicite est documenté.

Ainsi, l’outil ne transforme jamais une absence d’implémentation ou de test en
couverture implicite.
