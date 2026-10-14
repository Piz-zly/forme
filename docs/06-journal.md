# 6. Journal des versions

Les versions suivent `AAAA.MM.JJ-n`, `n` étant le numéro dans la journée. La
version courante est déclarée dans `src/js1.js` et affichée en bas des Réglages.

---

### 2026.10.14-5 — Muscu : records, types de série, suggestion de charge, séries par muscle, écran allumé (à essayer sur le téléphone)

- **Records en direct** : à la validation d'une série, comparaison avec toutes les séries de travail déjà
  faites sur l'exercice (séances enregistrées + séance en cours) ; bannière « 🏆 Record ! Squat 100 kg × 5
  (avant : 97,5 × 5) » sous la série, qui s'efface après 5 s et ne bloque rien. Ordre : charge max > 1RM
  estimé > répétitions à cette charge > volume. Premier enregistrement = pas de record. Liste gardée avec la
  séance (`prs`), affichée à la fin et dans le détail de la séance. Pas de confettis (chantier Motivation).
- **Types de série** : appui sur le numéro → Normale, Échauffement (« É », grisé), Échec (« E »), Drop set
  (« D ») ; aussi dans les routines (« Échauff. », « Échec », « Drop set ») et l'historique. Les séries
  normales restent numérotées 1, 2, 3 sans compter les autres. Minuteur de repos inchangé.
- **Suggestion de charge** (double progression) : en haut de l'exercice, d'après la dernière séance (un
  appui pré-remplit la charge des séries pas encore validées), et sous les séries pendant la séance pour la
  prochaine fois. Une ligne, couleur douce, mot « Suggestion ». Réglages → Muscu : palier (2,5 kg),
  fourchette (10–12), activation.
- **Séries par muscle (7 jours)** : carte repliable dans Progression, +1 muscle principal, +0,5 secondaire,
  repère courant 10 à 20 (zone claire). Barres seulement : les schémas `img2/` sont par exercice, il n'y a
  pas de schéma du corps entier à colorier sans nouveau fichier.
- **Écran allumé** (téléphone) : Screen Wake Lock pendant une séance en cours, redemandé au retour au
  premier plan, relâché à la fin, à l'abandon et en quittant ; réglage (activé par défaut). Rien dans
  `forme.html`. Non vérifiable dans Chromium de test : à confirmer sur son téléphone.
- Formules écrites à la main (Epley déjà présent) ; aucune dépendance. Test : `tests/t19.py`.

### 2026.10.14-4 — Repas : ajouts rapides, semaine, courses, frigo, bilan, étiquettes (à essayer sur le téléphone)

- **Ajouts rapides** : raccourcis +100 / +200 / +300 / +500 dans « Manuel », nom facultatif (« Ajout
  rapide »), favori proposé seulement avec un nom ; « Copier d'un jour » sous chaque repas et « Copier une
  journée entière » (28 derniers jours, nouveaux identifiants) ; **repas types** (« Enregistrer comme repas
  type », en haut de Favoris, ajout en un geste, suppression) ; « Souvent à ce repas » (2 fois au moins sur
  60 jours, 4 au plus, en haut de Chercher et dans Favoris).
- **Fiabilité** : source dans la fiche d'un aliment ; « Corriger les valeurs » (pour les ajouts futurs,
  « Rétablir l'original », `S.fixes`) ; « Version cuite / crue » quand le jumeau existe.
- **Recettes** : portions et « Calculer les valeurs » (`parseIng` lit « 150 g de poulet », « 2 œufs »,
  « 1 càs d'huile »), « Ajouter à ma liste de courses » dans la fiche ; **Mon frigo** (cases, « Avec mon
  frigo », pastille « Il manque 2 ingrédients » ; sel, poivre, eau, huile, épices toujours présents).
