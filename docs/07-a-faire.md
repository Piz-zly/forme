# 7. La suite

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
- **35 recettes** au départ, aucune allergie ni aliment exclu connu. Pas de
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

**L'esthétique.** Il a dit vouloir en parler plus tard, et qu'il ajouterait
« probablement des icônes » pour les repas. Les icônes actuelles sont
volontairement rangées dans une seule table, `SLOT_ICONS` en tête de
`src/js2.js`, faciles à remplacer sans toucher au reste.

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
- Les tests couvrent Poids, Muscu, le partage entrant et les recettes (`tests/t8.py`).
  Ni le journal du Repas ni l'onglet Scan n'ont de test de bout en bout.
