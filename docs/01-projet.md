# 1. Le projet

## L'utilisateur

Une seule personne utilise cette application : son propriétaire. Il n'est pas
développeur et ne lit pas le code. Il décrit ce qu'il veut dans ses mots, essaie
le résultat sur son téléphone, et dit ce qui va ou ne va pas.

- Téléphone Android, navigateur Chrome (modèle : `perso.md`, non publié).
- Pays : France. Interface en français, tutoiement, virgule décimale, kilos et
  kilocalories.
- Il utilise aussi **Step Counter Pedometer** pour ses pas, application séparée.
- Objectif de poids par paliers de 2,5 kg (chiffres : `perso.md`, non publié).

## Pourquoi cette application

Il utilisait quatre applications : Better Weight, Yazio, Hevy et Yuka. Il voulait
une seule application, privée, qui regroupe les quatre usages, avec trois
exigences formulées dès le départ : **efficace, assez jolie, très ergonomique**.

« Privée » est à prendre au sens fort : ses pesées et son alimentation ne doivent
pas partir sur un serveur. D'où le choix d'une application web installée qui
garde tout dans le navigateur du téléphone.

## Ce qui est en place

**Poids**
- Saisie d'une pesée, à la date du jour ou à une date passée.
- Cercle de progression : un arc par palier de 2,5 kg, chaque palier marqué d'un
  point et étiqueté, repère de position actuelle, compteur « x / y paliers ».
- Courbe d'évolution sur 14, 30, 90 jours ou tout, avec moyenne lissée sur
  7 jours et ligne d'objectif.