- Nouveaux sous-onglets **Semaine** (planning de 7 jours, ✓ vers le journal, liste de courses additionnée,
  par rayon, cases, ajouts, « Ranger dans mon frigo ») et **Bilan** (barres des 7 jours, moyennes, série qui
  pardonne un oubli par semaine, calendrier du mois coloré, toucher un jour l'ouvre). Série aussi sous le
  cercle du Journal. Barre de 5 sous-onglets lisible à 384 px.
- **Étiquette en photo, hors ligne** (téléphone) : Tesseract.js 7.0.0 + tesseract.js-core 6.1.2 (simd-lstm)
  + modèle français (tessdata_best en entiers) dans `vendor/ocr/` (≈ 4,8 Mo, chargés au premier usage,
  jamais d'un CDN, pas précachés). Boutons Photo / Galerie dans « Manuel », la fiche « produit inconnu » du
  Scanner et l'onglet Scan sans vision. Feuille de vérification obligatoire (photo, nom, 8 valeurs, alertes,
  texte lu, conversion portion -> 100 g). Sur de fausses étiquettes : nette 8/8, deux colonnes 8/8, floue et
  penchée 7/8 (sucres lus 46 au lieu de 4,6, signalé).
- Non faits : import d'une recette depuis un site (le navigateur bloque la lecture d'un autre site sans
  serveur) ; photo du frigo (il faudrait un modèle de vision sur le téléphone ou un envoi de la photo,
  qu'il a refusé) : remplacée par « Mon frigo » à cocher.
- `reSheet()` : une feuille se met à jour sans rejouer son ouverture. Tests : `tests/t17.py`, `tests/t18.py`,
  `tests/t8.py` adapté (cinq sous-onglets).

### 2026.10.14-3 — Poids : détails, historique par semaine, CSV, dépense estimée (à essayer sur le téléphone)

- Carte des statistiques : les trois cases restent ; dessous, « Plus de détails » (fermé par défaut,
  état gardé sur l'appareil) : plus bas, plus haut, moyenne 30 jours, variations 7 / 30 / 90 jours
  (vert vers l'objectif, orange sinon, « — » s'il manque des données), IMC avec un mot (si la taille
  est renseignée, « indicatif »), dépense estimée.
- Historique : écart avec la pesée précédente coloré selon l'objectif (gris sans objectif), un
  séparateur discret par semaine (« Semaine du 6 oct. · moyenne 83,4 kg · −0,6 kg »), carte repliable
  par son titre (« 42 pesées · dernière : 83,4 kg »), en douceur ; « Tout afficher » inchangé.
- Réglages : champ **Taille (cm)**, à côté du poids visé ; **Exporter les pesées (CSV)** et **Importer
  des pesées (CSV)**, avec aperçu et choix avant toute écriture (`docs/03-donnees.md`).
- Dépense estimée : kcal mangées en moyenne − 7 700 × pente du poids, sur 28 jours ; seulement avec
  assez de pesées et de repas notés. Indicative, ne change aucun objectif.
- `js1b.js` : une zone animée vide compte aussi, pour que l'historique rouvert apparaisse en douceur.
- Test : `tests/t16.py` (statistiques, historique, export et import CSV, dépense estimée, taille).

### 2026.10.14-2 — Routines : un poids et des répétitions par série (à essayer sur le téléphone)

- Demandé : régler chaque série d'une routine séparément (ex. 60 kg × 10, 70 kg × 8, 75 kg × 6) au lieu
  d'un seul poids et d'un seul nombre de répétitions pour toutes.
- En ajoutant un exercice à une routine, l'appli demande « Combien de séries ? » (1 à 8, 3 par
  défaut) ; Annuler n'ajoute rien. L'exercice apparaît avec une ligne par série (Série 1, Série 2…),
  chacune avec son poids (clavier décimal) et ses répétitions (clavier numérique). « Ajouter une
  série » recopie la dernière ; la croix supprime une série (il en reste toujours une). Le − / + du
  nombre de séries disparaît.
- Sous le nom de l'exercice, un résumé : « 3 × 8 · 60 kg », ou « 3 séries · 60–75 kg · 6–10 reps »
  quand les séries diffèrent. La liste des routines indique le total : « 2 exercices · 5 séries ».
- Au démarrage, chaque série de la séance est pré-remplie avec SA valeur. La séance, l'historique et
  la progression ne changent pas.
- Données : nouveau format `sets: [ {kg, reps}, … ]`. Les anciennes routines sont converties toutes
  seules, sans perte (3 séries à 60 × 8 restent 3 séries à 60 × 8), à l'ouverture, à l'import d'une
  ancienne sauvegarde et à la synchronisation (`docs/03-donnees.md`).
- Tests : `tests/t6.py` réécrit (parcours complet, rechargement, séance, conversion au chargement, à
  l'import et par la synchro simulée) ; t13 et t15 valident la nouvelle question.

### 2026.10.14-1 — Une illustration pour chacun des 175 exercices (à essayer sur le téléphone)

- Demandé : des images pour les 115 exercices ajoutés en 2026.10.13-2, uniquement depuis la collection
  déjà utilisée (Open Exercise Illustrations, CC0). Correspondance proposée exercice par exercice
  (89 exactes, 13 proches, 13 sans équivalent), validée par lui ; pour les 13 sans équivalent il a
  préféré l'image la plus proche plutôt que rien (liste et écarts dans `docs/04-images.md`).
- 91 mouvements nouveaux (451 fichiers, +2,5 Mo dans `ill/`, 3,9 Mo au total), même format que les
  58 existants (720 × 480, vignette 176 px, version colorée). Deux mouvements à une seule position
  (Gainage latéral, Flexion latérale haltère) ajoutés à `ILL1`. Aucun fichier existant modifié.
- Outils : `tools/recadre.py` (nouveau, l'outil de recadrage d'origine n'était pas dans le dépôt) ;
  `tools/paint.py` prend ses chemins dans `FORME_ATELIER` et `FORME_YOLO` (plus de chemin en dur), sait
  colorer adducteurs et abducteurs, retente la détection sur l'image tournée (personnage tête en bas)
  et colore le short quand les fessiers sont cachés dessous.
- Toutes les planches (recadrées puis colorées) relues ; corrigés : un bout de pied parasite en bas
  de l'image source du relevé de jambes, l'extension lombaire non colorée au départ, les fessiers
  invisibles du kickback à la poulie.
- `tests/t13.py` : les 175 fiches s'ouvrent avec leur illustration, sans image cassée (en couleur et
  en image simple) ; les 164 vignettes de la liste se chargent ; un exercice perso garde sa vignette
  lettre et une fiche « Pas d'illustration » propre.

### 2026.10.13-5 — Animations douces, outil maison (à essayer sur le téléphone)

- Demandé : des animations discrètes quand une ligne apparaît, disparaît ou change de place.
  AutoAnimate **non retenu** : l'appli redessine l'écran entier à chaque action (il n'aurait rien
  animé sans refaire le dessin de tous les onglets), et il n'existe qu'en module. Remplacé par un
  outil maison, `src/js1b.js` (aucune dépendance, rien dans `THIRD_PARTY.txt`).
- Quatre endroits : **journal du Repas** (aliment ajouté qui apparaît, aliment supprimé qui s'efface),
  **routine** (exercice qui glisse quand on le monte ou le descend, ajouté, retiré), **pesées** (nouvelle
  pesée), **bibliothèque du Scan** (produit retiré, sections qui se décalent, section ouverte). La séance
  Muscu n'est **pas** animée, à sa demande (« ignore complètement la séance Muscu pour l'instant »).
- Règles : apparence seulement (opacité, déplacement), 200 ms (150 ms pour un effacement) ; données
  enregistrées et écran redessiné avant toute animation ; un effacement est une copie inerte (aucun
  clic, aucune donnée) ; rien au-delà de 60 lignes, rien pendant une recherche, rien si le téléphone
  demande de réduire les animations ; en cas d'erreur, l'appli dessine comme avant.
- Test : `tests/t15.py` (chaque cas en mode normal puis « réduire les animations », deux suppressions
  coup sur coup, plafond de 60 lignes).

### 2026.10.13-4 — Recherches tolérantes aux fautes de frappe (à essayer sur le téléphone)

- **Pourquoi une dépendance :** avec plus de 3 500 aliments et 175 exercices, une faute de frappe
  (« saumom », « tracion ») ne trouvait plus rien, et Fuse.js (19 ko, sans dépendance, Apache-2.0)
  propose les mots voisins de façon fiable sans qu'on ait à écrire et maintenir ce moteur nous-mêmes.
- Version 7.2.0, la dernière livrée en fichier « navigateur » classique (les 7.3 à 7.5 n'existent
  qu'en module) ; variante « basic ». Copiée dans `vendor/`, chargée par `index.html`, mise en cache
  par `sw.js` ; intégrée telle quelle dans `forme.html` par `build.sh`.
- Quatre recherches : Chercher (aliments, Ciqual comprise), Ajouter un exercice, bibliothèque du Scan,
  Favoris/Récents du Repas. Toutes cherchent maintenant pareil : accents, œ/æ, apostrophes, tirets et
  pluriel ignorés, mots dans n'importe quel ordre (avant : exercices et Scan cherchaient la phrase d'un
  bloc ; les favoris ne géraient pas les accents).
- Méthode : recherche exacte d'abord, inchangée. Seul un mot tapé introuvable dans la liste est remplacé
  par des mots voisins proposés par Fuse.js, gardés seulement à 1 faute (4-5 lettres) ou 2 fautes
  (6 lettres et plus, première lettre juste). Ce qui est trouvé sans correction passe toujours devant.
- Mesures (`tests/t14.py`) : 15 recherches avec fautes réussies sur 15 (avant : 4) ; 12 recherches sans
  faute identiques à avant ; rien pour « voiture », « ordinateur », « chaussure » ; 8 524 aliments
  (5 000 fictifs ajoutés) : 2,7 ms par lettre tapée en moyenne, 12 ms au pire.
- Exercices : à égalité, le nom le plus court passe devant (« Élévations latérales » avant « Élévation
  latérale poulie »).

### 2026.10.13-3 — Choix de la prise sur la carte de l'exercice (à essayer sur le téléphone)

- Demandé : « pour les exercices avec beaucoup de prises différentes, pour éviter de surcharger
  l'espace de recherche ».
- 7 familles : Tirage vertical (Large, Serrée, Inversée, Neutre), Extension poulie (Barre, Corde,
  Barre en V, Inversée), Tractions, Rowing barre, Curl barre (Normale, Inversée), Développé couché
  (Normale, Large), Développé couché haltères (Normale, Neutre). La liste « Ajouter un exercice » ne
  montre que le premier (« · 4 prises ») ; une recherche qui ne trouve qu'une prise (« corde ») la
  montre directement.
- Sur la carte, en séance comme en routine : « Prise : » suivi des boutons. Choisir une prise change
  le nom de l'exercice : chaque prise garde son historique et sa progression, les séances passées
  ne changent pas. Les séries déjà saisies restent.
- Familles déclarées dans `tools/gen_exercices.py` (`FAMILLES`) → `EXV` dans `src/js3c.js`.

### 2026.10.13-2 — 175 exercices en Muscu, avec consignes en français et filtres (à essayer sur le téléphone)

- Piste 2 de `08-pistes-open-source.md`, après comparaison de deux sources sur 20 exercices et accord de
  l'utilisateur. **Texte et données seulement** : aucune image ni GIF des sources.
- **115 exercices en plus** (60 → 175), choisis parmi free-exercise-db (domaine public), noms écrits en
  français ; nouveau groupe **Avant-bras**. Les nouveaux n'ont pas d'illustration : initiale à la place,
  pas de schéma (aucun lien cassé).
- **Fiche d'exercice** : « Comment faire » (consignes pas à pas en français), « Équipement », muscles.
  Consignes : celles d'exercises-dataset (MIT) corrigées (« câble » → « poulie », « machine à traîneau » →
  « presse », prises fausses), ou écrites pour Forme quand la source n'avait pas l'exercice ou se trompait
  (28, dont face pull, hip thrust, gainage, curl marteau, presse).
- **Ajouter un exercice** : deux menus « Tous les muscles » / « Tout équipement », combinables avec la
  recherche ; la recherche ignore désormais les accents (« developpe »).
- Muscles corrigés : soulevé de terre (+ ischio-jambiers), curl marteau (+ avant-bras), leg curl
  (+ mollets), pompes (+ abdominaux). Les schémas `img2/` et l'illustration en rouge restent ceux d'avant.
- Nouveaux : `tools/gen_exercices.py`, `src/js3c.js` (104 ko), `tests/t13.py`. Retiré : une ancienne
  version inutilisée de la fiche dans `js3.js` (elle pointait vers un dossier `img/` inexistant).

### 2026.10.13-1 — 3 203 aliments de la table Ciqual dans « Chercher » (à essayer sur le téléphone)

- Piste 1 de `08-pistes-open-source.md`. La recherche du Repas trouve maintenant aussi les aliments de la
  table Ciqual 2025 de l'Anses (Licence Ouverte Etalab 2.0) : maquereau, abats, fromages, plats…
- Les 321 aliments familiers (noms simples, unités usuelles) passent devant ; les lignes Ciqual portent la
  mention « Ciqual » et leur fiche « Source : Anses, Table Ciqual 2025 ». Quantité en grammes (ml pour
  les boissons).
- Les puces de section ne listent toujours que les aliments familiers, avec « + N aliments de la table
  Ciqual dans cette section : tape un mot pour les trouver ».
- Nouveaux : `tools/gen_ciqual.py`, `src/js2g.js` (256 ko), `tests/t12.py`. Application : 392 → 655 ko
  avant compression.

### 2026.10.08-16 — Lune et nuages plus détaillés (à essayer sur le téléphone)

- Lune : cratères ombrés (ombre intérieure, rebord éclairé, trait d'encre, piton central), un cratère à
  rayons clairs, mers pointillées, cupules, hachures croisées dans l'ombre, liseré lumineux en haut à gauche.
- Nuages : deux plans (lobes du fond plus sombres), trois arcs par lobe et un reflet, bande rayée et
  perlée, grande et petite volute, traînées effilées, halo rose-violet, éclats autour. Plus grands.
- Flou derrière les cartes réduit (5 px, 4 px pour le niveau) pour laisser deviner les détails.
- Lune tracée en coordonnées entières et traits regroupés : décor ~100 ko (avant compression).

### 2026.10.08-15 — Ambiance Lune par défaut (à essayer sur le téléphone)

- Demandé : quelque chose dans l'esprit de son fond d'écran, « sombre assez éclairé avec des notes de violet ».
  On reprend l'atmosphère seulement (nuit étoilée, lune, nuages japonais, violet) : ni le personnage ni
  l'illustration, qui ne sont pas à nous.
- Nouvelle ambiance **Lune**, par défaut : ciel violet nuit éclairé par une grande lune lavande dessinée au
  trait d'encre (en haut à droite), nuages en volutes, étoiles qui scintillent. Cartes en verre violet.
  Le niveau s'affiche dans une petite lune ; les titres de section ont une étoile.
- Réglages → Ambiance : **Lune**, **Sakura**, **Néon** (l'ancienne « Nuit »). Valeurs de `S.settings.theme` :
  `lune` (ou vide), `sakura`, `nuit` ; `data-theme` sur `<html>` : `lune`, `light`, `dark`.
- Décor : `tools/gen_decor.py` assemble `gen_sakura.py` et `gen_lune.py` dans `src/p1.html`.
- Manifeste et `theme-color` : #16112E.

### 2026.10.08-14 — Ambiance Sakura (claire), Nuit en option (à essayer sur le téléphone)

- Nouvelle ambiance par défaut, claire : ciel pâle, branches de cerisier en fleurs, mont Fuji estompé et
  quelques pétales qui tombent en fond (`.deco`, dessin original généré par `tools/gen_sakura.py`, aucune
  image tierce). Cartes et barre d'onglets translucides ; l'en-tête devient dépoli quand on fait défiler.
- Police des titres et chiffres : Zen Maru Gothic (Google Fonts, comme Figtree).
- Le niveau s'affiche dans une fleur de cerisier ; les titres de section ont une petite fleur.
- L'ambiance sombre de la -13 reste disponible : Réglages → Ambiance → « Nuit · sombre »
  (`S.settings.theme = 'nuit'`, appliquée par `applyTheme()` dans `js1.js` via `data-theme="dark"`).
- Couleurs du manifeste et `theme-color` : #FFF8F8.

### 2026.10.08-13 — Look « jeu vidéo » (à essayer sur le téléphone)

- Thème sombre par défaut (le clair reste disponible via `data-theme="light"`), couleurs néon par onglet, polices Baloo 2 + Figtree.
- Boutons en relief, cartes à bord marqué, barres d'XP lumineuses, lueur sur les anneaux, barre d'onglets vitrée.
- Nouveau bandeau de niveau en haut de chaque onglet (`hudHtml` dans `js2.js`) : un niveau par palier de poids franchi, barre = avancement vers le palier suivant.
- Couleurs du manifeste et de `theme-color` alignées sur le fond sombre.
- Suite prévue : série de jours (streak), résumé de la semaine, coach « Maître » (personnage original).

### 2026.10.08-12 — Pas de doublon, aliments de base rangés

- Bibliothèque du Scan : un même produit scanné sous deux marques, avec les mêmes
  apports énergétiques, n'apparaît qu'une fois (« ×2 »). Le rangement et la
  suppression s'appliquent aux deux fiches. Les apports différents restent séparés.
- Les aliments de base du Repas sont rangés par **section et sous-section**, comme
  les produits scannés : puces VPO, Laitiers, Fruits & légumes, Féculents, Sucré,
  Huiles & sauces, Boissons, Plats, Apéritif, Sport ; chaque section liste ses
  aliments par sous-section.
- Nouvelles sous-sections : Sucre & sirops, Boissons protéinées ; « Pâtes, riz,
  semoule & farine » et « Café, thé & boissons chaudes » renommées.
- Meilleur classement automatique (blanc d'œuf, semoule, thon à l'huile, pain à
  burger, crêpes, sirop d'érable…), vérifié sur les 321 aliments.
- Nouveau test : `tests/t11.py`.

---

### 2026.10.08-11 — Bibliothèque des produits scannés

- Nouveau sous-onglet **Bibliothèque** dans Scan : tous les produits scannés,
  rangés en **11 sections** et leurs sous-sections. Exemple : *Viandes, poissons,
  œufs* → Viandes, Charcuteries, Poissons & fruits de mer, Œufs. Autres sections :
  produits laitiers, fruits & légumes, féculents & céréales, produits sucrés,
  huiles-sauces-condiments, boissons, plats préparés, apéritif & en-cas, sport &
  compléments, autres.
- Le rangement est automatique (nom du produit et catégorie Open Food Facts). Un
  produit mal rangé se corrige dans sa fiche (liste « Rangé dans »).
- Recherche dans la bibliothèque, « Tout ouvrir / Tout fermer », compteurs par
  section, suppression d'un produit.
- L'onglet Scanner n'affiche plus que les 5 derniers produits, avec un bouton
  vers la bibliothèque.
- Les feuilles du Scan sont vertes.
- Nouveau test : `tests/t10.py`.

---

### 2026.10.08-10 — Plus d'aliments et plus de recettes

- Aliments de base : de 163 à **321**. Nouvelle catégorie **Plats & en-cas**
  (pizza, burger, frites, croissant, sushi, quiche, desserts…), plus de viandes,
  poissons, fromages, légumes, fruits secs, graines, boissons et poudres de protéines.
- Recettes : de 35 à **74** (8 petits-déjeuners, 7 collations, 24 déjeuners/dîners
  de plus), toujours simples et protéinées (15 g de protéines minimum chacune).
- Nouveaux tests : `tests/t8.py` attend 74 recettes dont 21 collations.

---

### 2026.10.08-9 — Chercher un aliment

- Nouvel onglet **Chercher** dans « Ajouter » du Repas (ouvert par défaut) : une
  barre de recherche dans 163 aliments de base sans code-barres (œufs, laitages,
  viandes, poissons, féculents, légumes, fruits, gras, boissons).
- Les courants s'affichent d'abord ; des puces par catégorie ; la recherche
  ignore accents, majuscules et pluriel.
- Quantité en grammes (ou ml) ou en unité usuelle (œuf, tranche, càs, portion…),
  puces rapides, calories et macros calculées en direct.
- « Garder dans mes favoris » en un appui.
- La feuille « Ajouter » est maintenant orange comme le Repas.
- Valeurs moyennes indicatives, rédigées pour l'application.
- Nouveau test : `tests/t9.py`.

---

### 2026.10.08-8 — Recettes

- L'onglet Repas a trois sous-onglets : **Journal**, **Recettes**, **Déjà faites**.
- 35 recettes simples et protéinées (petit-déjeuner, déjeuner/dîner, collations),
  avec temps, ingrédients, étapes, calories et macros par portion.
- Classement selon ce qu'il reste dans la journée affichée : une recette qui
  tient dans les calories, glucides et lipides restants passe devant, celle qui
  couvre le mieux les protéines aussi. Sans filtre, on vise le prochain repas
  (selon l'heure et ce qui est déjà saisi).
- Filtres : repas, rapide (15 min max), à préparer à l'avance, végétarien.
- Fiche : portions ½ / 1 / 1,5 / 2 (quantités et macros recalculées), « Ajouter
  au journal » dans le repas choisi, « Je l'ai préparée », note personnelle.
- « Déjà faites » : les recettes préparées, la plus récente d'abord, avec date et
  note. Ajouter une recette au journal la marque aussi comme préparée.
- Ses propres recettes : créer, modifier, supprimer.
- Nouvelle tranche de données `recipes` (synchronisée, incluse dans l'export).
- Les feuilles de recettes sont orange comme l'onglet Repas.

---

### 2026.10.08-7 — Muscles en rouge

- Les muscles travaillés apparaissent en rouge directement sur l'illustration du
  mouvement, dans les deux positions. Rouge vif pour les principaux, rose pour
  les secondaires.
- Bouton « Image simple » pour retirer la couleur.
- Quatre illustrations mal recadrées corrigées (tête coupée sur les tractions et
  les shrugs) : le recadrage ne peut plus rogner la silhouette, il comble en noir.

### 2026.10.08-6 — Nouvelles illustrations

- Les photos de salle sont remplacées par des illustrations 3D sur fond noir,
  même style pour tous les exercices, recadrées sur le personnage.
- Les anciennes photos sont retirées du projet : leur base se disait « domaine
  public » mais plusieurs projets signalent que l'origine réelle n'est pas
  vérifiée.
- La barre de repos disparaît immédiatement au changement d'onglet.

### 2026.10.08-5 — Routines

- Création et modification de routines à l'avance : nom, exercices, ordre, nombre
  de séries, charges et répétitions prévues.
- Les valeurs prévues pré-remplissent la séance au démarrage.
- Duplication d'une routine.
- Le mot « modèle » devient « routine » partout.

### 2026.10.08-4 — Mouvement animé, minuteur, partage des pas

- Fiche d'exercice : grande image qui alterne départ et arrivée, bouton Pause.
  Le schéma anatomique passe en dessous, en petit.
- Les vignettes redeviennent des images du mouvement.
- Minuteur de repos transformé en barre fixe en bas de l'écran : démarrage
  manuel, choix de durée parmi huit valeurs, −15 s, +15 s, Passer, jauge,
  vibration.
- L'application s'inscrit au menu Partager d'Android : partager depuis
  l'application de podomètre remplit les pas et les calories.
- Correction : `history` était masqué par une fonction du même nom, l'adresse
  n'était pas nettoyée après un partage.

### 2026.10.08-2 — Carte Journée

- Nouvelle carte dans Poids : pas, calories dépensées, calories mangées, balance,
  barre vers l'objectif de pas, sept derniers jours en bâtons.
- Objectif de pas réglable.
- Reprise des pesées de l'ancienne application (carte d'import, retirée du code le 13 octobre 2026).
- Le cercle affiche « Départ … kg · … kg parcourus sur … ».

### 2026.10.08-1 — Version installable

- Première version publiée sur GitHub Pages, installable sur l'écran d'accueil.
- Scan en direct par la caméra.
- Recherche automatique des produits sur Open Food Facts.
- Fonctionnement hors ligne par service worker.
- Quatre fonctions restent propres à la version Claude : décrire un repas en
  texte, lire une étiquette en photo, lire les chiffres d'un code-barres, et la
  synchronisation sur le compte.

---

## Avant la version installable, dans Claude seulement

**Version 3** — chaque palier marqué et étiqueté sur le cercle ; macros calculées
depuis le poids ; icônes de repas ; schémas musculaires par exercice.

**Version 2** — cercle de progression par paliers ; lecture d'un code-barres sur
photo avec mémoire des produits ; images d'exercices.

**Version 1** — les quatre onglets : pesées et courbe, journal alimentaire,
séances de musculation, analyse de produit.
