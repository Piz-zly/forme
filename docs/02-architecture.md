# 2. Architecture du code

Aucun framework, aucune étape de compilation. Les fichiers de `src/` sont
concaténés dans une seule page HTML, et tout le JavaScript tourne dans une seule
fonction anonyme en mode strict. Il n'y a donc **aucun module, aucun import** :
toutes les fonctions se voient entre elles, dans l'ordre de concaténation.

```
p1.html  →  <title>, polices, variables CSS, feuille de style, <header>, #view, #layer, .tabbar
js1.js   →  utilitaires, état, stockage, synchro, helpers d'interface, graphique, navigation
js2.js   →  onglet Poids, onglet Repas
js2b.js  →  carte Journée
js2c.js  →  RECIPES : les recettes embarquées (GÉNÉRÉ par tools/gen_recettes.py, ne pas éditer)
js2d.js  →  sous-onglets Recettes et Déjà faites du Repas : classement, fiche, ajout au journal, recettes perso
js2e.js  →  FOODS : les aliments de base (GÉNÉRÉ par tools/gen_aliments.py, ne pas éditer)
js2g.js  →  CIQUAL : 3 203 aliments de la table Ciqual (GÉNÉRÉ par tools/gen_ciqual.py, ne pas éditer)
js2f.js  →  onglet « Chercher » de la feuille Ajouter : recherche, choix de la quantité, ajout
js2h.js  →  Repas : ajouts rapides, copier, repas types, souvent, corrections (applyFixes), cru/cuit,
            parseIng et calcul des recettes, Semaine et liste de courses, frigo, Bilan
js3c.js  →  EXD : consignes, équipement, muscles, 115 exercices en plus (GÉNÉRÉ par tools/gen_exercices.py) — chargé AVANT js3.js
js3.js   →  onglet Muscu : données, accueil, séance, sélecteur, fin de séance, progression
js3b.js  →  minuteur de repos, fiche d'exercice, routines
js4b.js  →  bibliothèque des produits scannés (sections, classement, fiche) — chargé AVANT js4.js
js4c.js  →  étiquette : parseLabel (texte lu -> valeurs pour 100 g), boutons Photo/Galerie, feuille de vérification — AVANT js4.js
js4.js   →  onglet Scan, codes-barres, note produit, réglages, démarrage
js5.js   →  uniquement version téléphone : caméra, Open Food Facts, partage, service worker,
            lecture d'étiquette (ocrScript, ocrPrep, ocrRun : Tesseract.js depuis vendor/ocr)
```

> `reSheet(html)` (js1.js) remplace le contenu de la feuille ouverte sans rejouer l'animation
> d'ouverture ni remonter en haut ; `addSheet` l'utilise quand une feuille est déjà ouverte.
> Les sous-onglets du Repas (`FOOD_SUBS`, js2.js) sont cinq : Journal, Recettes, Déjà faites, Semaine
> (`weekView`), Bilan (`bilanView`) ; barre `.seg5`, lisible à 384 px (tests/t8.py).
> Lecture d'étiquette : `ocrBtns` n'affiche rien si `ocrRun` n'existe pas (forme.html, sans js5.js).
> `ocrRun` lit la photo en niveaux de gris, contraste étiré (2–98 %), grand côté 1500 px (petite photo
> agrandie, ×2 au plus), mode de page 4 ; si moins de 6 valeurs sont trouvées, une seconde lecture à
> 1000 px. `parseLabel` garde, pour chaque nombre, ses lectures possibles (« g » lu comme 9 ou 0,
> virgule perdue, zéro de tête) et choisit la combinaison la plus cohérente avec les calories.

> L'ordre compte. `js3b.js` utilise `EXI` et `gymOpen` définis dans `js3.js`.
> Les **déclarations de fonction** sont remontées (hoisting) et peuvent donc être
> appelées depuis un fichier précédent ; les `const` et `let`, non. C'est pour ça
> que `syncRestBar()` est appelée depuis `js1.js` derrière un
> `typeof … === 'function'`.

