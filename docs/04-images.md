# 4. Les images

## Règle

Rien n'entre dans ce dépôt sans licence claire. Le dépôt est public : une image
sous droits publiée ici serait une contrefaçon. Toute source est inscrite dans
`THIRD_PARTY.txt`, accessible depuis le lien « Licences » en bas des Réglages.

L'utilisateur a proposé deux fois des visuels pris sur les réseaux sociaux. La
réponse est non, expliquée, suivie d'une proposition libre équivalente.

## `ill/` — illustrations des mouvements

739 fichiers WebP, environ 3,9 Mo, pour 149 mouvements couvrant **les 175 exercices**
de la bibliothèque (58 mouvements en 2026.10.08-6, 91 ajoutés en 2026.10.14-1).

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

Quelques exercices n'ont qu'une position (`plank`, `side-plank`, `dumbbell-side-bend` : image
`hold` de la collection) : pas de fichier `-1`. Le code le sait par l'ensemble `ILL1` dans
`src/js3b.js`. Pour une image à trois positions (`mid`), on garde départ et arrivée.

### Images partagées ou approchantes

Plusieurs exercices partagent une image (« Fentes » et « Fentes marchées »). Depuis 2026.10.14-1,
les exercices sans illustration exacte dans la collection ont, à sa demande, l'image **la plus
proche** plutôt que rien. Choix validés avec lui le 14 octobre 2026 :

| Exercice | Image | Écart |
|---|---|---|
| Développé couché haltères prise neutre | dumbbell-chest-press | prise non visible de profil |
| Pull-over poulie corde | straight-arm-pulldown | barre au lieu de la corde |
| Soulevé de terre jambes tendues | romanian-deadlift | même image que le roumain |
| Développé épaules Smith | smith-machine-overhead-press | debout au lieu d'assis |
| Développé haltères debout | dumbbell-push-press | genoux un peu fléchis au départ |
| Curl marteau incliné | incline-dumbbell-curl | prise non visible de profil |
| Curl machine | machine-preacher-curl | même image que le curl pupitre machine |
| Extension poulie prise inversée / barre en V / un bras | tricep-pushdowns | prise, poignée ; deux mains |
| Extension nuque un bras / barre | overhead-triceps-extension | un haltère tenu à deux mains |
| Dips triceps | dips | même image que « Dips » |
| Presse pieds serrés | leg-press | même image que la presse |
| Leg extension unilatéral | leg-extension | une ou deux jambes : invisible de profil |
| Écarté décliné haltères | dumbbell-fly | banc plat |
| Écarté incliné poulie | cable-fly-low-to-high | debout, pas sur un banc |
| Rowing haltères deux bras | bent-over-row | barre au lieu des haltères |
| Tirage vertical un bras | lat-pulldown | deux bras |
| Shrugs machine | smith-machine-shrug | Smith debout au lieu de la machine assise |
| Développé militaire assis | overhead-press | debout |
| Élévations latérales assis | lateral-raises | debout |
| Oiseau poulie | reverse-pec-deck | machine au lieu des poulies |
| Oiseau assis | rear-delt-fly | debout penché |
| Curl poulie haute | cable-curl | poulie basse |
| Box squat | box-squat | sans barre |

### Comment elles ont été fabriquées

1. **Correspondance** — `tools/exercices_map.py` associe chaque nom français à un
   identifiant de la collection. C'est le seul fichier à compléter pour ajouter un
   exercice.
2. **Recadrage** — `tools/recadre.py` (écrit en 2026.10.14-1 ; l'outil d'origine n'avait pas été
   gardé). Chaque image est recadrée sur l'union des silhouettes (pixels plus clairs que 60) de
   départ et d'arrivée, avec 5 % de marge, étendue au format 3:2, puis ramenée à 720 × 480 ;
   vignette carrée de 176 px centrée sur la même zone. Les défauts d'une image source peuvent être
   effacés avant recadrage (`NETTOIE` : un bout de pied coupé en bas de `leg-raises`). Le recadrage est **identique pour
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
     secondaires ;
   - adducteurs et abducteurs (ajoutés en 2026.10.14-1) : capsule hanche→genou décalée vers
     l'intérieur ou l'extérieur de la cuisse ;
   - deux secours, seulement en cas d'échec : personnage non reconnu (tête en bas, ex.
     `back-extensions`) → la détection est refaite sur l'image tournée ; muscle principal caché par
     le short (fessiers) → la couleur est aussi posée sur le tissu, pour les deux positions du
     mouvement afin que l'animation ne clignote pas.

   ```bash
   pip install ultralytics pillow numpy      # PyTorch : Python 3.12 (pas encore de 3.15)
   curl -L -o yolo11x-pose.pt \
     https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-pose.pt
   export FORME_ATELIER=/chemin/hors/depot FORME_YOLO=/chemin/yolo11x-pose.pt
   # dans l'atelier : zones_todo.json et src/<id>-start|end|hold.webp
   python3 tools/recadre.py                  # -> atelier/out/
   python3 tools/paint.py                    # -> atelier/red/ (tout)
   python3 tools/paint.py bench-press squat  # seulement ces identifiants
   ```

   Ni l'atelier, ni les images sources, ni le modèle n'entrent dans le dépôt. Copie ensuite dans
   `ill/` : `out/<id>-0` → `<id>-0`, `red/<id>-0` → `<id>-0r`, idem `-1`, `out/<id>-t` → `<id>-t`.
   En 2026.10.14 sous Windows : environnement Python 3.12 créé avec `uv`, PyTorch pour processeur.

4. **Vérification** — les 115 images ont été relues une par une sur des planches
   de contact. Deux imperfections connues et assumées : sur un exercice de bras vu
   de face, bras le long du corps, le rouge déborde un peu sur le buste ; sur les
   mollets assis vus de profil, la couleur apparaît côté tibia, le mollet étant
   caché.

   Les 91 mouvements de 2026.10.14-1 ont été relus de même (planches départ, arrivée, vignette,
   puis versions colorées). Imperfections connues : vue de profil, quadriceps et ischio-jambiers
   tombent sur la même zone de la cuisse (good morning, soulevé de terre roumain haltères) ; les
   fessiers et adducteurs sous le short sont colorés sur le tissu (pont fessier, kickback, pull
   through, machines adducteurs et abducteurs) ; les muscles secondaires fins (avant-bras) se voient
   peu ; l'image d'arrivée de `leg-raises` a les pieds au ras du bord (image source ainsi).

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
