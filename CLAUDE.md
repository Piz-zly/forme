# Forme — note de synthèse pour l'assistant

Ce fichier est lu en premier par une IA qui ouvre ce dossier. Il dit ce qu'est le
projet, ce qu'on attend de lui, où se trouve chaque chose et comment travailler
dessus sans rien casser. Les détails sont dans `docs/`.

---

## 1. Nature du projet

**Forme** est une application personnelle de suivi sportif et alimentaire, écrite
en HTML, CSS et JavaScript, sans aucun framework. Elle remplace quatre
applications par une seule, organisée en quatre onglets :

| Onglet | Remplace | Rôle |
|---|---|---|
| **Poids** | Better Weight | Pesées, courbe, cercle de progression par paliers, pas et calories du jour |
| **Repas** | Yazio | Journal alimentaire, calories et macros, objectifs calculés selon le poids ; sous-onglets **Recettes** (classées selon le reste du jour) et **Déjà faites** |
| **Muscu** | Hevy | Séances, séries, charges, routines préparées à l'avance, minuteur de repos, progression |
| **Scan** | Yuka | Lecture de codes-barres, fiche produit, note de qualité nutritionnelle ; sous-onglet **Bibliothèque** (produits scannés rangés par section et sous-section) |

Elle existe en deux versions bâties depuis les mêmes sources :

- **`index.html`** — la version réelle, installée sur le téléphone de l'utilisateur
  (PWA publiée sur GitHub Pages). C'est **la version de référence**.
- **`forme.html`** — la même application pour l'intérieur de Claude (artefact privé).
  Elle n'a ni caméra en direct ni accès réseau, mais a accès au modèle (estimation
  d'un repas décrit en texte, lecture d'une étiquette en photo) et à une
  synchronisation privée sur le compte.

## 2. Objectif

Un outil quotidien, rapide et agréable, pour **une seule personne**, utilisateur
unique, sur un téléphone Android (Chrome), en France.
Il est **novice en programmation** : il ne lit pas le code, il décrit ce qu'il veut
et juge le résultat sur son téléphone.

**Informations personnelles** (modèle de téléphone, poids, objectif) : dans
`perso.md`, à lire s'il existe. Ce fichier est dans `.gitignore` : le dépôt est
public, **aucune donnée personnelle ne doit apparaître dans un fichier publié**
(ni dans le code, ni dans les tests, ni dans `docs/`).

## 3. Règles à respecter sans exception

1. **Les données restent chez lui.** Tout est dans le navigateur
   (`localStorage`, clé `forme.v1`). Aucun compte, aucun serveur, aucun envoi.
   Ne jamais mettre d'export de ses données dans ce dépôt, qui est public.
2. **Pas d'image ni de contenu dont on n'a pas les droits.** L'utilisateur a déjà
   proposé des visuels pris sur les réseaux sociaux : refuser, expliquer pourquoi,
   et proposer une source libre. Tout ce qui est embarqué doit être CC0, domaine
   public, MIT ou équivalent, et listé dans `THIRD_PARTY.txt`.
3. **Ne jamais utiliser un mot de passe ou un jeton donné dans la conversation.**
   On ne s'en sert pas, on ne crée pas de compte à sa place. C'est lui qui se
   connecte à GitHub, dans la fenêtre prévue.
4. **Pas de conseil médical.** Les objectifs de macros, le Nutri-Score et les
   dépenses affichées sont indicatifs. Le dire quand c'est utile, sans alourdir.
5. **Interface en français**, tutoiement, vocabulaire simple. Il dit « routine »,
   pas « modèle » ; « séance », pas « workout ».
