# 9. Nettoyage du code — rapport d'analyse

Analyse faite le 7 novembre 2026 sur la branche `nettoyage`, partie de `main` (version 2026.10.15-1).
Corrections faites le même jour, version **2026.11.07-1** : voir « Ce qui a été fait » en fin de fichier.
Les tableaux ci-dessous sont l'analyse d'origine.

Classement de chaque point :

- **Sûr** : aucun effet visible (ou un vrai bug corrigé), facile à vérifier.
- **À confirmer** : change un comportement, touche aux données, ou il reste un doute.
- **À laisser** : trop risqué ou trop lourd pour le gain.

## Point de départ

- Les 16 tests (`tests/t4.py` à `t19.py`) passent tous, sans erreur JavaScript.
- Console du navigateur (les quatre onglets, leurs sous-onglets et les Réglages, sur `index.html` et
  `forme.html`) : aucun message, aucune erreur, aucun fichier introuvable.
- Poids : `index.html` 865 424 octets, `forme.html` 869 630 octets.
- Outils utilisés, hors du dossier : ESLint (variables non déclarées, doublons, code mort) sur les sources
  assemblées comme le fait `build.sh`, et un script d'analyse de la feuille de style.

## A. Doublons

Aucune fonction n'est définie deux fois et aucune action (`A[...]`, `I[...]`) n'est enregistrée deux
fois : le piège « la dernière gagne sans prévenir » ne se produit nulle part.

| # | Où | Problème | Proposition | Classement |
|---|---|---|---|---|
| A1 | `js1.js`, `chart` (`dstr`) | Recalcule à la main la date d'un jour, ce que fait déjà `xToDate` juste en dessous. | Utiliser `xToDate`. | Sûr |
| A2 | `js2.js`, `addSheet` | Recherche le nom du repas à la main, ce que fait déjà `slotName` (`js2h.js`). | Utiliser `slotName`. | Sûr |
| A3 | `js2h.js` (`pl-add`), `js2d.js` (`rcNextSlot`), `js4.js` (`s-journal`) | Trois règles « quel repas selon l'heure » : les deux premières changent à 11 h et 16 h, celle du Scan à 10 h, 15 h et 18 h (avec collation). | Une seule règle commune. Mais le repas proposé par défaut changerait dans l'un des écrans. | À confirmer |
| A4 | `src/p1.html` (style) | 49 propriétés écrites une première fois puis redéfinies plus bas pour le même élément (restes de l'ancienne apparence, recouverts par l'ambiance actuelle). Elles ne servent plus. | Retirer les valeurs recouvertes. Gain ≈ 2 Ko, mais beaucoup de petites retouches dans le style. | À confirmer |
| A5 | `js4.js` l. 203, `js4c.js` l. 107 | Deux écouteurs « changement » à part, en plus du registre commun `I`. | Rien : ils marchent, les déplacer apporte peu. | À laisser |
| A6 | `tests/` | La fonction d'aide `check` est recopiée dans 13 tests. | Une aide commune pour les tests. Pas fait sans ton accord. | À confirmer |
| A7 | `js4b.js` | La bibliothèque du Scan est regroupée trois fois à chaque affichage. | Rien : 400 produits au plus, l'affichage reste rapide. | À laisser |

## B. Code qui ne sert plus