## Le rendu

Chaque onglet est une fonction qui **retourne une chaîne de HTML** :

```js
VIEWS.weight = () => `<div class="card">…</div>`;
VIEWS.weight_after = () => { /* code exécuté après insertion, ex. tracer un graphique */ };
```

`render()` écrit `VIEWS[tab]()` dans `#view`, puis appelle `VIEWS[tab+'_after']`
si elle existe. Il n'y a ni rendu différentiel ni état de composant : on
reconstruit la vue entière, c'est suffisant à cette échelle.

Les quatre vues : `weight`, `food`, `gym`, `scan`.

Le **Repas** a trois sous-onglets, pilotés par la variable `foodSub`
(`'journal'`, `'recipes'`, `'done'`) : `VIEWS.food` affiche le journal, ou passe la
main à `recipesView()` (`js2d.js`). Le choix n'est pas enregistré : on revient au
journal à chaque ouverture de l'application.

**Animations** (`js1b.js`, 2026.10.13-5) — outil maison chargé juste après `js1.js`. Il
remplace `renderBehind` par une enveloppe : avant le dessin, `animSnap()` note la position des
lignes marquées ; après, `animPlay()` les fait glisser (si elles ont bougé) ou apparaître (si elles
sont nouvelles), et réinsère les lignes disparues sous forme de copie inerte qui se replie en 150 ms.
Marquage : un conteneur `data-ag="portée:nom"` dont les enfants directs portent `data-ak="clé"` (clé
unique dans l'écran). Rien ne s'anime si la portée n'existait pas avant (autre onglet, autre jour),
au-delà de 60 lignes (`ANIM_MAX`), ou avec `prefers-reduced-motion: reduce`. Endroits marqués :
journal (`m:jour:repas`, clé = id de l'entrée), pesées (`w:hist`, clé = `w` + date), routine
(`r:id:x`, clé = nom#n), bibliothèque du Scan (`lib:section`, clé = id du produit, pas pendant une
recherche). Pour animer une autre liste : poser ces deux attributs. Pour retirer l'outil : enlever
`js1b.js` de `build.sh`, les attributs restent sans effet.

## Les actions

Trois registres, un seul écouteur global chacun, par délégation d'événement
(`js1.js`) :

| Attribut HTML | Registre | Déclencheur |
|---|---|---|
| `data-act="nom"` | `A.nom = (bouton, event) => {}` | clic |
| `data-in="nom"` | `I.nom = (champ) => {}` | saisie (`input`) |
| `data-ch="nom"` | `I.nom = (champ) => {}` | changement (`change`), cases, dates, fichiers |

Les paramètres passent par des `data-*` lus dans le gestionnaire :

```html
<button data-act="g-rsets" data-i="2" data-d="-1">−</button>
```
```js
A['g-rsets'] = b => { const i = +b.dataset.i, d = +b.dataset.d; … };
```

Préfixes par domaine : `w-` poids, `f-` repas, `g-` muscu, `s-` scan,
`bc-` code-barres, `act-` activité du jour, `mov-` animation, `set-` réglages.

## Les feuilles du bas

Toute saisie passe par une feuille coulissante, jamais par une fenêtre système :

```js
openSheet(html);                     // insère dans #layer
closeSheet();                        // vide #layer
confirmSheet(titre, texte, libellé, onOk);  // confirmation destructive
```

Un clic sur le fond (`.scrim`) ferme la feuille. `A.close` est déjà câblé.

## Le style

Tout est dans `p1.html`, dans un seul `<style>`, avec des variables CSS sur
`:root`. Trois ambiances, choisies dans Réglages (`S.settings.theme`) et appliquées par
`applyTheme()` au début de `render()` (`data-theme` sur `<html>`) : **Lune** (par défaut, variables de
`:root`), **Sakura** (`[data-theme="light"]`) et **Néon** (`[data-theme="dark"]`, réglage `nuit`).
Elles ne suivent pas `prefers-color-scheme`. Les jetons `--panel`, `--tile`, `--press`, `--well`,
`--glow`, `--depth-mix`, `--lift-mix`, `--timer` changent avec l'ambiance ; les règles propres à Sakura
et Néon sont en fin de feuille, préfixées par leur `[data-theme]`. Le décor de fond (`.deco`, avec `.sk`
pour Sakura et `.ln` pour Lune) est en tête de `p1.html` entre `<!-- deco:debut -->` et
`<!-- deco:fin -->`, écrit par `python3 tools/gen_decor.py` ; `#app` passe au-dessus (`z-index:1`).
Le bandeau de niveau est `#hud`, rempli par `hudHtml()` (`js2.js`).

Règle forte : **une seule couleur d'accent à la fois**, donnée par l'onglet actif.
`render()` écrit `#app[data-tab]`, et le CSS redéfinit `--accent` en conséquence :

```css
#app[data-tab="weight"] { --accent: var(--c-weight); }  /* bleu   */
#app[data-tab="food"]   { --accent: var(--c-food);   }  /* orange */
#app[data-tab="gym"]    { --accent: var(--c-gym);    }  /* rouge  */
#app[data-tab="scan"]   { --accent: var(--c-scan);   }  /* vert   */
```

Un composant n'utilise jamais `--c-gym` directement : il utilise `--accent`.

Classes réutilisables : `.card`, `.btn` (+ `.ghost`, `.soft`, `.danger`, `.block`),
`.chip`, `.pill` (+ `.good`, `.warn`, `.bad`, `.neutral`), `.li`, `.list`,
`.field`, `.inp`, `.grid2`, `.sec`, `.stats`/`.stat`, `.row`, `.sb`, `.small`,
`.muted`, `.num` (chiffres à chasse fixe), `.empty`.

Tailles tactiles : rien d'interactif en dessous de 44 px de haut.

## Points particuliers

**Cercle de progression** (`js2.js`, `ringCard`) — SVG tracé à la main dans un
`viewBox` 280×280. Un arc par palier, séparé par un petit intervalle, un point à
chaque limite, une étiquette à l'extérieur, un repère à la position courante. Les
arcs sont proportionnels aux kilos, pas au nombre de paliers.

**Graphique** (`js1.js`, `chart`) — SVG fait maison : grille, échelle « ronde »
via `niceStep`, points pour les pesées, courbe pour la moyenne 7 jours, ligne
d'objectif, et une ligne de lecture qui suit le doigt (`onPick`).

**Bibliothèque du Scan** (`js4b.js`) — sous-onglet « Bibliothèque » de l'onglet Scan
(`scanSub`, `scanSeg`). `SLIB` décrit les 11 sections et leurs sous-sections ;
chaque catégorie est écrite `section.sous-section` (`vpo.poisson`). `libGuess(p)`
rend `p.cat` si elle existe, sinon applique `SLIB_RULES` dans l'ordre : la première
règle dont le mot-clé du nom (sans accents) **ou** la catégorie Open Food Facts
(`p.tags`) correspond gagne, donc les cas précis passent avant les cas généraux
(« barre protéinée » avant « barre », « pain au chocolat » avant « chocolat »…).
Pour améliorer le classement : ajouter un mot à la règle concernée, ou une règle au
bon endroit, puis lancer `tests/t10.py` (40 produits fictifs). Rien n'est enregistré
tant qu'il n'a pas rangé lui-même un produit : un meilleur classement profite donc
à tous les produits déjà scannés. Une fiche s'ouvre en feuille (`lib-open`) avec le
choix du rangement (`<select>` groupé par section), et la suppression.
`js4b.js` est chargé **avant** `js4.js` car celui-ci lance le premier rendu en fin de
fichier : les `const`/`let` de la bibliothèque doivent déjà exister.
**Doublons** : `libBuild` regroupe les fiches qui ont le même rangement, les mêmes
calories/protéines/glucides/lipides (`libSig`) et des noms proches une fois la marque et
les mots vides retirés (au moins 60 % de mots communs, `libSame`). Les produits sans
aucune valeur (eau à 0 kcal) ne sont jamais fusionnés. La ligne affichée est la plus
récemment scannée, avec « ×2 » et les marques ; la fiche liste toutes les fiches du
groupe ; ranger ou retirer le produit s'applique à tout le groupe. L'état n'est pas
modifié : c'est un regroupement à l'affichage, donc réversible.
Les feuilles du Scan sont enveloppées dans `.sc` (accent vert, le calque est hors de
`#app`). À la lecture d'une étiquette par Claude, `libPrompt()` lui demande aussi
la catégorie (liste fermée), vérifiée par `libOk`.

**Aliments de base rangés** — chaque aliment de `js2e.js` a une catégorie
`section.sous-section` (celles de `SLIB`, `js4b.js`), écrite dans `tools/gen_aliments.py`
(le script refuse un rangement inconnu). Les puces de « Chercher » sont « Courants »
puis les sections (nom court `s` de `SLIB`, ex. « VPO ») ; une section affiche ses
aliments par sous-section ; une recherche reste une liste à plat. `tests/t11.py` vérifie
que tout aliment apparaît dans sa section et que les règles de classement de la
bibliothèque donnent le même rangement que la table (≥ 95 %) : si les deux divergent,
corriger la règle de `SLIB_RULES` ou la catégorie de l'aliment.

**Table Ciqual** (`js2g.js`, 2026.10.13-1) — `CIQUAL` est une liste compacte
`[code, rangement, nom, kcal, P, G, L, (1 = ml)]` ; `js2f.js` en fait des objets comme
ceux de `FOODS` (`id` = `cq` + code, `cq:1`) dans `CQFOODS`, et cherche dans
`ALLFOODS` = `FOODS` + `CQFOODS`. Un aliment Ciqual prend 1,5 point de pénalité : les
aliments familiers passent devant à pertinence égale. Les puces de section ne listent
que `FOODS` (sinon des centaines de lignes), suivies de « + N aliments de la table
Ciqual » (`cqMore`). Pas d'unité usuelle : grammes, ou ml pour les boissons. La fiche
affiche « Source : Anses, Table Ciqual 2025 » (exigé par la licence). Régénérer :
`python3 tools/gen_ciqual.py <fichier .xlsx>` (le fichier vient de
recherche.data.gouv.fr et ne va pas dans le dépôt). Testé par `tests/t12.py`.

**Fautes de frappe** (`js2f.js`, 2026.10.13-4) — module commun aux quatre recherches (aliments,
exercices `exPicker`, bibliothèque `libGroups`, favoris `mineList`). `fzWords` découpe et normalise
(`normTxt`, pluriel retiré) ; `fzCache(objet, signature, clés)` garde un vocabulaire par liste (mots
distincts + index `Fuse`), refait seulement si la signature change ; `fzAlts` laisse tel quel un mot
présent dans la liste et propose sinon jusqu'à 3 voisins (Fuse, puis `fzDist` ≤ 1 ou 2, première
lettre juste à 2 fautes) ; `fzScore` note une clé (0 = tout exact). Fuse.js est global (`vendor/`,
chargé avant le script dans `index.html`, intégré dans `forme.html`) ; sans lui, recherche exacte.

**Chercher** (`js2f.js`, données `js2e.js` et `js2g.js`) — premier onglet de `addSheet()` (js2.js),
ouvert par défaut (`A['f-add']` remet la recherche à zéro). `foodSearch` ignore
accents, majuscules, `œ`/`oe` et le pluriel (« oeufs » trouve « Œuf entier ») ; tous
les mots tapés doivent être présents ; le début du nom passe avant le début d'un
mot, lui-même avant le milieu ; les aliments « courants » (`top`) gagnent un
demi-point. Sans texte, on affiche les courants ou la catégorie choisie. Taper
met à jour la liste en place (`foodRefresh`) pour ne pas fermer le clavier.
Un clic sur un aliment (`b-pick`) passe à l'écran de quantité : grammes/ml, ou une
unité usuelle (`u` : œuf, tranche, càs, portion…) avec 1 par défaut ; changer
d'unité garde la même masse. `bDraw` recalcule en place. L'entrée ajoutée au
journal est écrite en toutes lettres (« 2 œufs », « 150 g de riz basmati cuit »,
« 1 càs d'huile d'olive ») ; la case « Garder dans mes favoris » l'ajoute à
`S.foods`. Les valeurs sont des moyennes **rédigées pour l'application** dans
`tools/gen_aliments.py` (rien n'est recopié d'une base) : ajouter un aliment =
ajouter un appel `F(...)` puis relancer le script et le build. Dans le script, une
unité est `(libellé 'sing|plur', grammes, 's'|'d')` : `s` si le libellé est
l'aliment lui-même (« 2 œufs »), `d` sinon (« 2 tranches de pain »). Attention :
les regex de `js2f.js` utilisent des codes `\u` plutôt que des caractères
accentués collés, car `forme.html` n'a pas de `<meta charset>`.

**Recettes** (`js2d.js`) — le reste de la journée affichée (`rcRem`) est comparé à
chaque recette. Une recette « tient » si elle ne dépasse ni les calories restantes
(+30), ni les lipides (+4 g), ni les glucides (+8 g) ; les protéines ne sont jamais
bloquantes. Les recettes qui tiennent passent en premier, triées par `rcScore` :
écart à la part du reste qu'un repas de ce type devrait couvrir (`rcTarget`, qui
répartit le reste entre les repas pas encore saisis), les protéines en dessous de
la cible comptant plus que celles au-dessus. Sans filtre de repas, la cible est celle
du prochain repas (`rcNextSlot` : l'heure, puis le premier repas non saisi) et une
recette prévue pour un autre repas prend une petite pénalité. Si les calories sont
déjà dépassées, tout est « en trop » et les plus légères passent en premier.
La fiche d'une recette ne se reconstruit pas à chaque appui (portions, repas
choisi) : `rcDraw()` met à jour les morceaux concernés, sinon la fiche remonterait
en haut. Le calque des feuilles est hors de `#app`, donc la classe `.rc` y remet
l'accent orange du Repas.

