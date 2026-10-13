#!/bin/bash
# =============================================================================
# Forme - assemblage des sources
#
#   ./src/build.sh
#
# Produit deux fichiers a la racine du projet :
#   index.html  l'application installee sur le telephone (version GitHub Pages)
#   forme.html  la meme application pour l'interieur de Claude (sans js5.js)
# et aligne le numero de version du service worker (sw.js) sur APP_VER.
#
# Prerequis : bash, node (pour la verification de syntaxe), python3.
# =============================================================================
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$ROOT/src"
cd "$SRC"

# --- version declaree dans js1.js -------------------------------------------
V=$(grep -o "APP_VER='[^']*'" js1.js | cut -d"'" -f2)
[ -n "$V" ] || { echo "APP_VER introuvable dans js1.js"; exit 1; }

# --- verification de syntaxe ------------------------------------------------
TMP="$(mktemp -d)"
{ echo "(function(){'use strict';"; cat js1.js js2.js js2b.js js2c.js js2d.js js2e.js js2f.js js3.js js3b.js js4b.js js4.js js5.js; echo '})();'; } > "$TMP/all.js"
if command -v node >/dev/null; then node --check "$TMP/all.js"; else echo "node absent : verification de syntaxe ignoree"; fi

# --- version Claude (artefact) : pas de js5.js ------------------------------
{ cat p1.html
  echo '<script>'; echo "(function(){'use strict';"
  cat js1.js js2.js js2b.js js2c.js js2d.js js2e.js js2f.js js3.js js3b.js js4b.js js4.js
  echo '})();'; echo '</script>'
} > "$ROOT/forme.html"

# --- version telephone : en-tete PWA + CSS supplementaire + js5.js ----------
{
cat <<'HEAD'
<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#16112E">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Forme">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
HEAD
sed 's#<link rel="preconnect" href="https://fonts.googleapis.com">##' p1.html \
 | python3 -c "import sys;s=sys.stdin.read();css=open('p1.pwa.css').read();print(s.replace('</style>','</style>\n<style>'+css+'</style>',1),end='')"
echo '<script>'; echo "(function(){'use strict';"
cat js1.js js2.js js2b.js js2c.js js2d.js js2e.js js2f.js js3.js js3b.js js4b.js js4.js js5.js
echo '})();'; echo '</script>'; echo '</body></html>'
} > "$ROOT/index.html"

# --- le service worker doit changer de nom a chaque version -----------------
python3 - "$ROOT/sw.js" "$V" <<'PY'
import re,sys
p,v=sys.argv[1],sys.argv[2]
s=open(p,encoding='utf8').read()
open(p,'w',encoding='utf8').write(re.sub(r"const VERSION='[^']*'","const VERSION='forme-%s'"%v,s))
PY

rm -rf "$TMP"
echo "build ok - version $V"
