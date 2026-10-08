# 2. Architecture du code

Aucun framework, aucune étape de compilation. Les fichiers de `src/` sont
concaténés dans une seule page HTML, et tout le JavaScript tourne dans une seule
fonction anonyme en mode strict. Il n'y a donc **aucun module, aucun import** :
toutes les fonctions se voient entre elles, dans l'ordre de concaténation.

```
p1.html  →  <title>, polices, variables CSS, feuille de style, <header>, #view, #layer, .tabbar
js1.js   →  utilitaires, état, stockage, synchro, helpers d'interface, graphique, navigation
js2.js   →  onglet Poids, onglet Repas
js2b.js  →  carte Journée, reprise des pesées
js2c.js  →  RECIPES : les recettes embarquées (GÉNÉRÉ par tools/gen_recettes.py, ne pas éditer)
js2d.js  →  sous-onglets Recettes et Déjà faites du Repas : classement, fiche, ajout au journal, recettes perso
js3.js   →  onglet Muscu : données, accueil, séance, sélecteur, fin de séance, progression
js3b.js  →  minuteur de repos, fiche d'exercice, routines
js4.js   →  onglet Scan, codes-barres, note produit, réglages, démarrage
js5.js   →  uniquement version téléphone : caméra, Open Food Facts, partage, service worker
```

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
`:root`. Le thème sombre suit `prefers-color-scheme`.

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