**Minuteur de repos** (`js3b.js`) — l'élément `#rbar` est ajouté au `<body>`, pas
dans `#view`, pour survivre aux rendus. `syncRestBar()` est appelée chaque seconde
par `tick()` et après chaque `render()` ; elle ne reconstruit le HTML que lorsque
l'état change (au repos / en repos), sinon elle ne met à jour que le compteur et
la jauge.

**Exercices enrichis** (`js3c.js`, 2026.10.13-2) — `EXD[nom] = {eq, m, s, st, g?}`. En tête de `js3.js`,
chaque entrée est fusionnée dans `EXI` (qui garde `i`, l'identifiant du schéma `img2/`, pour les 60
d'origine) ; un exercice avec `g` est ajouté au groupe `g` de `LIB` (créé s'il manque : Avant-bras).
Un exercice sans `i` n'a pas de schéma (les 115 de 2026.10.13-2), sans entrée `ILL` pas d'illustration
(depuis 2026.10.14-1, seulement les exercices créés par l'utilisateur) : la fiche et la vignette
(initiale) s'en passent. Le sélecteur (`exPicker`) a deux `<select data-ch>` (`exMus` : muscle principal, `exEq` :
équipement) ; filtres actifs sans texte → liste par groupe, filtrée ; la recherche passe par `normTxt`
(js2f.js). Régénérer : `python3 tools/gen_exercices.py <A.json> <B.json> [--relire]` ; `--relire`
affiche toutes les consignes pour relecture. Testé par `tests/t13.py`.
Familles de prises (2026.10.13-3) : `EXV[base] = [libellé, [[bouton, nom], …]]`, `GRIP[nom] = base`.
`gripHidden(n)` retire les prises autres que la base de la liste ; `gripRow(nom, act, i)` dessine les
boutons sur la carte (séance : `g-grip`, routine : `g-rgrip`), qui remplacent `e.name`.

