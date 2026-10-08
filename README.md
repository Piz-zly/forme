# Forme

Application personnelle de suivi du poids, des repas, de la musculation et de la
qualité des produits alimentaires. Quatre onglets, une seule application, écrite
en HTML, CSS et JavaScript sans framework.

- **Application** : https://piz-zly.github.io/forme/
  (à ouvrir dans Chrome sur Android, puis « Ajouter à l'écran d'accueil »)
- **Les données restent sur le téléphone.** Aucun compte, aucun serveur.
  Ne jamais déposer d'export de données dans ce dépôt, qui est public.

## Pour s'y retrouver

| | |
|---|---|
| `CLAUDE.md` | Synthèse du projet et méthode de travail — **à lire en premier** |
| `docs/` | Documentation détaillée ([sommaire](docs/00-sommaire.md)) |
| `src/` | Les sources, c'est ici qu'on modifie |
| `index.html` | L'application assemblée — générée, ne pas éditer |
| `tools/` | Scripts de fabrication des images |
| `tests/` | Tests de bout en bout |

## Construire

```bash
./src/build.sh     # après avoir monté APP_VER dans src/js1.js
```

## Licences

Code écrit pour ce projet. Les éléments tiers — illustrations, schémas
anatomiques, lecteur de codes-barres, données produits, polices — sont listés
avec leur licence dans [THIRD_PARTY.txt](THIRD_PARTY.txt).
