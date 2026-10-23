# Préalable légal à l'ouverture des contributions

Constat au 23 octobre 2026 : aucun fichier `LICENSE` n'existe dans
l'arbre `main` de tllib à cette date. tllib-specs porte Apache-2.0,
mais son fichier LICENSE ne licencie pas implicitement tllib.

**Issue de décision : #263.** Recommandation : Apache-2.0 si les
titulaires des droits le confirment et si l'historique/composants
sont compatibles. Ne pas insérer par simple inférence une licence
qui pourrait avoir un autre propriétaire ou des exceptions.

Avant de lancer des contributions externes de code :
1. confirmer l'autorité juridique de la licence ;
2. ajouter LICENSE et éventuelle NOTICE ;
3. documenter politique des contributions (DCO ou CLA si justifié) ;
4. vérifier les licences des dépendances retenues ;
5. refléter le résultat dans packages et README.

Cette gate est administrative, non scientifique, et ne nécessite
ni compilateur ni matrice CI. Ne pas considérer les 36 domaines
`ready` pour contributions externes tant qu'elle n'est pas satisfaite.
