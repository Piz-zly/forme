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

Un outil quotidien, rapide et agréable, pour **une seule personne** :
un homme, utilisateur unique, sur **Samsung S25+** (Android, Chrome), en France.
Il est **novice en programmation** : il ne lit pas le code, il décrit ce qu'il veut
et juge le résultat sur son téléphone.

Objectif chiffré en cours : passer de 104,3 kg (21/09/2026) à **80 kg**, par
paliers de 2,5 kg.

## 3. Règles à respecter sans exception

1. **Les données restent chez lui.** Tout est dans le navigateur
   (`localStorage`, clé `forme.v1`). Aucun compte, aucun serveur, aucun envoi.
   Ne jamais mettre d'export de ses données dans ce dépôt, qui est public.
2. **Pas d'image ni de contenu dont on n'a pas les droits.** L'utilisateur a déjà
   proposé des visuels pris sur les réseaux sociaux : refuser, expliquer pourquoi,
   et proposer une source libre. Tout ce qui est embarqué doit être CC0, domaine
   public, MIT ou équivalent, et listé dans `THIRD_PARTY.txt`.
3. **Ne jamais utiliser un mot de passe donné dans la conversation.** Il en a
   communiqué un par erreur ; il lui a été conseillé de le changer. On ne s'en
   sert pas, on ne crée pas de compte à sa place.
4. **Pas de conseil médical.** Les objectifs de macros, le Nutri-Score et les
   dépenses affichées sont indicatifs. Le dire quand c'est utile, sans alourdir.
5. **Interface en français**, tutoiement, vocabulaire simple. Il dit « routine »,
   pas « modèle » ; « séance », pas « workout ».
6. **Pas de dépendance ajoutée** sans raison forte. Une seule bibliothèque
   externe aujourd'hui : ZXing, copiée en local dans `vendor/`.

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
│   ├── js2.js                 ← onglet Poids (cercle, paliers) + onglet Repas
│   ├── js2b.js                ← carte « Journée » (pas, dépense, apport) + reprise des pesées
│   ├── js2c.js                ← les recettes embarquées — GÉNÉRÉ par tools/gen_recettes.py, ne pas éditer
│   ├── js2d.js                ← sous-onglets Recettes et Déjà faites du Repas
│   ├── js2e.js                ← les aliments de base — GÉNÉRÉ par tools/gen_aliments.py, ne pas éditer
│   ├── js2f.js                ← onglet « Chercher » (recherche d'aliments, quantité) de la feuille Ajouter
│   ├── js3.js                 ← onglet Muscu : bibliothèque d'exercices, séance, progression
│   ├── js3b.js                ← minuteur de repos, fiche d'exercice animée, routines
│   ├── js4b.js                ← bibliothèque des produits scannés : sections, classement auto, fiche (chargé AVANT js4.js)
│   ├── js4.js                 ← onglet Scan, codes-barres, note produit, réglages, démarrage
│   ├── js5.js                 ← propre au téléphone : caméra, Open Food Facts, partage, hors ligne
│   └── build.sh               ← assemble le tout
│
├── tools/                     ← scripts d'atelier, lancés à la main, hors application
│   ├── gen_recettes.py        ← fabrique src/js2c.js : recettes, macros calculées
│   ├── gen_aliments.py        ← fabrique src/js2e.js : 321 aliments de base, rangés par section.sous-section, unités usuelles
│   ├── exercices_map.py       ← correspondance nom français → illustration
│   ├── paint.py               ← colore en rouge les muscles sur les illustrations
│   └── gen_schemas_muscles.py ← génère les schémas anatomiques de img2/
│
├── tests/                     ← tests de bout en bout (Playwright, Chromium)
│   ├── t4.py  séance, minuteur de repos, fiche d'exercice
│   ├── t5.py  partage entrant des pas, mise en page de la fiche
│   ├── t6.py  routines : création, édition, démarrage
│   ├── t7.py  bascule muscles en rouge / image simple
│   ├── t8.py  recettes : classement, fiche, journal, recettes faites, recette perso
│   ├── t9.py  Chercher : recherche d'aliments, unités, ajout au journal, favoris
│   ├── t10.py bibliothèque du Scan : classement de 40 produits fictifs, doublons, rangement, suppression
│   └── t11.py aliments de base rangés par section ; cohérence avec les règles de la bibliothèque
│
├── ill/                       ← illustrations des mouvements (288 fichiers, CC0)
├── img2/                      ← schémas anatomiques par exercice (MIT)
├── icons/                     ← icônes de l'application
└── vendor/zxing.min.js        ← lecteur de codes-barres (Apache-2.0)
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
6. **Publier** : `git add -A && git commit && git push`. GitHub Pages met le site
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

Ce dossier est une **copie du dépôt** `github.com/Piz-zly/forme`, posée sur
l'ordinateur de l'utilisateur. Il n'y a pas de `.git` : c'est volontaire, il n'a
pas à manipuler git.

- **Rafraîchir le dossier** depuis la dernière version publiée :

  ```bash
  curl -sSL -o /tmp/forme.tar.gz \
    https://codeload.github.com/Piz-zly/forme/tar.gz/refs/heads/main
  rm -rf /tmp/forme-new && mkdir -p /tmp/forme-new
  tar xzf /tmp/forme.tar.gz --strip-components=1 -C /tmp/forme-new
  cp -r /tmp/forme-new/. "<ce dossier>"
  ```

  On passe par un dossier temporaire et `cp` : extraire directement par-dessus
  échoue. Quand une IA accède à ce dossier depuis une conversation, la
  **suppression de fichiers y est interdite par défaut**, et `tar` doit effacer
  un fichier avant de le réécrire. `cp` se contente de réécrire par-dessus, ce
  qui passe. Un fichier retiré du dépôt restera donc dans le dossier : le
  supprimer à la main si besoin.

- **Travailler depuis ce dossier** : modifier `src/`, lancer `./src/build.sh`,
  tester. Pour publier, les fichiers doivent repartir vers le dépôt ; sans git
  ici, le plus simple est de refaire la modification côté dépôt, ou d'y recopier
  les fichiers changés.
- Le dossier n'est **pas** ce que sert GitHub Pages : le site vient du dépôt. Une
  modification faite ici et jamais poussée ne changera rien sur le téléphone.

### Comment lui parler

Il est novice. Annoncer ce qui change en termes d'usage, pas de code : « la barre
de repos est maintenant en bas de l'écran », pas « refonte du composant timer ».
Dire franchement ce qui n'a pas pu être testé (vibration, caméra, menu de partage
d'Android ne sont testables que sur son téléphone). Un point par message quand il
le demande : il avance sujet par sujet.

## 7. État au 8 octobre 2026

- Version construite dans ce dossier : **2026.10.08-12** (doublons, aliments de base rangés par section). Publiée sur GitHub le 8 octobre 2026 (tout ce qui précède l'est aussi : recettes, Chercher, bibliothèque).
- Site : `https://piz-zly.github.io/forme/` — dépôt : `github.com/Piz-zly/forme`
- Les quatre onglets fonctionnent. Il utilise l'application tous les jours sur son
  téléphone et a validé le scan de codes-barres, les routines et les illustrations.
- Sous-onglet **Recettes** (2026.10.08-8) : publié sur GitHub, pas encore essayé sur
  son téléphone. Onglet **Chercher** (-9, agrandi en -10), bibliothèque du Scan (-11) et rangement par
  section (-12) : testés (`tests/t9.py` à `t11.py`), **pas encore essayés sur son téléphone**. Voir `docs/07-a-faire.md` pour
  les choix à lui confirmer.
