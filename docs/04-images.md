# 4. Les images

## Règle

Rien n'entre dans ce dépôt sans licence claire. Le dépôt est public : une image
sous droits publiée ici serait une contrefaçon. Toute source est inscrite dans
`THIRD_PARTY.txt`, accessible depuis le lien « Licences » en bas des Réglages.

L'utilisateur a proposé deux fois des visuels pris sur les réseaux sociaux. La
réponse est non, expliquée, suivie d'une proposition libre équivalente.

## `ill/` — illustrations des mouvements

288 fichiers WebP, environ 2,1 Mo, pour 58 mouvements couvrant les 60 exercices
de la bibliothèque.

Source : [Open Exercise Illustrations](https://github.com/hitmanrepo/open-exercise-illustrations),
**CC0 1.0** (domaine public). Images générées par IA, non validées par un coach :
c'est écrit dans `THIRD_PARTY.txt` et cela a été dit à l'utilisateur.

Nommage, pour un identifiant `bench-press` :

| Fichier | Rôle |
|---|---|
| `bench-press-0.webp` | position de départ, sans couleur |
| `bench-press-1.webp` | position d'arrivée, sans couleur |
| `bench-press-0r.webp` | départ, muscles en rouge |
| `bench-press-1r.webp` | arrivée, muscles en rouge |
| `bench-press-t.webp` | vignette carrée 176 px |

Quelques exercices n'ont qu'une position (`plank`) : pas de fichier `-1`. Le code
le sait par l'ensemble `ILL1` dans `src/js3b.js`.

### Comment elles ont été fabriquées

1. **Correspondance** — `tools/exercices_map.py` associe chaque nom français à un
   identifiant de la collection. C'est le seul fichier à compléter pour ajouter un
   exercice.
2. **Recadrage** — chaque image est recadrée sur l'union des silhouettes de
   départ et d'arrivée, étendue au format 3:2. Le recadrage est **identique pour
   les deux positions**, sinon l'animation saute. Le débordement est comblé en
   noir, ce qui est invisible sur ce fond.
3. **Coloration** — `tools/paint.py`. Une page web ne peut pas « allumer » un
   muscle sur une image plate ; la méthode retenue :
   - détection de posture avec **YOLO11x-pose** (17 points : épaules, coudes,
     poignets, hanches, genoux, chevilles) ;
   - la fonction `zones()` traduit un nom de muscle français en formes placées sur
     ces points. Exemple : pectoraux = disque entre le milieu des épaules et le
     milieu des hanches, à 30 % ; quadriceps = capsule le long de hanche→genou ;
     biceps = capsule le long d'épaule→coude ;
   - les formes sont floutées puis appliquées **uniquement sur les pixels clairs**
     du personnage, jamais sur la barre, le banc ou le fond ;
   - rouge vif à 88 % pour les muscles principaux, rose à 55 % pour les
     secondaires.

   ```bash
   pip install ultralytics pillow numpy
   curl -L -o yolo11x-pose.pt \
     https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-pose.pt
   python3 tools/paint.py                    # tout
   python3 tools/paint.py bench-press squat  # seulement ces identifiants
   ```

   Les chemins en tête de `paint.py` sont ceux de l'atelier d'origine : les
   adapter avant de relancer.

4. **Vérification** — les 115 images ont été relues une par une sur des planches
   de contact. Deux imperfections connues et assumées : sur un exercice de bras vu
   de face, bras le long du corps, le rouge déborde un peu sur le buste ; sur les
   mollets assis vus de profil, la couleur apparaît côté tibia, le mollet étant
   caché.

## `img2/` — schémas anatomiques

Deux silhouettes, face et dos, muscles principaux en rouge et secondaires en rose,
une paire par exercice (`<slug>-m.png`), plus une vignette inutilisée
(`<slug>-t.png`).

Tracés vectoriels repris de
[react-body-highlighter](https://github.com/giavinh79/react-body-highlighter),
**MIT, © 2020 GV79**. Le rendu est fait par `tools/gen_schemas_muscles.py`.

Attention : ces fichiers utilisent **l'ancien système d'identifiants**, celui de
`EXI[nom].i` dans `src/js3.js` (`barbell-bench-press-medium-grip`), différent de
celui de `ill/` (`bench-press`). Les deux cohabitent volontairement.

## `icons/` — icônes de l'application

Générées pour ce projet : un anneau en quatre quarts aux couleurs des quatre
onglets. Tailles 192, 512, 512 masquable et 180 pour Apple. Déclarées dans
`manifest.webmanifest`.

## `vendor/zxing.min.js`

[ZXing](https://github.com/zxing-js/library), **Apache-2.0**, copié en local pour
que la lecture des codes-barres fonctionne hors ligne. La version Claude charge
la même bibliothèque depuis un CDN, faute de pouvoir servir un fichier local.

## Ajouter un exercice

1. Ajouter le nom français dans `LIB` (`src/js3.js`), dans le bon groupe.
2. Ajouter une entrée dans `EXI` : `{ i: '<slug ancien système>', m: [...], s: [...] }`
   pour le schéma anatomique et les listes de muscles.
3. Ajouter la correspondance dans `ILL` (`src/js3b.js`) vers un identifiant de la
   collection d'illustrations.
4. Produire les cinq fichiers de `ill/` avec les outils ci-dessus.
5. Reconstruire, tester, publier.


## Décors de fond (ambiances Lune et Sakura)

Dessins originaux, tracés par des scripts : `tools/gen_lune.py` (ciel étoilé, lune au trait d'encre,
nuages en volutes) et `tools/gen_sakura.py` (branches de cerisier, mont Fuji). `tools/gen_decor.py`
les assemble dans `src/p1.html`. Aucune image tierce, rien à déclarer dans `THIRD_PARTY.txt`.
Les images de référence envoyées par l'utilisateur (photos, fond d'écran tiré d'un manga) n'ont servi
qu'à l'ambiance : on n'en reprend ni les personnages ni la composition.