| # | Où | Problème | Proposition | Classement |
|---|---|---|---|---|
| B1 | `js3.js` l. 131, `A['g-start-r']` | Aucun bouton ne déclenche cette action (les routines démarrent par `g-rstart`). | Supprimer. | Sûr |
| B2 | `js5.js` l. 97, `A['share-open']` | Action vide, appelée nulle part. | Supprimer. | Sûr |
| B3 | `js4.js` l. 202, `I['s-files']=null` | Ligne sans effet (les photos sont traitées par l'écouteur juste en dessous). | Supprimer. | Sûr |
| B4 | `js3.js` l. 165, `VIEWS.gym_after=tick` | Écrasé par une autre définition l. 358. | Supprimer la première. | Sûr |
| B5 | `js1.js` l. 216 (`st`), `js3.js` l. 344-345 (`val`, `unit`) | Variables calculées et jamais lues. | Supprimer. | Sûr |
| B6 | `src/p1.html` (style) | Classes `.fab`, `.exinfo` (et ses `figure`, `img`, `figcaption`), `.lg` : aucun élément ne les porte. | Supprimer ces règles. | Sûr |
| B7 | `sw.js` | Exception pour Google Fonts, inutile depuis les polices en local (2026.10.15-1). | Supprimer l'exception. | Sûr |
| B8 | `img2/*-t.png` | 60 vignettes (240 Ko) jamais affichées ; `tools/gen_schemas_muscles.py` les fabrique encore. | Les supprimer, avec le bout de script qui les crée. Bonus : 60 fichiers de moins à joindre à la version Claude (limite de 255 par envoi). | À confirmer |
| B9 | `js2d.js` l. 163, `rcMark` | Une variable locale s'appelle `dn`, comme la fonction de dates `dn` : source de confusion. | La renommer. | Sûr |

Rien trouvé : aucun `console.log`, aucun reste d'AutoAnimate. Les liens Google Fonts ne restent que
dans `forme.html`, ce qui est voulu (la version Claude ne peut pas lire `vendor/fonts/`).

## C. Erreurs et fragilités

| # | Où | Problème | Proposition | Classement |
|---|---|---|---|---|
| C1 | `js1.js` l. 16, `num` | **Bug.** Un nombre de 1 000 ou plus est affiché avec une espace (« 2 200 ») et relu comme son premier morceau (2). Vérifié dans le navigateur : Réglages → Enregistrer sans rien changer fait passer l'objectif de 2 200 kcal à **2 kcal** et celui de 10 000 pas à **10 pas** ; un aliment du journal à 1 200 kcal ouvert puis enregistré devient **1 kcal**. Même chose avec « × 1,5 » ou « × 2 » au-delà de 1 000, les boutons +100 / +500 de l'ajout rapide au-delà de 1 000, « Calculer les valeurs » d'une recette perso au-delà de 1 000 kcal, une quantité scannée de 1 000 g ou plus, et des pas tapés « 8 400 » comme le suggère l'exemple. | Ignorer les espaces dans `num` : une ligne, qui corrige tous les écrans d'un coup. | Sûr (bug corrigé) |
| C2 | `js2.js` l. 354, barres de macros | Quand l'objectif de glucides vaut 0 (calories trop basses pour les réglages) et que rien n'est noté, la barre s'affiche pleine au lieu de vide (0 ÷ 0). | Barre vide dans ce cas. | Sûr (bug corrigé) |
| C3 | `js1.js` l. 30, chargement | Si les données du navigateur étaient illisibles, l'appli repart à zéro et les écrase au premier enregistrement, sans copie. | Garder une copie du texte illisible sous une seconde clé (`forme.v1.abime`) avant de repartir. | À confirmer |
| C4 | `js1.js` l. 80, `saveLocal` | Si le stockage du téléphone est plein, l'enregistrement échoue sans rien dire. | Afficher un message. Change ce qu'il voit, donc à décider. | À confirmer |
| C5 | `js4.js`, Restaurer | Seule vérification : le fichier vient de Forme. Un fichier abîmé à la main pourrait bloquer l'affichage. | Rien : ce sont ses propres sauvegardes. | À laisser |
| C6 | `js2h.js` l. 219, `weekView` | Les jours de planning de plus de 14 jours sont effacés pendant l'affichage de l'écran Semaine. | Rien : c'est voulu et ça marche. | À laisser |
| C7 | `src/build.sh` | Sous Windows, la partie style de `index.html` est écrite avec des fins de ligne Windows : la page change à chaque build même sans modification (10 lignes de différence). | Forcer les fins de ligne Unix dans cette étape. | Sûr |
| C8 | `tools/gen_recettes.py`, `gen_aliments.py`, `gen_decor.py` | Même problème : relancés sous Windows, ils réécrivent tout le fichier produit (502 lignes pour `p1.html`). Vérifié : le contenu produit est identique au fichier actuel, seules les fins de ligne changent. | Forcer les fins de ligne Unix à l'écriture. | Sûr |

Vérifié sans problème : pas de `toISOString`, « aujourd'hui » est toujours calculé en heure locale ;
aucun écouteur ajouté à chaque affichage ; aucune variable non déclarée ; les moyennes et pentes du
Poids sont protégées contre les listes vides ; les `JSON.parse` sont protégés.

## D. Cohérence du projet

| # | Où | Problème | Proposition | Classement |
|---|---|---|---|---|
| D1 | `sw.js`, liste `SHELL` | Tous les fichiers listés existent. `ill/`, `img2/` et `vendor/ocr/` sont mis en cache au premier usage. | Rien. | À laisser |
| D2 | `THIRD_PARTY.txt` | Complet, mais le point 9 est placé avant le point 8. | Remettre dans l'ordre. | Sûr |
| D3 | `CLAUDE.md`, `docs/` | La version 2026.10.15-1 (polices en local) n'est ni dans `06-journal.md` ni dans `CLAUDE.md` ; `vendor/fonts/` et `docs/00-sommaire.md` manquent dans `CLAUDE.md` ; `01-projet.md` parle encore de 60 exercices (175) ; `02-architecture.md` dit « trois sous-onglets » du Repas (cinq) ; `05-build-publication.md` ne cite que 4 tests sur 16 ; la partie « Dettes » de `07-a-faire.md` est dépassée (`paint.py` est déjà réglable, le journal et le Scan ont maintenant des tests). | Mettre à jour. | Sûr |
| D4 | `tools/gen_schemas_muscles.py` | Chemin absolu de l'ancien atelier (`/tmp/…`). Ses fichiers d'entrée ne sont pas dans le dépôt. | Passer le chemin en argument. Le script n'est pas relancé. | Sûr |
| D5 | `ill/`, `img2/` | Aucune illustration manquante, aucune en trop dans `ill/` (les 6 « secondes images » absentes sont celles des exercices tenus, voulu). Voir B8 pour `img2/`. | — | — |
| D6 | `js4.js` l. 50 | La version Claude charge le lecteur de codes-barres depuis un CDN (le téléphone utilise `vendor/`). | Rien : la page Claude ne peut pas lire `vendor/`, et elle n'a de toute façon pas la caméra en direct. | À laisser |
| D7 | `src/p1.html` | Le décor de fond (dessiné par `tools/gen_decor.py`) fait 100 Ko sur 142 Ko. | Rien : c'est l'apparence choisie. | À laisser |

Table Ciqual : `tools/gen_ciqual.py` a besoin du fichier Excel, absent ici ; il n'a pas été relancé.

## E. Données personnelles

Rien trouvé dans les fichiers suivis par git.

## Fautes d'orthographe dans l'interface

Aucune repérée à la lecture.

## Récapitulatif

| Catégorie | Sûr | À confirmer | À laisser | Total |
|---|---|---|---|---|
| A. Doublons | 2 | 3 | 2 | 7 |
| B. Code inutile | 8 | 1 | 0 | 9 |
| C. Erreurs et fragilités | 4 | 2 | 2 | 8 |
| D. Cohérence | 3 | 0 | 3 | 6 |
| E. Données personnelles | 0 | 0 | 0 | 0 |
| **Total** | **17** | **6** | **7** | **30** |

## Ce qui a été fait (version 2026.11.07-1)

Décisions de l'utilisateur : les 17 points sûrs, plus C3, C4, B8 et A6 ; A4 à condition que les captures
des quatre onglets soient identiques dans les trois ambiances ; A3 avec la règle du Scan partout.

| Point | Fait | Vérification |
|---|---|---|
| C1 nombres de 1 000 et plus | `num()` ignore les espaces | `tests/t20.py` : 2 200 kcal et 10 000 pas gardés après Enregistrer, aliment à 1 200 kcal gardé, « 8 400 » pas → 8400 ; le test échoue (8 contrôles) sur l'ancien code |
| C2 barre des glucides | vide quand l'objectif vaut 0 | barres mesurées dans le navigateur (0 px) |
| B1-B5, B7, B9 code inutile | retiré | tous les tests |
| A1, A2 doublons | `xToDate`, `slotName` | tous les tests |
| B6 style inutilisé | `.fab`, `.exinfo`, `.lg` retirés | captures identiques |
| A4 style recouvert | 48 propriétés et 3 règles vides retirées (1,2 Ko) | 33 captures (onglets, sous-onglets, Réglages, séance) × 3 ambiances identiques au pixel, rendu reproductible (3 séries de référence identiques) ; style calculé identique pour la série cochée, la barre de repos, la feuille des durées et le message — seules la jauge et l'horloge du repos diffèrent, parce que le temps passe |
| A3 repas de l'heure | `slotNow()` partout | `tests/t21.py`, horloge simulée à 9 h 59, 10 h, 14 h 59, 15 h, 17 h 59, 18 h, 23 h 30 |
| C3, C4 protection des données | copie `forme.v1.abime`, feuille d'alerte ; message si stockage plein | `tests/t22.py` |
| B8 vignettes `img2/*-t.png` | 60 fichiers retirés (240 Ko), script adapté | tous les tests ; aucune référence |
| C7, C8 fins de ligne | `build.sh` et trois générateurs écrivent en fins de ligne Unix | build depuis `main` : contenu identique ; générateurs relancés : aucun fichier modifié |
| D4 chemin absolu | `FORME_ATELIER` | syntaxe vérifiée, script non relancé |
| A6 tests | `tests/commun.py` dans 16 tests ; code de sortie 1 en cas d'échec partout | tous les tests |
| D2, D3 cohérence | `THIRD_PARTY.txt` remis dans l'ordre ; `CLAUDE.md`, sommaire, 01, 02, 03, 05, 06 (dont 2026.10.15-1), 07 à jour | relecture |

Une conséquence à connaître : `index.html` passe une fois entièrement en fins de ligne Unix (environ
500 lignes du style étaient en fins de ligne Windows sur `main`). Le contenu est identique ; le diff de
cette page le montre comme modifié.

Poids : `index.html` 865 424 → 863 942 octets, `forme.html` 869 630 → 868 678 octets, `img2/` −240 Ko.
Console du navigateur : toujours vide sur les deux versions. Tests : `t4.py` à `t22.py`, tous verts.

**Reste à faire, à décider plus tard** : rien de « sûr ». Les points « à laisser » (A5, A7, C5, C6, D1,
D6, D7) le restent pour les raisons données plus haut.

**Non vérifiable ici** : l'affichage réel sur son téléphone, la caméra, la vibration, le menu Partager
d'Android, l'écran allumé. Les objectifs déjà abîmés par le bug des nombres (si Réglages a été
enregistré) ne sont pas réparés automatiquement : à vérifier dans Réglages.
