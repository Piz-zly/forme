# 7. La suite

Pour agrandir encore : une ligne `F(...)` dans `tools/gen_aliments.py`, un appel
`rec(...)` dans `tools/gen_recettes.py` (les aliments d'une recette doivent exister
dans sa table `ALIM`, qui est séparée de celle de la recherche), puis relancer les
scripts et `./src/build.sh`. Pensé pour s'agrandir ainsi, sans toucher au reste.

## Animations douces : faites en 2026.10.13-5, à essayer sur son téléphone

Journal du Repas, routine, pesées, bibliothèque du Scan (`src/js1b.js`). À voir avec lui : la
fluidité sur son téléphone, si c'est assez discret ou trop discret. **Séance Muscu : volontairement non
animée**, à reprendre seulement s'il le demande (séries validées, avec les précautions déjà notées :
jamais de retard sur l'enregistrement ni sur le minuteur, pas d'effacement différé, focus des
champs kg/reps). Favoris : écartés (peu utile).

## Recherche tolérante aux fautes : faite en 2026.10.13-4, à essayer sur son téléphone

Fuse.js dans les quatre recherches (aliments, exercices, bibliothèque du Scan, favoris). À voir avec lui :
les fautes qu'il fait vraiment au clavier et qui ne sont pas rattrapées (les ajouter à `tests/t14.py`),
ou au contraire des corrections qui le surprennent. Réglage : `FZ_T` et la règle des fautes dans
`fzAlts` (`src/js2f.js`). Non testable ici : le clavier Android (correcteur automatique, saisie
prédictive, majuscule automatique, glissement), qui peut lui-même modifier ce qui est tapé.

## Exercices enrichis : fait en 2026.10.13-2, à essayer sur son téléphone

175 exercices (115 nouveaux), consignes en français, équipement, filtres Muscle et Équipement. À voir
avec lui : les exercices qui manquent ou qui sont en trop, les noms (« Face pull », « Hip thrust »,
« Rack pull », « Good morning »… gardés en anglais comme en salle), la clarté des consignes. Les
illustrations sont faites en 2026.10.14-1 (voir ci-dessous). Les schémas
`img2/` ne montrent pas les muscles secondaires ajoutés (ischio-jambiers du soulevé de terre…) :
il faudrait les régénérer avec `tools/gen_schemas_muscles.py`. Lisibilité des menus déroulants et des
consignes à vérifier sur son écran.

## Poids détaillé : fait en 2026.10.14-3, à essayer sur son téléphone

À vérifier sur son téléphone : le téléchargement du CSV et le sélecteur de fichier d'Android, la
lecture du fichier dans Excel ou Google Sheets, la lisibilité des couleurs (vert / orange) et des
séparateurs de semaine. À lui proposer, sans l'ajouter d'office : utiliser la dépense estimée comme
repère pour l'objectif de calories.

## Routines série par série : fait en 2026.10.14-2, à essayer sur son téléphone

À vérifier avec lui : le clavier qui s'ouvre (décimal pour le poids, avec virgule ; numérique pour les
répétitions), la taille des champs et de la croix au doigt, que l'écran ne saute pas pendant la
saisie, et que ses routines existantes sont bien là avec leurs valeurs. Idées en attente, non
demandées : « Enregistrer comme routine » pourrait reprendre les poids réellement faits (aujourd'hui,
comme avant, séries vides) ; une flèche pour recopier une série sur les suivantes.

## Illustrations des 115 exercices : fait en 2026.10.14-1, à essayer sur son téléphone

Les 175 exercices ont une illustration animée (91 nouveaux mouvements, Open Exercise Illustrations,
CC0) ; liste des images approchantes dans `docs/04-images.md`. À voir avec lui : les approchantes qui
le gênent (les retirer alors de `ILL` et de `tools/exercices_map.py`), la lisibilité des vignettes sur
son écran, le chargement hors ligne (`ill/` passe de 1,4 à 3,9 Mo, chargé à la demande puis gardé en
cache par `sw.js`).

