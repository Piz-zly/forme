# 6. Journal des versions

Les versions suivent `AAAA.MM.JJ-n`, `n` étant le numéro dans la journée. La
version courante est déclarée dans `src/js1.js` et affichée en bas des Réglages.

---

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
- Reprise des 15 pesées de l'ancienne application, du 21 septembre au 7 octobre.
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
