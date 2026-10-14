# 3. Les données

## Où elles vivent

Tout tient dans un seul objet JavaScript, `S`, enregistré dans le navigateur sous
la clé **`forme.v1`** de `localStorage`. Rien ne part sur un serveur.

Conséquences à ne jamais perdre de vue :

- Les données sont **liées au navigateur et à l'adresse du site**. La version
  installée depuis `piz-zly.github.io` et la version dans Claude ont chacune leur
  stock, séparés.
- **Effacer les données de navigation de Chrome efface tout.** D'où l'export.
- La version installée appelle `navigator.storage.persist()` au démarrage pour
  demander à Android de ne pas effacer ce stockage en cas de manque de place.

## Forme de l'objet

```js
{
  settings: {
    kcal: 2200,        // calories visées
    p: 150, c: 250, f: 70,   // macros fixes, utilisées si auto = false
    auto: true,        // calculer les macros depuis le poids
    pkg: 2, fkg: 1,    // grammes de protéines / lipides par kilo
    steps: 10000,      // objectif de pas
    goalW: 80,         // objectif de poids
    startW: null,      // poids de départ ; null = première pesée
    step: 2.5,         // taille d'un palier, en kg
    rest: 90,          // durée de repos par défaut, en secondes
    seeded: 1,         // la reprise des anciennes pesées a été proposée
    v2: 1              // marqueur de migration
  },

  weights: { "2026-01-15": 85.0, … },        // une pesée par jour

  act:     { "2026-01-15": { s: 7500, k: 350 } },  // pas (s) et kcal dépensées (k)

  meals:   { "2026-01-15": [ { id, slot, name, kcal, p, c, f } ] },
                       // slot : 'bk' petit-déjeuner, 'lu' déjeuner,
                       //        'di' dîner, 'sn' collations

  foods:   [ { id, name, kcal, p, c, f, fav } ],   // favoris et aliments récents

  routines:[ { id, name, exercises: [ { name, sets: [ { kg, reps } ] } ] } ],
                       // une entrée par série, chacune avec SON poids et SES répétitions
                       // (textes tels que tapés, "" si vide ; au moins une série)
                       // avant 2026.10.14-2 : { name, sets: 3, kg: "60", reps: "8" }, voir Migrations

  sessions:[ { id, name, date, start, dur,
               exercises: [ { name, sets: [ { kg, reps, done } ] } ] } ],

  exercises: [ "Nom d'un exercice créé à la main" ],

  recipes: {
    done:  { "pancakes": { n: 2, last: "2026-10-08" } },  // recettes préparées : nombre de jours, dernière date
    notes: { "pancakes": "avec un peu de cannelle" },       // note personnelle par recette
    mine:  [ { id: "u_ab12", n, s: ["di"], t, k, p, c, f,   // ses propres recettes (valeurs par portion)
               ingTxt: ["150 g de poulet"], st: ["Étape 1"], mine: 1 } ]
  },

  scans:   [ { id, date, name, brand, code, src,
               per: { kcal, fat, sat, carbs, sugar, salt, fiber, prot, fv },
               additives: [ { name, risk } ], lastG,
               cat?: "vpo.poisson",     // rangement choisi (par lui, ou par Claude à la lecture d'une étiquette)
               tags?: ["cheeses"] } ],  // catégories Open Food Facts, sans préfixe de langue
                                        // 400 au maximum

  active:  null,       // la séance en cours, ou null
  ui:      { tab: 'weight' },
  _t:      { … }       // horodatage par tranche, pour la synchronisation
}
```

Les recettes **embarquées** ne sont pas dans l'état : elles sont dans `RECIPES`
(`src/js2c.js`, fichier généré). L'état ne garde que ce que l'utilisateur en fait :
`recipes.done` (clé = identifiant de la recette), `recipes.notes`, `recipes.mine`.
Une recette est comptée une seule fois par jour dans `done`.

`cat` = `section.sous-section` de la bibliothèque (voir `SLIB` dans `src/js4b.js`).
Absent tant qu'il ne l'a pas choisi : le rangement est alors deviné à l'affichage
(`libGuess`) d'après le nom, la marque et `tags`, et rien n'est écrit dans l'état.