**Routines, une ligne par série** (`js3b.js`, 2026.10.14-2) — `e.sets = [{kg, reps}, …]` (voir
`docs/03-donnees.md`). Choisir un exercice dans une routine (`pushEx`, `js3.js`) ouvre d'abord
`rAskSets(nom)` : feuille « Combien de séries ? », pastilles 1 à 8 (`g-rcnt`, 3 par défaut),
`g-rcok` ajoute l'exercice, Annuler ferme sans rien ajouter. Chaque série est une ligne de la grille
`.rsets` : deux champs `data-in="rset"` (`data-i` exercice, `data-s` série, `data-f` kg ou reps),
enregistrés à chaque touche **sans redessiner** (seul le résumé `#rsum<i>` est mis à jour), et une
croix `g-rdelset` (désactivée quand il ne reste qu'une série). `g-raddset` ajoute une série qui
recopie la dernière (20 au plus). `rSum(e)` résume l'exercice : « 3 × 8 · 60 kg » si toutes les séries
sont identiques, sinon « 3 séries · 60–75 kg · 6–10 reps ». `g-rdup` copie en profondeur.
`startSession(nom, exercices)` prend ce format (« Refaire » et « Enregistrer comme routine »
construisent des séries vides, comme avant). Les lignes de séries ne sont pas animées (elles
bougeraient deux fois quand la carte de l'exercice glisse) ; les cartes d'exercice le restent.

**Progression de la Muscu** (`js3.js`, 2026.10.14-5) — `STYPES` (types de série), `isWork` / `workSets`
(tout sauf l'échauffement), `setLab` (lettre ou numéro parmi les séries normales), `withT` (recopie le type).
`prCheck(nom, série, autres)` compare une série validée à `S.sessions` + séries déjà validées de la séance ;
`g-check` pose `s.pr` et `prBan` (bannière `#prban`, dans la grille `.sets`, retirée du DOM après
`PR_MS` sans redessiner ; une nouvelle série validée la remplace). `sugCalc(séries)` rend `{up, kg, st, lo,
hi}` ou `null` ; ligne courte `.sug` (une ligne à 384 px, `sugTxt` donne la phrase entière au lecteur
d'écran) ; `g-sug` pré-remplit seulement. `g-stype` / `g-stype-ok` : feuille des types (`c` = `a` séance,
`r` routine). `musWeek()` / `musCard()` : séries par muscle sur 7 jours, repli `S.ui.gMusClosed` (`g-mus`).
Écran allumé : `wakeSync()` dans `js5.js` (téléphone seulement), appelé chaque seconde par `tick()` et à
`visibilitychange` ; ses variables sont des `var` car `tick()` peut tourner avant la fin du script.
Rien n'est animé dans la séance (choix de l'utilisateur).

**Fiche d'exercice** (`js3b.js`) — deux `<img>` superposées en fondu, alternées
toutes les 950 ms par `playMov()`. La boucle s'arrête d'elle-même quand l'élément
n'est plus dans le document. `ILL` associe le nom français à l'identifiant de
l'illustration, `EXI` au schéma anatomique et aux muscles.

**Codes-barres** (`js4.js`) — trois tentatives en cascade : `BarcodeDetector`
natif, puis ZXing sur l'image en niveaux de gris à trois résolutions avec essai
à 90°, puis en dernier recours lecture des chiffres par Claude. Toujours validé
par la clé de contrôle EAN (`EAN_OK`).

**Note produit** (`js4.js`, `evalProduct`) — Nutri-Score simplifié (barème
général) converti en note sur 100, moins 15, 7 ou 2 points par additif selon le
risque, plafonné à 49 si un additif à risque élevé est présent. C'est une
estimation, pas la note officielle d'une application du marché.

## Un piège rencontré

`js3.js` définit `function history(name)`. Dans la portée de l'IIFE, ce nom
**masque `window.history`**. Tout appel à l'historique du navigateur doit donc
s'écrire `window.history.replaceState(…)`. Le cas s'est déjà produit avec le
partage entrant dans `js5.js`.
