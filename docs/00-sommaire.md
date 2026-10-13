# Documentation de Forme — sommaire

Commencer par **`../CLAUDE.md`** à la racine : nature du projet, règles,
arborescence et méthode de travail. Les fichiers ci-dessous détaillent chaque
aspect.

| # | Fichier | Ce qu'on y trouve |
|---|---|---|
| 1 | [01-projet.md](01-projet.md) | L'utilisateur, pourquoi cette application, ce qui est fait, ce qui ne le sera pas et pourquoi, l'historique des demandes |
| 2 | [02-architecture.md](02-architecture.md) | Organisation du code : ordre des fichiers, vues, actions, feuilles, style, composants particuliers, pièges |
| 3 | [03-donnees.md](03-donnees.md) | Où vivent les données, forme de l'objet, enregistrement, synchronisation, export, migrations |
| 4 | [04-images.md](04-images.md) | Origine et licences des images, fabrication des illustrations et de la coloration des muscles, ajout d'un exercice |
| 5 | [05-build-publication.md](05-build-publication.md) | Construire, tester, publier, mettre à jour le téléphone, service worker, installation |
| 6 | [06-journal.md](06-journal.md) | Historique des versions |
| 7 | [07-a-faire.md](07-a-faire.md) | Le prochain sujet, les demandes en attente, les dettes techniques |

## Les trois réflexes

1. **On modifie `src/`, jamais `index.html` ni `forme.html`** : ils sont générés.
2. **On monte `APP_VER` dans `src/js1.js`** avant de construire, sinon la mise à
   jour ne part pas sur le téléphone.
3. **On n'embarque rien dont on n'a pas les droits**, et les données de
   l'utilisateur ne quittent pas son téléphone.
