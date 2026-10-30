# Phase A — Interopérabilité des buffers Python (#252)

**Décision :** aucune dépendance NumPy obligatoire et aucun DLPack/GPU dans
ce jalon. Les besoins validés par #250 et #253 sont CPU 1D/2D.

`tllib.inspect_buffer(object)` emprunte `Py_buffer` via le protocole buffer
Python **pendant l'appel natif uniquement**. Il valide dtype (`int32`,
`float64` natifs), forme, strides, contiguïté C ou Fortran, alignement
et étendue physique. Le retour `BufferInfo` immuable contient les
métadonnées **sans exposer de pointeur natif** ; aucune vue persistante
n'est retournée. Le `PyBuffer_Release` s'exécute avant le retour.
Un test natif de comparaison d'alias de buffers, sans divulguer d'adresse,
prouve l'inspection sans copie. Il ne constitue pas une promotion
d'ownership. Les tests vérifient les références `memoryview` qui
possèdent légalement leur exporter.

Les vues non contiguës et les dtype non natifs sont **refusés** par code
structuré, jamais copiés silencieusement. L'utilisateur effectue si besoin
une copie explicite, par exemple `numpy.ascontiguousarray` avant l'appel.
Une conversion perdant la mutabilité/shape n'est jamais annoncée zero-copy.
Aucun gestionnaire de device ni runtime tensoriel général n'est ajouté.

Le propriétaire Python doit rester vivant pour tout appel natif qui emprunte
ce buffer ; les futures APIs réutiliseront cette frontière centralisée
plutôt que réécrire des conversions par domaine. DLPack est **reporté**,
car aucune nécessité d'échange de device, capsule ou synchronisation n'est
démontrée par le snapshot actuel. La décision sera réévaluée seulement
après une acceptation TLC-FC demandant effectivement cet échange.

## Copie volontaire vérifiée

Le test `test_buffers.py` part d'une vue NumPy non contiguë refusée,
construit une copie **explicitement** via `numpy.ascontiguousarray`,
prouve l'absence d'aliasing avec `numpy.shares_memory` et le contrôle
natif de pointeurs (sans divulguer d'adresse), puis constate que
`inspect_buffer` emprunte cette nouvelle allocation sans copier
à nouveau. Les valeurs d'entrée sont préservées.