- Statistiques : moyenne 7 jours, tendance par semaine, reste à perdre ; dessous, « Plus de
  détails » (fermé par défaut) : plus bas et plus haut avec leur date, moyenne 30 jours,
  variations sur 7, 30 et 90 jours (vert vers l'objectif, orange sinon), IMC si la taille est
  renseignée, dépense estimée (indicative) d'après les repas notés et la pente du poids.
- Carte « Journée » : pas, calories dépensées, calories mangées, balance,
  barre vers l'objectif de pas, sept derniers jours en bâtons.
- Historique complet, modifiable : écart coloré selon l'objectif, séparateur par semaine
  (moyenne, variation), carte repliable par son titre.
- Réglages : taille (facultative, pour l'IMC) ; export et import des pesées en CSV.

**Repas**
- Journal par repas : petit-déjeuner, déjeuner, dîner, collations, chacun avec
  son icône.
- Anneau de calories et trois barres de macros.
- Objectifs de macros calculés depuis la dernière pesée : protéines et lipides
  en grammes par kilo (2 et 1 par défaut), glucides en complément des calories.
  Débrayable pour saisir des grammes fixes.
- Cinq façons d'ajouter : **chercher** un aliment de base sans code-barres (œuf,
  riz, poulet… 321 aliments, avec unités usuelles), décrire en texte (Claude
  uniquement), scanner un code-barres, reprendre un favori ou un aliment récent,
  saisir à la main. « Chercher » est l'onglet ouvert par défaut.
- **Recettes** : 74 recettes simples et protéinées, classées selon les calories,
  protéines, glucides et lipides restants du jour. Filtres (repas, rapide, à
  l'avance, végétarien), portions, ajout au journal, note, recettes personnelles.
- **Déjà faites** : les recettes préparées, avec la date et la note.
- Ajouts rapides (2026.10.14-4) : calories rapides dans « Manuel » (+100, +200…, nom facultatif),
  copier un repas ou une journée des 28 derniers jours, **repas types** (dans Favoris), « Souvent à ce
  repas » (Chercher et Favoris).
- Fiabilité : la fiche d'un aliment montre sa source ; ses valeurs peuvent être corrigées (pour les
  ajouts futurs, « Rétablir l'original ») ; bascule cru / cuit quand l'aliment jumeau existe.
- Recettes perso : portions et « Calculer les valeurs » depuis les ingrédients. **Mon frigo** : cases
  de ce qu'il a, « Avec mon frigo » classe les recettes selon ce qui manque.
- **Semaine** : recettes posées sur 7 jours, ✓ pour les noter au journal, **liste de courses**
  additionnée et rangée par rayon, « Ranger dans mon frigo ».
- **Bilan** : 7 derniers jours (barres, moyennes), **série** de jours notés qui pardonne un oubli,
  calendrier du mois coloré selon l'objectif ; la série s'affiche aussi sous le cercle du Journal.
- Lecture d'une étiquette en photo, **hors ligne**, sur le téléphone (Tesseract.js) : les chiffres
  lus sont toujours montrés pour vérification avant d'être enregistrés.

**Muscu**
- Bibliothèque de 60 exercices en 7 groupes, plus les exercices créés à la volée.
- Séance en cours : séries, charge, répétitions, rappel de la dernière
  performance, chronomètre de séance.
- Minuteur de repos en barre fixe en bas de l'écran, lancé à la main ou
  automatiquement après une série validée, −15 s, +15 s, Passer, vibration.
- Routines préparées à l'avance : exercices, nombre de séries, charges et
  répétitions prévues qui pré-remplissent la séance.
- Fiche d'exercice : illustration animée du mouvement avec les muscles en rouge,
  bascule vers l'image simple, schéma anatomique, listes des muscles.
- Progression par exercice : charge maximale, 1RM estimé (Epley), volume.

**Scan**
- Lecture d'un code-barres par photo, et en direct par la caméra sur le téléphone.
- Recherche automatique du produit sur Open Food Facts (téléphone uniquement).
- Sinon : lecture de l'étiquette en photo par Claude, ou saisie manuelle.
- Note sur 100 à partir d'un Nutri-Score recalculé, moins une pénalité d'additifs.
- Mémoire des produits déjà scannés, ajout direct au journal.

**Réglages**
- Calories visées, grammes par kilo, objectifs fixes, objectif de pas.
- Objectif de poids, poids de départ, pas de palier, durée de repos par défaut.
- Export et import des données en JSON.
- Numéro de version, bouton de mise à jour, crédits et licences.

## Ce qui n'existe pas, et pourquoi

| Demande | État | Raison |
|---|---|---|
| Récupérer les pas automatiquement depuis Step Counter Pedometer | Non | Android réserve Health Connect aux applications natives. Une page web n'y a pas accès. Contourné par le menu Partager d'Android et la saisie manuelle. |
| Illustrations anatomiques du style qu'il avait envoyé | Remplacé | Les images fournies venaient d'une marque tierce. Remplacées par une collection CC0 colorée automatiquement. |
| Application Android native | Non | Seule voie vers les pas en temps réel, mais il faudrait un APK, l'installation de sources inconnues, et on perdrait la mise à jour automatique. Écarté d'un commun accord. |
| Notifications, rappels | Non demandé | — |
| Plusieurs utilisateurs | Hors sujet | Application strictement personnelle. |

## Historique des demandes

1. Regrouper quatre applications en une, quatre onglets, efficace, jolie, ergonomique.
2. Cercle de progression avec paliers de 2,5 kg. Scan de
   codes-barres. Images pour les exercices.
3. Marquer chaque palier sur le cercle. Icônes de repas. Calcul des macros selon
   le poids. Changer les images d'exercices.
4. Sortir l'application de Claude pour l'installer sur le téléphone.
5. Pas et calories dépensées dans l'onglet Poids, reprise des anciennes pesées.
6. Images montrant le mouvement, minuteur de repos facile d'accès.
7. Routines remplissables à l'avance.
8. Muscles travaillés en rouge sur les illustrations.
9. Transposer le projet dans un dossier documenté.
10. Un sous-onglet de recettes dans Repas, selon les calories et macros restantes,
    avec les recettes déjà préparées.
11. Ajouter au Repas des aliments de base sans code-barres (comme les œufs), en
    les cherchant avec une barre de recherche : onglet « Chercher » (2026.10.08-9),
    puis plus d'aliments et de recettes (2026.10.08-10).
12. Une bibliothèque de tous les aliments scannés, triés en sections et
    sous-sections (ex. Viandes, poissons, œufs → viandes / poissons / œufs), sur le
    même principe pour les autres aliments (2026.10.08-11).
13. Pas de doublon dans la bibliothèque (même produit de deux marques, mêmes apports)
    et les aliments de base du Repas rangés selon les mêmes sections et sous-sections
    (2026.10.08-12).
14. Travailler le graphisme et ce qui motive à utiliser l'application : style jeu vidéo à niveaux, série de
    jours, résumé de la semaine, un coach chibi « Maître » (2026.10.08-13).
15. Une ambiance claire avec des branches de cerisier en fond (2026.10.08-14).
16. Une ambiance dans l'esprit de son fond d'écran : sombre mais éclairée, notes de violet (2026.10.08-15),
    puis plus de détails dans la lune et les nuages (2026.10.08-16).
