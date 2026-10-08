# 5. Construire, tester, publier

## Construire

```bash
./src/build.sh
```

Le script :

1. lit `APP_VER` dans `src/js1.js` ;
2. vérifie la syntaxe de tout le JavaScript avec `node --check` ;
3. écrit `forme.html` — version Claude, sans `js5.js` ;
4. écrit `index.html` — version téléphone : en-tête PWA, `p1.pwa.css` ajouté,
   `js5.js` inclus ;
5. recopie la version dans `const VERSION` de `sw.js`.

**Avant de construire, monter la version** dans `src/js1.js` :

```js
const APP_VER='2026.10.08-7';   // AAAA.MM.JJ-numéro dans la journée
```

C'est ce qui change le nom du cache du service worker. Sans ça, les téléphones
qui ont déjà l'application gardent l'ancienne version.

Prérequis : `bash`, `python3`, et `node` pour la vérification de syntaxe (le
script continue sans, mais on perd le filet).

## Tester

```bash
python3 -m http.server 8765          # depuis la racine du projet
python3 tests/t4.py                  # séance, minuteur de repos, fiche d'exercice
python3 tests/t6.py                  # routines
python3 tests/t7.py                  # bascule muscles en rouge
python3 tests/t5.py                  # partage entrant des pas
```

Les tests utilisent Playwright avec Chromium en 412 × 900, la taille d'un
téléphone. Ils cliquent dans l'application comme un utilisateur et affichent le
texte obtenu, en plus de captures dans `/tmp`. Ils signalent toute erreur
JavaScript : **`ERRS []` est la ligne à vérifier en priorité**.

```bash
pip install playwright && playwright install chromium
```

Ce qui ne peut pas être testé ici, et qu'il faut annoncer comme tel :

- la vibration ;
- la caméra en direct ;
- l'inscription au menu Partager d'Android ;
- l'installation sur l'écran d'accueil ;
- le rendu réel sur l'écran du S25+.

## Publier

```bash
git add -A
git commit -m "Description courte de ce qui change"
git push
```

GitHub Pages republie le site en une à deux minutes.

- Site : `https://piz-zly.github.io/forme/`
- Dépôt : `github.com/Piz-zly/forme`, branche `main`, Pages servie depuis la
  racine. Le fichier `.nojekyll` est indispensable, ne pas le supprimer.

### La version dans Claude

`forme.html` est publié comme artefact privé, avec les dossiers `ill/`, `img2/` et
`THIRD_PARTY.txt` en fichiers joints. Deux limites rencontrées : 255 fichiers par
publication, 512 fichiers par version. Les anciennes photos ont dû être retirées
pour faire de la place.

## Mettre à jour le téléphone

À dire à l'utilisateur, à chaque publication :

1. Fermer complètement Forme, la retirer des applications récentes.
2. La rouvrir avec le réseau activé : elle se met à jour seule.
3. Si rien ne change : Réglages → **Vérifier les mises à jour**. Le bouton vide
   les caches et recharge.
4. Contrôler le numéro de version en bas des Réglages.

Les données ne sont jamais touchées par une mise à jour.

## Comment fonctionne le service worker

`sw.js` met en cache le squelette de l'application à l'installation, puis :

- **navigation** : le réseau d'abord, le cache si le réseau manque. C'est ce qui
  fait qu'une nouvelle version arrive dès la première ouverture connectée.
- **autres fichiers** : le cache d'abord, le réseau sinon, et on met en cache.
- **Open Food Facts** n'est jamais mis en cache : toujours en direct.

`skipWaiting()` et `clients.claim()` font que la nouvelle version prend la main
immédiatement. Changer `VERSION` supprime tous les anciens caches : c'est le rôle
d'`APP_VER`.

## Installer sur un téléphone

1. Ouvrir `https://piz-zly.github.io/forme/` dans Chrome.
2. Menu à trois points → **Ajouter à l'écran d'accueil**.
3. L'application s'ouvre en plein écran et fonctionne hors ligne, sauf la
   recherche de produits.

Si une fonction déclarée dans `manifest.webmanifest` n'apparaît pas — le menu
Partager, par exemple — Android ne l'a pas enregistrée : exporter les données par
précaution, retirer l'icône, puis réinstaller depuis Chrome.