**Schémas anatomiques `img2/` encore manquants** (autre système d'identifiants, `EXI[nom].i`) : aucun
des 115 exercices ajoutés en 2026.10.13-2 n'en a. Pectoraux : Développé couché prise large,
Développé couché Smith, Développé incliné Smith, Développé décliné haltères, Développé couché haltères
prise neutre, Développé incliné machine, Écarté incliné haltères, Écarté décliné haltères, Écarté poulie
basse, Écarté incliné poulie, Pull-over haltère, Pompes pieds surélevés, Pompes inclinées, Pompes prise
large. Dos : Rowing haltères deux bras, Rowing barre prise inversée, Rowing sur banc incliné, Rowing
poulie un bras, Rowing machine, Rowing Smith, Rowing kettlebell un bras, Tirage vertical prise inversée,
Tirage vertical prise neutre, Tirage vertical un bras, Pull-over poulie corde, Shrugs barre, Shrugs
machine, Soulevé de terre sumo, Rack pull, Soulevé de terre jambes tendues, Good morning, Extensions
lombaires. Épaules : Développé militaire assis, Développé épaules machine, Développé épaules Smith,
Développé haltères debout, Élévations latérales assis, Élévation latérale poulie, Élévations frontales
poulie, Oiseau machine, Oiseau poulie, Oiseau assis, Rowing menton barre, Rowing menton haltères, Rowing
menton poulie, Rotation externe poulie, Écartement élastique. Bras : Curl barre EZ, Curl concentré, Curl
haltères alterné, Curl haltères assis, Curl marteau poulie corde, Curl marteau incliné, Curl pupitre
haltère, Curl pupitre machine, Curl araignée, Curl inversé barre, Curl Zottman, Curl poulie haute, Curl
machine, Kickback haltère, Extension poulie prise inversée, Extension poulie barre en V, Extension poulie
un bras, Extension nuque barre, Extension nuque un bras, Extension couché haltères, Extension triceps
machine, Dips triceps, Dips machine, Pompes serrées, Développé serré haltères, Développé au sol, Curl
poignets barre, Curl poignets inversé. Jambes : Squat Smith, Squat haltères, Squat poids du corps, Box
squat, Squat sumo haltère, Squat bulgare, Hack squat machine, Presse pieds serrés, Fentes barre, Fentes
arrière, Montées sur banc, Leg extension unilatéral, Leg curl debout, Soulevé de terre roumain haltères,
Pont fessier barre, Pont fessier, Pont fessier une jambe, Kickback fessier poulie, Pull through poulie,
Adducteurs machine, Abducteurs machine, Mollets à la presse, Mollets haltères, Mollets Smith. Abdos :
Crunch inversé, Crunch oblique, Crunch machine, Crunch décliné, Crunch vélo, Relevé de jambes allongé,
Relevé de genoux chaise romaine, Sit-up, Russian twist, Gainage latéral, Roulette abdominale, Bûcheron
poulie, Pallof press, Dead bug, Mountain climber, Flexion latérale haltère. La fiche s'en passe proprement
(muscles en pastilles) ; les produire demanderait d'étendre `tools/gen_schemas_muscles.py` pour
partir des noms de muscles plutôt que de l'identifiant de l'ancienne base.

## Bibliothèque du Scan : fait en 2026.10.08-11 (doublons et aliments de base en -12), à essayer sur son téléphone

Demandé : une bibliothèque des aliments scannés, triés en sections et sous-sections
(exemple donné : VPO = viandes / poissons / œufs), « pareil avec les autres
aliments ». À valider avec lui : les noms des sections, les sous-sections qui
manquent, les produits mal rangés (corriger les règles de `SLIB_RULES`). Les
catégories Open Food Facts (`tags`) ne sont enregistrées que pour les produits
scannés **après** cette version : les anciens sont rangés d'après leur nom
seulement. Pas essayé sur téléphone.

## Chercher un aliment : fait en 2026.10.08-9, à essayer sur son téléphone

Demandé : « ajouter au Repas des aliments basic sans code barre, comme les œufs.
En les cherchant avec une barre de recherche. » 163 aliments, voir
`tools/gen_aliments.py`. À valider avec lui : les aliments qu'il cherche et qui
manquent (les ajouter), et si les valeurs moyennes lui conviennent. Les valeurs
du cacao diffèrent un peu entre `gen_recettes.py` et `gen_aliments.py` : à
harmoniser si besoin. Pas essayé sur téléphone (clavier Android, défilement de
la feuille).

## Recettes : fait en 2026.10.08-8, restent à valider avec lui

Demandé mot pour mot : « pour les repas il me faudrait un sous onglet avec des
idées de recette en fonction des calories, Protéine, glucide, Lipide restante
(cherche sur les réseaux sociaux ou internet des recettes simples, gourmande,
mais surtout protéiné ou healty). Les recettes qui ont déjà été préparer. »

Ce qui a été fait : voir `docs/06-journal.md`. Les recettes sont **rédigées pour
l'application** (ingrédients et proportions, étapes dans nos mots) : rien n'est
recopié d'un site ou d'un réseau social. Calories et macros sont **calculées** à
partir d'une table de valeurs moyennes par aliment, dans `tools/gen_recettes.py`
(à relancer après toute modification, puis `./src/build.sh`).

Choix faits sans lui poser la question, à lui confirmer :

- Une recette = **une portion**, avec un choix ½ / 1 / 1,5 / 2 sur la fiche.
- **35 recettes** au départ (74 depuis 2026.10.08-10), aucune allergie ni aliment exclu connu. Pas de
  matériel particulier (poêle, four, micro-ondes, mixeur).
- Il peut **ajouter ses propres recettes** (valeurs saisies à la main).
- Ajouter une recette au journal la marque aussi « préparée ».

Pour agrandir la liste : ajouter un appel `rec(...)` dans `tools/gen_recettes.py`
avec des aliments de la table `ALIM` (en ajouter si besoin), relancer le script.
Il refuse une recette dont les macros ne collent pas aux calories (écart de plus
de 8 %) ou qui a moins de 15 g de protéines.

Pistes non faites : recherche par mot dans les recettes, liste de courses,
recettes favorites, un filtre « sans viande de porc / sans lactose » si besoin.

## Demandé plus tôt, en attente

**L'esthétique : faite en 2026.10.08-13 à -16, à essayer sur son téléphone.** Trois ambiances au
choix (Réglages → Ambiance) : **Lune** par défaut (nuit violette éclairée, lune, nuages japonais, inspirée
de l'ambiance de son fond d'écran sans en reprendre le personnage), **Sakura** (claire, cerisiers),
**Néon** (sombre, style jeu vidéo). Bandeau de niveau : un niveau par palier de poids franchi. Les icônes de
repas sont toujours dans `SLOT_ICONS` en tête de `src/js2.js`. À lui demander : quelle ambiance il garde,
si les cartes doivent laisser voir davantage le décor.

**Motivation : demandée le 8 octobre, à faire, dans cet ordre s'il le confirme.**
- **Série de jours** (jours d'affilée avec une pesée, un repas noté ou une séance).
- **Résumé de la semaine** (poids perdu, séances, jours dans l'objectif, petit mot d'encouragement).
- **Coach « Maître »** : petit personnage chibi qui l'encourage, façon BitePal. Il a demandé Toji Fushiguro
  (Jujutsu Kaisen) : refusé, personnage protégé. Faire un personnage **original**, dessiné par nous.

**L'import d'un fichier de podomètre.** Proposé, non retenu pour l'instant : il a
choisi le menu Partager. À ressortir si le partage de Step Counter Pedometer
envoie une image plutôt qu'un texte — dans ce cas la fenêtre s'ouvre avec les
champs vides, et c'est le signe qu'il faut passer à l'import de fichier.

## Idées non demandées, à proposer seulement si l'occasion se présente

- Une vue hebdomadaire des calories, pour juger la tendance plutôt que la journée.
- Le volume par groupe musculaire sur la semaine, dans Muscu.
- Un rappel de pesée. Il faudrait les notifications ; à ne proposer que s'il en
  parle.
- Le mode sombre existe déjà par le réglage du téléphone ; un réglage manuel dans
  l'application n'a pas été demandé.

## Dettes techniques connues

- Deux systèmes d'identifiants coexistent pour les exercices : celui de `EXI[].i`
  pour les schémas anatomiques, celui de `ILL[]` pour les illustrations. Les
  unifier demanderait de régénérer `img2/`. Sans urgence, mais à savoir.
- `tools/paint.py` et `tools/gen_schemas_muscles.py` contiennent des chemins
  absolus de l'atelier d'origine. À adapter avant toute réexécution.
- Deux imperfections assumées sur la coloration des muscles, décrites dans
  `docs/04-images.md`.
- Les tests couvrent Poids, Muscu, le partage entrant et les recettes (`tests/t8.py`) et l'ajout d'un aliment par la recherche (`tests/t9.py`).
  Ni le journal du Repas ni l'onglet Scan n'ont de test de bout en bout.