`src` d'un produit scanné : `off` (Open Food Facts), `label` (étiquette lue par
Claude), `estimate` (estimé), `manual` (saisi à la main).

## Enregistrement

```js
persist('weights');          // marque la tranche, écrit localStorage,
                             // puis envoie vers la base au bout de 900 ms
persist('meals', '2026-01-15');   // tranches découpées par mois
persist('sessions', '2026-01-15'); // tranches découpées par année
```

`saveLocal()` écrit immédiatement dans `localStorage`. L'envoi vers la base est
regroupé et différé. Les repas et les séances sont découpés en documents
(`meals_2026-10`, `sessions_2026`) pour ne pas tout réécrire à chaque ajout.

## Synchronisation — version Claude uniquement

`initDb()` ouvre une collection privée propre au compte, compare les horodatages
`_t` document par document, applique le plus récent, puis renvoie ce qui manque.
Le téléphone n'a pas cette fonction : `window.claude` n'y existe pas, `initDb()`
sort immédiatement, et `syncState` reste à `local`.

## Export et import

Réglages → **Exporter** produit un fichier JSON :

```json
{ "app": "forme", "v": 1, "date": "2026-10-08", "data": { … } }
```

Sur le téléphone c'est un téléchargement classique. Dans Claude cela passe par la
capacité `downloads`, avec repli sur un bloc de texte à copier.

Réglages → **Restaurer** relit ce fichier et **remplace** l'état. C'est le seul
chemin pour transférer les données d'une version à l'autre.

Les clés `ui` et `_t` sont retirées de l'export.

## Migrations

`migrateSettings()` complète les réglages absents à l'ouverture. Toute nouvelle
clé de `settings` doit être ajoutée à `defaults()` dans `js1.js` : les
installations existantes la récupéreront automatiquement, sans perdre le reste.

Pour une nouvelle tranche de données, l'ajouter aussi à `SLICES` dans `js1.js`,
sinon elle ne sera jamais synchronisée.

### Routines : séries une par une (2026.10.14-2)

`migRoutines(routines)` (`js1.js`) convertit l'ancien format d'un exercice de routine
`{ name, sets: 3, kg: "60", reps: "8" }` en `{ name, sets: [ {kg:"60",reps:"8"} ×3 ] }` :
autant de séries identiques que l'ancien nombre, le poids et les répétitions recopiés dans chacune
(un nombre devient un texte : `42.5` → `"42.5"`). `sets` absent, 0 ou illisible → 3 séries. Les clés
`kg` et `reps` de l'exercice sont retirées. Une routine déjà au nouveau format est seulement
nettoyée (chaque série réduite à `{kg, reps}`). Elle renvoie `true` si quelque chose a changé.

Elle est appelée aux trois portes d'entrée des données :

- **au chargement** de `forme.v1` : la conversion est enregistrée sur l'appareil **sans changer
  l'horodatage** `_t.routines`, et marquée à renvoyer au compte. Ainsi, si le compte a une version
  plus récente (modifiée ailleurs), c'est elle qui gagne à la synchronisation, puis elle est
  convertie à son tour ;
- **à la synchronisation** (`applyDoc`) : une routine reçue à l'ancien format est convertie et
  renvoyée au compte ;
- **à l'import** d'une sauvegarde (Réglages → Restaurer) : une ancienne sauvegarde est convertie
  avant d'être enregistrée.

`index.html` et `forme.html` sont construits depuis les mêmes sources : les deux lisent et écrivent
le nouveau format. Une version **antérieure** à 2026.10.14-2 qui recevrait le nouveau format
(par la synchro de la version Claude) démarrerait les séances de ces routines sans série : il
suffit de la mettre à jour. Le téléphone le fait seul à l'ouverture avec le réseau.

Ce qui ne change pas : la séance en cours (`active`) et l'historique (`sessions`) gardent
`sets: [ { kg, reps, done } ]`. Au démarrage d'une routine, chaque série de la séance reprend le poids
et les répétitions de la série correspondante de la routine.
