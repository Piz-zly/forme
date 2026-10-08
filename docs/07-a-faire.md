# 7. La suite

## Prochain sujet convenu : les recettes

Demandé mot pour mot : « pour les repas il me faudrait un sous onglet avec des
idées de recette en fonction des calories, Protéine, glucide, Lipide restante
(cherche sur les réseaux sociaux ou internet des recettes simples, gourmande,
mais surtout protéiné ou healty). Les recettes qui ont déjà été préparer. »

Ce que cela veut dire :

1. **Un sous-onglet Recettes dans Repas**, à côté du journal.
2. **Un classement par ce qu'il reste** sur la journée : calories, protéines,
   glucides, lipides. Une recette qui tient dans le reste remonte en tête.
3. **Des recettes simples, gourmandes, protéinées ou saines.**
4. **Marquer les recettes déjà préparées** et les retrouver facilement.

Pistes d'implémentation, à valider avec lui :

- Une liste de recettes embarquée dans le code, en français, avec pour chacune :
  nom, temps, ingrédients avec quantités, étapes, et les valeurs par portion
  (kcal, protéines, glucides, lipides).
- Tri par écart aux macros restantes, avec un bandeau « il te reste X kcal et Y g
  de protéines ».
- Un bouton « Ajouter au journal » qui reprend les valeurs de la portion.
- Un marquage « déjà préparée » et une note, conservés dans une nouvelle tranche
  `recipes` de l'état (penser à l'ajouter à `SLICES` et `defaults()`).
- Attention aux droits : **ne pas recopier le texte d'une recette trouvée en
  ligne**. Les ingrédients et les proportions ne sont pas protégés, la rédaction
  l'est. Donc : rédiger les étapes soi-même, ou citer la source avec un lien.

Questions à lui poser avant de coder :

- Combien de recettes au départ, et quelles habitudes alimentaires ? (allergies,
  aliments qu'il ne mange pas, matériel de cuisine)
- Veut-il pouvoir ajouter ses propres recettes ?
- Une recette = une portion, ou un nombre de portions ajustable ?

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
- Aucun test ne couvre les onglets Repas et Scan de bout en bout. Les tests
  existants couvrent Poids, Muscu et le partage entrant.
