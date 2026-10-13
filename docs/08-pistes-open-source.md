# 8. Pistes open source (proposées le 13 octobre 2026)

Cinq projets libres repérés pour améliorer Forme. **Intégrés : 1 (Ciqual), en 2026.10.13-1 ; 2 (exercices), en 2026.10.13-2 ; 3 (Fuse.js), en 2026.10.13-4.**
**Non retenu : 4 (AutoAnimate)**, remplacé par un outil maison en 2026.10.13-5 (voir plus bas).
Les autres restent à faire.
Avant chaque intégration : respecter les règles de `CLAUDE.md` (pas de dépendance
sans raison forte, fichiers copiés en local dans `vendor/` et jamais chargés depuis
un CDN — l'application doit marcher hors ligne —, licence ajoutée à `THIRD_PARTY.txt`,
version montée, tests).

| # | Projet | Licence | Pour quoi faire dans Forme |
|---|---|---|---|
| 1 | **Table Ciqual (ANSES)** — ciqual.anses.fr | Licence Ouverte Etalab (citer la source) | Base d'aliments : 3 484 aliments français, 74 constituants, mise à jour du 19/11/2025. Passer de 321 aliments à plusieurs milliers. |
| 2 | **free-exercise-db** — github.com/yuhonas/free-exercise-db | Unlicense (domaine public) | 800+ exercices en JSON : muscles principaux et secondaires, niveau, matériel, consignes pas à pas (en anglais). |
| 3 | **Fuse.js** — github.com/krisk/Fuse | Apache-2.0 | Recherche tolérante aux fautes de frappe (« poulé » → poulet). Les accents sont déjà gérés par `normTxt` dans `js2f.js`. Utile surtout avec la base Ciqual. |
| 4 | **AutoAnimate** — github.com/formkit/auto-animate | MIT | Esthétique : animations douces quand une ligne apparaît, disparaît ou se déplace (repas ajouté, série validée, produit rangé). Une ligne de code par liste. |
| 5 | **canvas-confetti** — github.com/catdad/canvas-confetti | ISC | Chantier « Motivation » : célébrer un palier de 2,5 kg franchi, une série de jours, une semaine dans l'objectif. Activer `disableForReducedMotion: true`. |

## Notes d'intégration

**Ciqual — fait en 2026.10.13-1.** Fichier utilisé : `Table Ciqual 2025_FR_2025_11_03.xlsx`
(https://doi.org/10.57745/RDMHWY, fichier n° 666260 sur entrepot.recherche.data.gouv.fr).
`tools/gen_ciqual.py` le lit sans dépendance et écrit `src/js2g.js` (3 203 aliments, 256 ko ;
écartés : eaux, sels, aliments infantiles, aliments sans calories ou sans macros). Les 321
aliments familiers restent en tête ; Ciqual en grammes seulement. Pas encore fait : remplacer
les valeurs des 321 par celles de Ciqual, ajouter des unités usuelles aux aliments Ciqual.
Notes d'origine ci-dessous.

Télécharger l'export (XLS/XML) depuis ciqual.anses.fr ou
recherche.data.gouv.fr, ne pas le mettre dans le dépôt s'il est lourd : le lire
avec un nouveau script `tools/gen_ciqual.py` qui produit le même format que
`js2e.js` (nom, section.sous-section, kcal / protéines / glucides / lipides pour
100 g, unités usuelles). Garder seulement les colonnes utiles pour rester léger.
Les noms Ciqual sont techniques (« Œuf, cru ») : garder les noms familiers des
321 aliments actuels quand ils existent, Ciqual complète. Ajouter la mention
« Source : Anses, Table Ciqual » dans `THIRD_PARTY.txt` et dans la fiche aliment.

**Exercices — fait en 2026.10.13-2**, avec une seconde source : **exercises-dataset**
(github.com/hasaneyldrm/exercises-dataset, 1 324 exercices, consignes en 10 langues dont le français,
licence MIT pour le texte et les données ; ses images et GIF sont © Gym visual et ne sont **pas**
utilisés). Comparaison sur 20 exercices : nos 60 exercices venaient déjà de free-exercise-db (mêmes
identifiants et muscles) ; le français d'exercises-dataset est naturel et tutoie, mais avec des
erreurs (prises contradictoires, « machine à traîneau », « câble » pour « poulie », curl marteau faux) ;
son champ « muscle_group » n'est pas fiable. Retenu : liste et muscles de free-exercise-db, consignes
françaises d'exercises-dataset corrigées, équipement d'exercises-dataset, 115 exercices ajoutés
(sélection, pas tout), noms écrits par nous. Voir `tools/gen_exercices.py`. Notes d'origine :

Ne pas embarquer ses 2 600 images (trop lourd, et le style
diffère de `ill/`). Prendre les données (muscles, consignes, niveau), traduire les
consignes en français avec des mots simples, et les rattacher aux exercices
existants via `tools/exercices_map.py`. Attention aux deux systèmes
d'identifiants déjà notés dans `07-a-faire.md`.

**AutoAnimate — non retenu (13 octobre 2026).** Deux raisons : l'appli redessine l'écran entier
à chaque action (`render`), alors qu'AutoAnimate observe un conteneur qui doit rester en place ; il
n'aurait rien animé sans refaire le dessin de tous les onglets. Et il n'existe qu'en module (aucune
version navigateur classique, même ancienne). Remplacé par `src/js1b.js`, une quarantaine de lignes
qui utilisent la même technique (mesurer avant, faire glisser après) autour de `render`.

**Fuse.js, canvas-confetti.** Copier le fichier minifié dans
`vendor/`, l'ajouter au service worker et à `build.sh`, licence dans
`THIRD_PARTY.txt`.

## Ordre conseillé

1 puis 3 (la base d'aliments d'abord, la recherche floue ensuite), 5 avec le
chantier Motivation, 4 quand l'ambiance définitive est choisie, 2 en dernier.