6. **Pas de dépendance ajoutée** sans raison forte. Trois bibliothèques
   externes aujourd'hui, copiées en local dans `vendor/` : ZXing (codes-barres), Fuse.js
   (recherche tolérante aux fautes, depuis 2026.10.13-4) et Tesseract.js (lecture des étiquettes
   hors ligne, `vendor/ocr/`, ≈ 4,8 Mo chargés seulement au premier usage de la photo, version
   téléphone seulement, depuis 2026.10.14-4). Jamais de CDN, tout doit marcher hors ligne. Il a
   **écarté** l'idée d'une clé Claude dans l'application : ne pas la proposer. Données externes :
   la table Ciqual (Anses, Etalab 2.0), extraite dans `src/js2g.js` ; le texte de deux bases
   d'exercices (free-exercise-db, exercises-dataset), dans `src/js3c.js` — **jamais leurs images**
   (celles d'exercises-dataset sont © Gym visual).

## 4. Arborescence

```
.
├── CLAUDE.md                  ← ce fichier
├── README.md                  ← version courte, pour un humain
├── docs/                      ← documentation détaillée (voir sommaire ci-dessous)
│
├── index.html                 ← APPLICATION TÉLÉPHONE — généré, ne pas éditer
├── forme.html                 ← application pour Claude — généré, ne pas éditer
├── manifest.webmanifest       ← nom, icônes, écran d'accueil, partage entrant
├── sw.js                      ← service worker : hors ligne + mises à jour
├── .nojekyll                  ← exigé par GitHub Pages
├── THIRD_PARTY.txt            ← licences des éléments tiers
│
├── src/                       ← LES SOURCES — c'est ici qu'on modifie
│   ├── p1.html                ← titre, polices, variables CSS, feuille de style, structure
│   ├── p1.pwa.css             ← CSS en plus, uniquement pour la version téléphone
│   ├── js1.js                 ← utilitaires, état, stockage, synchro, graphique, navigation
│   ├── js1b.js                ← animations douces (outil maison) autour du dessin des écrans — à retirer de build.sh pour s'en passer
│   ├── js2.js                 ← onglet Poids (cercle, paliers) + onglet Repas
│   ├── js2b.js                ← carte « Journée » (pas, dépense, apport)
│   ├── js2c.js                ← les recettes embarquées — GÉNÉRÉ par tools/gen_recettes.py, ne pas éditer
│   ├── js2d.js                ← sous-onglets Recettes et Déjà faites du Repas
│   ├── js2e.js                ← les aliments de base — GÉNÉRÉ par tools/gen_aliments.py, ne pas éditer
│   ├── js2g.js                ← 3 203 aliments de la table Ciqual (Anses) — GÉNÉRÉ par tools/gen_ciqual.py, ne pas éditer
│   ├── js2f.js                ← onglet « Chercher » (recherche d'aliments, quantité) de la feuille Ajouter
│   ├── js2h.js                ← Repas : ajouts rapides, copier, repas types, corrections, Semaine, courses, frigo, Bilan
│   ├── js3c.js                ← consignes, équipement, muscles, 115 exercices en plus — GÉNÉRÉ par tools/gen_exercices.py (chargé AVANT js3.js)
│   ├── js3.js                 ← onglet Muscu : bibliothèque d'exercices, séance, types de série, records, suggestion de charge, progression, séries par muscle
│   ├── js3b.js                ← minuteur de repos, fiche d'exercice animée, routines
│   ├── js4b.js                ← bibliothèque des produits scannés : sections, classement auto, fiche (chargé AVANT js4.js)
│   ├── js4c.js                ← étiquette : parseLabel (texte lu -> valeurs) et feuille de vérification (AVANT js4.js)
│   ├── js4.js                 ← onglet Scan, codes-barres, note produit, réglages, démarrage
│   ├── js5.js                 ← propre au téléphone : caméra, Open Food Facts, partage, hors ligne, lecture d'étiquette (ocrRun), écran allumé (wakeSync)
│   └── build.sh               ← assemble le tout
│
├── tools/                     ← scripts d'atelier, lancés à la main, hors application
│   ├── gen_recettes.py        ← fabrique src/js2c.js : recettes, macros calculées
│   ├── gen_aliments.py        ← fabrique src/js2e.js : 321 aliments de base, rangés par section.sous-section, unités usuelles
│   ├── gen_ciqual.py          ← fabrique src/js2g.js depuis le fichier Excel Ciqual 2025 (téléchargé, hors dépôt)
│   ├── gen_exercices.py       ← fabrique src/js3c.js depuis exercises-dataset (texte, MIT) et free-exercise-db (domaine public)
│   ├── exercices_map.py       ← correspondance nom français → illustration
│   ├── recadre.py             ← recadre les illustrations au format de ill/ (atelier hors dépôt)
│   ├── paint.py               ← colore en rouge les muscles sur les illustrations
│   ├── gen_schemas_muscles.py ← génère les schémas anatomiques de img2/
│   ├── gen_decor.py           ← écrit le décor de fond dans src/p1.html (lance les deux suivants)
│   ├── gen_lune.py            ← décor Lune : ciel étoilé, lune au trait d'encre, nuages en volutes
│   └── gen_sakura.py          ← décor Sakura : branches de cerisier, mont Fuji
│
├── tests/                     ← tests de bout en bout (Playwright, Chromium)
│   ├── t4.py  séance, minuteur de repos, fiche d'exercice
│   ├── t5.py  partage entrant des pas, mise en page de la fiche
│   ├── t6.py  routines : séries une par une, démarrage, conversion de l'ancien format (chargement, import, synchro)
│   ├── t7.py  bascule muscles en rouge / image simple
│   ├── t8.py  recettes : classement, fiche, journal, recettes faites, recette perso
│   ├── t9.py  Chercher : recherche d'aliments, unités, ajout au journal, favoris
│   ├── t10.py bibliothèque du Scan : classement de 40 produits fictifs, doublons, rangement, suppression
│   ├── t11.py aliments de base rangés par section ; cohérence avec les règles de la bibliothèque
│   ├── t12.py table Ciqual dans « Chercher » : recherche, ordre, fiche, ml
│   ├── t13.py exercices enrichis : filtres muscle et équipement, fiche avec consignes, pas d'image cassée
│   ├── t14.py recherches tolérantes aux fautes : 15 fautes, non-régression, vitesse sur 8 500 aliments
│   ├── t15.py animations : apparition, effacement, déplacement, « réduire les animations », plafond
│   ├── t16.py Poids : plus de détails, IMC, historique par semaine et repliable, CSV, dépense estimée
│   ├── t17.py Repas : ajouts rapides, copier, repas types, souvent, corrections, cru/cuit, Semaine, courses, frigo, Bilan
│   ├── t18.py étiquettes : parseLabel, lecture réelle de fausses étiquettes (Tesseract.js, hors ligne)
│   └── t19.py Muscu : records, types de série, suggestion de charge, séries par muscle, écran allumé
│
├── ill/                       ← illustrations des mouvements (739 fichiers, 149 mouvements, CC0)
├── img2/                      ← schémas anatomiques par exercice (MIT)
├── icons/                     ← icônes de l'application
└── vendor/                    ← zxing.min.js (codes-barres), fuse.basic.min.js (fautes de frappe), ocr/ (Tesseract.js), Apache-2.0
```

## 5. Sommaire de la documentation

| Fichier | Contenu |
|---|---|
| `docs/01-projet.md` | L'utilisateur, l'historique des demandes, ce qui est fait, ce qui ne l'est pas |
| `docs/02-architecture.md` | Comment le code est organisé : vues, actions, feuilles, rendu |
| `docs/03-donnees.md` | Modèle de données, stockage, export, import, synchronisation |
| `docs/04-images.md` | D'où viennent les images, comment elles sont fabriquées, licences |
| `docs/05-build-publication.md` | Construire, tester, publier, mettre à jour le téléphone |
| `docs/06-journal.md` | Historique des versions |
| `docs/07-a-faire.md` | La suite : recettes, esthétique, idées en attente |
| `docs/08-pistes-open-source.md` | Projets libres repérés et ce qui en a été fait : Ciqual, free-exercise-db, Fuse.js et Tesseract.js intégrés, AutoAnimate écarté, canvas-confetti en attente |

## 6. Méthode de travail

### Le cycle normal

1. **Lire** `docs/02-architecture.md` avant de toucher au code. Le fichier à
   modifier se déduit du tableau de l'arborescence ci-dessus.
2. **Modifier uniquement `src/`**. `index.html` et `forme.html` sont générés :
   toute édition directe sera écrasée au prochain build.
3. **Monter la version** dans `src/js1.js` : `const APP_VER='AAAA.MM.JJ-n'`.
   Sans ça, le téléphone garde l'ancienne version en cache.
4. **Construire** : `./src/build.sh` (vérifie la syntaxe, régénère les deux
   fichiers, aligne `sw.js`).
5. **Tester** : voir `docs/05-build-publication.md`. Au minimum, servir le dossier
   et lancer les scripts de `tests/`.
6. **Publier** : branche, commits, envoi, puis fusion dans `main` après son accord
   (voir « Ce dossier et GitHub » ci-dessous). GitHub Pages met le site
   à jour en une à deux minutes.
7. **Dire à l'utilisateur comment récupérer la mise à jour** : fermer
   l'application, la rouvrir avec le réseau, ou Réglages → « Vérifier les mises à
   jour ». Et lui donner le numéro de version à vérifier en bas des Réglages.

### Ce qu'il ne faut pas faire

- Éditer `index.html`, `forme.html` ou le `VERSION` de `sw.js` à la main.
- Oublier de monter `APP_VER` : la mise à jour ne partira pas.
- Déplacer `index.html`, `manifest.webmanifest`, `sw.js`, `ill/`, `img2/`,
  `icons/` ou `vendor/` hors de la racine : GitHub Pages sert la racine, les
  chemins sont relatifs, et le service worker a déjà mis en cache ces chemins.
- Ajouter des fichiers lourds. L'application doit rester installable et rapide.

### Ce dossier et GitHub

Depuis le 13 octobre 2026, ce dossier **est un dépôt git** relié à
`github.com/Piz-zly/forme` (dépôt **public**, recréé ce jour-là sans données
personnelles). GitHub Pages sert la branche `main`, dossier racine.

- **Identité des commits** : `Piz-zly` et l'adresse masquée de GitHub
  (`339355630+Piz-zly@users.noreply.github.com`), en configuration locale et
  globale. Ne jamais utiliser son prénom ni sa vraie adresse.
- **Ne jamais publier** : `perso.md` (informations personnelles, dans
  `.gitignore`), les sauvegardes `forme-sauvegarde-*.json`, les fichiers Excel
  Ciqual, les images ou GIF de Gym visual. Avant chaque envoi, vérifier qu'aucune
  donnée personnelle n'est entrée dans un fichier publié (code, tests, docs).
- **Connexion à GitHub** : c'est lui qui se connecte, dans la fenêtre qui s'ouvre
  au premier envoi ; ses identifiants restent ensuite enregistrés par Git for
  Windows. Ne jamais demander ni utiliser de mot de passe ou de jeton.
- **Cycle d'une mise à jour** :
  1. `git switch main && git pull` pour partir de la dernière version publiée ;
  2. `git switch -c <nom-de-branche>` ;
  3. modifier `src/`, monter `APP_VER`, `./src/build.sh`, lancer tous les tests ;
  4. un commit clair en français par fonction ;
  5. `git push -u origin <nom-de-branche>`, lui donner le lien
     `https://github.com/Piz-zly/forme/compare/main...<nom-de-branche>` ;
  6. après son accord seulement : `git switch main`,
     `git merge --ff-only <nom-de-branche>`, `git push`.
  Ne jamais forcer un envoi sur `main` sans son accord explicite
  (`--force-with-lease`, jamais `--force`).
- La branche locale `sauvegarde-avant-reecriture` garde l'historique d'avant le
  changement de nom d'auteur (13 octobre) : elle ne doit **jamais** être envoyée.
- Une modification faite ici et jamais envoyée ne change rien sur le téléphone.

### Comment lui parler

Il est novice. Annoncer ce qui change en termes d'usage, pas de code : « la barre
de repos est maintenant en bas de l'écran », pas « refonte du composant timer ».
Dire franchement ce qui n'a pas pu être testé (vibration, caméra, menu de partage
d'Android ne sont testables que sur son téléphone). Un point par message quand il
le demande : il avance sujet par sujet.

## 7. État au 8 octobre 2026

- Version publiée : **2026.10.08-16**, poussée sur GitHub le 8 octobre 2026 au soir (ambiances
  Lune par défaut, Sakura et Néon dans Réglages → Ambiance ; bandeau de niveau en haut de chaque onglet).
  Les versions -13 à -16 ne sont **pas encore essayées sur son téléphone**.
- Site : `https://piz-zly.github.io/forme/` — dépôt : `github.com/Piz-zly/forme`
- Les quatre onglets fonctionnent. Il utilise l'application tous les jours sur son
  téléphone et a validé le scan de codes-barres, les routines et les illustrations.
- Sous-onglet **Recettes** (2026.10.08-8) : publié sur GitHub, pas encore essayé sur
  son téléphone. Onglet **Chercher** (-9, agrandi en -10), bibliothèque du Scan (-11) et rangement par
  section (-12) : testés (`tests/t9.py` à `t11.py`), **pas encore essayés sur son téléphone**. Voir `docs/07-a-faire.md` pour
  les choix à lui confirmer.
- **2026.10.13-1** (13 octobre 2026) : la recherche « Chercher » du Repas inclut 3 203 aliments de la
  table Ciqual (piste 1 de `docs/08-pistes-open-source.md`). Construite et testée (`tests/t4.py` à
  `t12.py`) ; publiée le 14 octobre 2026.
- **2026.10.13-2** (13 octobre 2026) : Muscu passe de 60 à 175 exercices, fiche avec consignes en
  français et équipement, filtres Muscle et Équipement (piste 2). Testée (`tests/t4.py` à `t13.py`),
  publiée le 14 octobre 2026.
- **2026.10.13-3** : choix de la prise (Large, Serrée…) sur la carte de 7 exercices, qui n'apparaissent
  plus qu'une fois dans la liste. Testée (`tests/t4.py` à `t13.py`), publiée le 14 octobre 2026.
- **2026.10.13-4** : recherches tolérantes aux fautes de frappe (Fuse.js) dans les aliments, les
  exercices, la bibliothèque du Scan et les favoris. Testée (`tests/t4.py` à `t14.py`), publiée le 14 octobre 2026.
- **2026.10.13-5** : animations douces (outil maison `src/js1b.js`, AutoAnimate non retenu) dans le
  journal du Repas, la routine, les pesées et la bibliothèque du Scan ; la séance Muscu n'est pas
  animée, à sa demande. Testée (`tests/t4.py` à `t15.py`), publiée le 14 octobre 2026.
- **2026.10.14-1** (14 octobre 2026) : les 175 exercices de Muscu ont une illustration animée (91
  mouvements ajoutés, dont 26 images proches ou approchantes validées par lui, voir
  `docs/04-images.md`). Testée (`tests/t4.py` à `t15.py`), **publiée le 14 octobre 2026** avec -2.
- **2026.10.14-2** : routines série par série (« Combien de séries ? » à l'ajout, un poids et des
  répétitions par série, ajouter / supprimer une série) ; anciennes routines converties sans perte
  (`docs/03-donnees.md`). Testée (`tests/t4.py` à `t15.py`), **publiée sur GitHub le 14 octobre 2026**
  (versions 2026.10.13-1 à 2026.10.14-2 en ligne), pas encore essayée sur son téléphone.
- **2026.10.14-3** : onglet Poids, « Plus de détails » (plus bas / haut, moyenne 30 j, variations, IMC,
  dépense estimée), historique coloré par semaine et repliable, taille dans Réglages, export / import
  CSV des pesées. Testée (`tests/t4.py` à `t16.py`), publiée le 14 octobre 2026.
- **2026.10.14-4** : Repas enrichi — calories rapides, copier un repas ou une journée, repas types,
  « Souvent à ce repas », source et correction des valeurs d'un aliment, cru / cuit, portions et calcul
  des recettes perso, sous-onglets **Semaine** (planning, liste de courses) et **Bilan** (série, calendrier),
  « Mon frigo » sans photo, lecture d'étiquette hors ligne (Tesseract.js, téléphone seulement, avec
  feuille de vérification). Testée (`tests/t4.py` à `t18.py`), publiée le 14 octobre 2026, pas encore essayée sur son téléphone.
  Non faits, et pourquoi : import de recette depuis un site (bloqué sans serveur), photo du frigo
  (il faudrait un modèle de vision ou un envoi, refusé).
- **2026.10.14-5** : Muscu — records battus en direct (bannière), types de série (échauffement, échec,
  drop set), suggestion de charge (double progression 10–12, palier 2,5 kg, réglables), carte « Séries
  par muscle (7 jours) » dans Progression, écran allumé pendant la séance (téléphone). Testée
  (`tests/t4.py` à `t19.py`), non publiée, branche `muscu-progression`. L'écran allumé n'est vérifiable
  que sur son téléphone.
