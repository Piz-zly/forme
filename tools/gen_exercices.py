#!/usr/bin/env python3
"""Genere src/js3c.js : consignes, equipement, muscles des exercices de Muscu, et les exercices en plus.

    python3 tools/gen_exercices.py <exercises.json de A> <exercises.json de B>

Deux sources, TEXTE ET DONNEES SEULEMENT (aucune image, aucun GIF) :
  A  github.com/hasaneyldrm/exercises-dataset, data/exercises.json - licence MIT pour le texte
     et les donnees. Ses images/ et videos/ sont (c) Gym visual, NON libres : jamais utilisees.
     On prend : les consignes en francais (instruction_steps.fr) et l'equipement.
  B  github.com/yuhonas/free-exercise-db, dist/exercises.json - Unlicense (domaine public).
     C'est deja la source des 60 exercices de l'appli (identifiants de EXI dans src/js3.js).
     On prend : la liste des exercices en plus et les muscles principaux et secondaires.
Les deux fichiers se telechargent a part et ne vont PAS dans le depot.

Choix (voir docs/08-pistes-open-source.md) :
  - muscles : ceux de l'appli et de B, avec quelques corrections (MUSCLES ci-dessous) ;
  - consignes : celles de A en francais, corrigees (FIX), ou ecrites ici (OWN) quand A n'a pas
    l'exercice ou se trompe ;
  - equipement : celui de A s'il y a correspondance, sinon celui de B ;
  - noms : en francais, ecrits ici. Ceux que l'on dit en anglais en salle restent en anglais.

Sortie : const EXD={nom:{eq, m, s, st, g?}} ; g (groupe de la liste) seulement pour les
exercices en plus. src/js3.js fusionne EXD dans EXI et LIB.
"""
import json, os, re, sys

# ------------------------------------------------------------------ vocabulaire
MUS = {'chest': 'Pectoraux', 'shoulders': 'Épaules', 'triceps': 'Triceps', 'biceps': 'Biceps',
       'lats': 'Grand dorsal', 'middle back': 'Milieu du dos', 'lower back': 'Lombaires',
       'forearms': 'Avant-bras', 'calves': 'Mollets', 'glutes': 'Fessiers', 'hamstrings': 'Ischio-jambiers',
       'quadriceps': 'Quadriceps', 'traps': 'Trapèzes', 'abdominals': 'Abdominaux',
       'adductors': 'Adducteurs', 'abductors': 'Abducteurs', 'neck': 'Cou'}
EQ_A = {'body weight': 'Poids du corps', 'weighted': 'Poids du corps', 'dumbbell': 'Haltères',
        'cable': 'Poulie', 'barbell': 'Barre', 'olympic barbell': 'Barre', 'trap bar': 'Barre',
        'ez barbell': 'Barre EZ', 'leverage machine': 'Machine', 'sled machine': 'Machine',
        'assisted': 'Machine', 'smith machine': 'Machine guidée', 'kettlebell': 'Kettlebell',
        'band': 'Élastique', 'resistance band': 'Élastique', 'stability ball': 'Ballon',
        'medicine ball': 'Ballon', 'bosu ball': 'Ballon', 'wheel roller': 'Roulette'}
EQ_B = {'barbell': 'Barre', 'dumbbell': 'Haltères', 'cable': 'Poulie', 'machine': 'Machine',
        'body only': 'Poids du corps', 'kettlebells': 'Kettlebell', 'bands': 'Élastique',
        'e-z curl bar': 'Barre EZ', 'medicine ball': 'Ballon', 'exercise ball': 'Ballon'}
EQUIP = ['Barre', 'Barre EZ', 'Haltères', 'Kettlebell', 'Poulie', 'Machine', 'Machine guidée',
         'Poids du corps', 'Élastique', 'Ballon', 'Roulette', 'Banc']
GROUPS = ['Pectoraux', 'Dos', 'Épaules', 'Biceps', 'Triceps', 'Jambes', 'Abdos', 'Avant-bras']

# ------------------------------------------------------------------ les 60 exercices de l'appli
# nom de l'appli : id dans A (None : pas d'equivalent sur, consignes dans OWN)
OLD = {
 'Développé couché': '0025', 'Développé incliné barre': '0047', 'Développé incliné haltères': '0314',
 'Développé couché haltères': '0289', 'Développé décliné': '0033', 'Développé couché machine': '0577',
 'Écarté haltères': '0308', 'Écarté poulie': '0227', 'Pec deck': '0596', 'Pompes': '0662', 'Dips': '0251',
 'Tractions': '0652', 'Tractions supination': '1326', 'Tirage vertical': '2330', 'Tirage vertical prise serrée': None,
 'Rowing barre': '0027', 'Rowing haltère': '0292', 'Tirage horizontal': '0861', 'Rowing T-bar': None,
 'Soulevé de terre': '0032', 'Pull-over poulie': '0238', 'Shrugs haltères': '0406',
 'Développé militaire': '1457', 'Développé haltères assis': '0405', 'Arnold press': '2137',
 'Élévations latérales': '0334', 'Élévations frontales': '0310', 'Oiseau': '0383', 'Face pull': None,
 'Curl barre': '0031', 'Curl haltères': '0294', 'Curl marteau': None, 'Curl pupitre': '0070',
 'Curl incliné': '0318', 'Curl poulie': '0868',
 'Extension poulie': '0201', 'Extension poulie corde': '0200', 'Barre au front': '0060', 'Dips banc': '0129',
 'Extension nuque haltère': '0430', 'Extension verticale poulie': '0194', 'Développé serré': '0030',
 'Squat': '0043', 'Squat avant': '0042', 'Goblet squat': '1760', 'Hack squat': '0046', 'Presse à cuisses': None,
 'Fentes': '0336', 'Fentes marchées': '1460', 'Leg extension': '0585', 'Leg curl': '0586', 'Leg curl assis': '0599',
 'Soulevé de terre roumain': '0085', 'Hip thrust': None, 'Mollets debout': '0605', 'Mollets assis': '0594',
 'Crunch': '0274', 'Relevé de jambes': '0472', 'Crunch poulie': '0175', 'Gainage': None,
}

# ------------------------------------------------------------------ les exercices en plus
# groupe | nom | id B | id A (vide : consignes dans OWN)
NEW = '''
Pectoraux|Développé couché prise large|Wide-Grip_Barbell_Bench_Press|0122
Pectoraux|Développé couché Smith|Smith_Machine_Bench_Press|0748
Pectoraux|Développé incliné Smith|Smith_Machine_Incline_Bench_Press|0757
Pectoraux|Développé décliné haltères|Decline_Dumbbell_Bench_Press|0301
Pectoraux|Développé couché haltères prise neutre|Dumbbell_Bench_Press_with_Neutral_Grip|0352
Pectoraux|Développé incliné machine|Leverage_Incline_Chest_Press|1299
Pectoraux|Écarté incliné haltères|Incline_Dumbbell_Flyes|0319
Pectoraux|Écarté décliné haltères|Decline_Dumbbell_Flyes|0302
Pectoraux|Écarté poulie basse|Low_Cable_Crossover|0179
Pectoraux|Écarté incliné poulie|Incline_Cable_Flye|0171
Pectoraux|Pull-over haltère|Straight-Arm_Dumbbell_Pullover|0433
Pectoraux|Pompes pieds surélevés|Push-Ups_With_Feet_Elevated|0279
Pectoraux|Pompes inclinées|Incline_Push-Up|0493
Pectoraux|Pompes prise large|Push-Up_Wide|1311
Dos|Rowing haltères deux bras|Bent_Over_Two-Dumbbell_Row|0293
Dos|Rowing barre prise inversée|Reverse_Grip_Bent-Over_Rows|0118
Dos|Rowing sur banc incliné|Dumbbell_Incline_Row|0327
Dos|Rowing poulie un bras|Seated_One-arm_Cable_Pulley_Rows|0214
Dos|Rowing machine|Leverage_Iso_Row|1350
Dos|Rowing Smith|Smith_Machine_Bent_Over_Row|1359
Dos|Rowing kettlebell un bras|One-Arm_Kettlebell_Row|0541
Dos|Tirage vertical prise inversée|Underhand_Cable_Pulldowns|0245
Dos|Tirage vertical prise neutre|V-Bar_Pulldown|2616
Dos|Tirage vertical un bras|One_Arm_Lat_Pulldown|3563
Dos|Pull-over poulie corde|Rope_Straight-Arm_Pulldown|0237
Dos|Shrugs barre|Barbell_Shrug|0095
Dos|Shrugs machine|Leverage_Shrug|0604
Dos|Soulevé de terre sumo|Sumo_Deadlift|0117
Dos|Rack pull|Rack_Pulls|0074
Dos|Soulevé de terre jambes tendues|Stiff-Legged_Barbell_Deadlift|
Dos|Good morning|Good_Morning|0044
Dos|Extensions lombaires|Hyperextensions_Back_Extensions|0488
Épaules|Développé militaire assis|Seated_Barbell_Military_Press|0091
Épaules|Développé épaules machine|Machine_Shoulder_Military_Press|0603
Épaules|Développé épaules Smith|Smith_Machine_Overhead_Shoulder_Press|0766
Épaules|Développé haltères debout|Standing_Dumbbell_Press|0426
Épaules|Élévations latérales assis|Seated_Side_Lateral_Raise|0396
Épaules|Élévation latérale poulie|Standing_Low-Pulley_Deltoid_Raise|0178
Épaules|Élévations frontales poulie|Front_Cable_Raise|0162
Épaules|Oiseau machine|Reverse_Machine_Flyes|0602
Épaules|Oiseau poulie|Cable_Rear_Delt_Fly|
Épaules|Oiseau assis|Seated_Bent-Over_Rear_Delt_Raise|
Épaules|Rowing menton barre|Upright_Barbell_Row|0120
Épaules|Rowing menton haltères|Standing_Dumbbell_Upright_Row|0437
Épaules|Rowing menton poulie|Upright_Cable_Row|0246
Épaules|Rotation externe poulie|External_Rotation_with_Cable|0235
Épaules|Écartement élastique|Band_Pull_Apart|
Biceps|Curl barre EZ|EZ-Bar_Curl|0447
Biceps|Curl concentré|Concentration_Curls|0297
Biceps|Curl haltères alterné|Dumbbell_Alternate_Bicep_Curl|0285
Biceps|Curl haltères assis|Seated_Dumbbell_Curl|0391
Biceps|Curl marteau poulie corde|Cable_Hammer_Curls_-_Rope_Attachment|0165
Biceps|Curl marteau incliné|Incline_Hammer_Curls|0320
Biceps|Curl pupitre haltère|One_Arm_Dumbbell_Preacher_Curl|0372
Biceps|Curl pupitre machine|Machine_Preacher_Curls|0592
Biceps|Curl araignée|Spider_Curl|0454
Biceps|Curl inversé barre|Reverse_Barbell_Curl|0080
Biceps|Curl Zottman|Zottman_Curl|0439
Biceps|Curl poulie haute|High_Cable_Curls|1636
Biceps|Curl machine|Machine_Bicep_Curl|0575
Triceps|Kickback haltère|Tricep_Dumbbell_Kickback|0333
Triceps|Extension poulie prise inversée|Reverse_Grip_Triceps_Pushdown|0207
Triceps|Extension poulie barre en V|Triceps_Pushdown_-_V-Bar_Attachment|0241
Triceps|Extension poulie un bras|Cable_One_Arm_Tricep_Extension|
Triceps|Extension nuque barre|Standing_Overhead_Barbell_Triceps_Extension|0109
Triceps|Extension nuque un bras|Standing_One-Arm_Dumbbell_Triceps_Extension|0423
Triceps|Extension couché haltères|Lying_Dumbbell_Tricep_Extension|0351
Triceps|Extension triceps machine|Machine_Triceps_Extension|0607
Triceps|Dips triceps|Dips_-_Triceps_Version|
Triceps|Dips machine|Dip_Machine|1451
Triceps|Pompes serrées|Push-Ups_-_Close_Triceps_Position|0259
Triceps|Développé serré haltères|Close-Grip_Dumbbell_Press|
Triceps|Développé au sol|Floor_Press|
Jambes|Squat Smith|Smith_Machine_Squat|0770
Jambes|Squat haltères|Dumbbell_Squat|0413
Jambes|Squat poids du corps|Bodyweight_Squat|
Jambes|Box squat|Box_Squat|
Jambes|Squat sumo haltère|Plie_Dumbbell_Squat|
Jambes|Squat bulgare|Split_Squat_with_Dumbbells|0410
Jambes|Hack squat machine|Hack_Squat|0743
Jambes|Presse pieds serrés|Narrow_Stance_Leg_Press|
Jambes|Fentes barre|Barbell_Lunge|0054
Jambes|Fentes arrière|Dumbbell_Rear_Lunge|0381
Jambes|Montées sur banc|Dumbbell_Step_Ups|0431
Jambes|Leg extension unilatéral|Single-Leg_Leg_Extension|
Jambes|Leg curl debout|Standing_Leg_Curl|
Jambes|Soulevé de terre roumain haltères|Stiff-Legged_Dumbbell_Deadlift|1459
Jambes|Pont fessier barre|Barbell_Glute_Bridge|1409
Jambes|Pont fessier|Butt_Lift_Bridge|3013
Jambes|Pont fessier une jambe|Single_Leg_Glute_Bridge|3645
Jambes|Kickback fessier poulie|One-Legged_Cable_Kickback|
Jambes|Pull through poulie|Pull_Through|0196
Jambes|Adducteurs machine|Thigh_Adductor|0598
Jambes|Abducteurs machine|Thigh_Abductor|0597
Jambes|Mollets à la presse|Calf_Press_On_The_Leg_Press_Machine|
Jambes|Mollets haltères|Standing_Dumbbell_Calf_Raise|0417
Jambes|Mollets Smith|Smith_Machine_Calf_Raise|0773
Abdos|Crunch inversé|Reverse_Crunch|0872
Abdos|Crunch oblique|Oblique_Crunches_-_On_The_Floor|0635
Abdos|Crunch machine|Ab_Crunch_Machine|
Abdos|Crunch décliné|Decline_Crunch|0277
Abdos|Crunch vélo|Air_Bike|0003
Abdos|Relevé de jambes allongé|Flat_Bench_Lying_Leg_Raise|0620
Abdos|Relevé de genoux chaise romaine|Knee_Hip_Raise_On_Parallel_Bars|
Abdos|Sit-up|Sit-Up|0735
Abdos|Russian twist|Russian_Twist|0687
Abdos|Gainage latéral|Side_Bridge|0705
Abdos|Roulette abdominale|Barbell_Ab_Rollout_-_On_Knees|
Abdos|Bûcheron poulie|Standing_Cable_Wood_Chop|
Abdos|Pallof press|Pallof_Press|
Abdos|Dead bug|Dead_Bug|0276
Abdos|Mountain climber|Mountain_Climbers|0630
Abdos|Flexion latérale haltère|Dumbbell_Side_Bend|0407
Avant-bras|Curl poignets barre|Palms-Up_Barbell_Wrist_Curl_Over_A_Bench|1412
Avant-bras|Curl poignets inversé|Palms-Down_Wrist_Curl_Over_A_Bench|1411
'''
NEW = [l.split('|') for l in NEW.strip().splitlines()]

# ------------------------------------------------------------------ corrections
# Muscles : remplacent ceux de B (et donc de l'appli). Decides avec l'utilisateur le 13/10/2026.
MUSCLES = {
 'Soulevé de terre': (['Lombaires'], ['Ischio-jambiers', 'Fessiers', 'Mollets', 'Avant-bras']),
 'Curl marteau': (['Biceps'], ['Avant-bras']),
 'Leg curl': (['Ischio-jambiers'], ['Mollets']),
 'Pompes': (['Pectoraux'], ['Épaules', 'Triceps', 'Abdominaux']),
 'Pallof press': (['Abdominaux'], []),
}
# Equipement impose (A et B ne disent pas ce qu'on voit en salle).
EQUIP_FIX = {'Extensions lombaires': 'Banc', 'Relevé de genoux chaise romaine': 'Poids du corps',
             'Roulette abdominale': 'Roulette', 'Barre au front': 'Barre EZ', 'Mountain climber': 'Poids du corps',
             'Dips': 'Poids du corps', 'Box squat': 'Barre', 'Rowing T-bar': 'Barre', 'Presse à cuisses': 'Machine',
             'Mollets à la presse': 'Machine', 'Crunch machine': 'Machine', 'Kickback fessier poulie': 'Poulie',
             'Extension poulie un bras': 'Poulie', 'Développé serré haltères': 'Haltères', 'Dips triceps': 'Poids du corps'}

# Francais de A : remplacements surs (l'ordre compte).
FIX = [
 (r"machine à traîneau", "presse"), (r"traîneau", "presse"),
 (r"plaque de pied|plateforme de pied", "plateau"), (r"\b(la|les|une) plateau\b", "le plateau"),
 (r"prise (en )?(pronation|supination),? (avec )?les paumes tournées l'une vers l'autre", "prise neutre, les paumes tournées l'une vers l'autre"),
 (r"machine à levier", "machine"), (r"Assieds-toi sur un banc à prêch(eur|er)", "Assieds-toi au pupitre"), (r"levier rembourré", "coussin"), (r"banc à prêch(eur|er)", "pupitre"),
 (r"(une|la) machine à câbles? (à|avec) (une )?poulie (haute|basse)", r"\1 poulie \4"),
 (r"machine à câbles?", "poulie"), (r"poulie à poulie", "poulie"),
 (r"\baux câbles\b", "aux poulies"), (r"\bdes câbles\b", "des poulies"), (r"\bles câbles\b", "les poulies"),
 (r"\bdu câble\b", "de la poulie"), (r"\bau câble\b", "à la poulie"), (r"\ble câble\b", "la poulie"),
 (r"\bun câble\b", "une poulie"), (r"\bcâbles\b", "poulies"), (r"\bcâble\b", "poulie"),
 (r"la poulie de la poulie", "la poulie"), (r"(poulies? (haute|basse)s?) d'une poulie", r"\1"),
 (r"(à (une|la) poulie (haute|basse)) sur une poulie", r"\1"), (r"\s+", " "),
]

# Consignes ecrites ici : A n'a pas l'exercice, ou se trompe (curl marteau : A fait tourner les paumes).
REP = "Répète le nombre de répétitions souhaité."
OWN = {
 'Face pull': ["Règle la poulie à hauteur du visage, ou un peu plus haut, et fixe la corde.",
   "Saisis la corde à deux mains, les paumes tournées l'une vers l'autre, et recule d'un pas pour mettre la poulie en tension.",
   "Tire la corde vers ton visage en écartant les mains, les coudes hauts, à hauteur des épaules.",
   "En fin de mouvement, serre les omoplates : tes mains arrivent de chaque côté de ta tête.",
   "Reviens lentement, bras tendus, sans laisser la charge t'emporter.", REP],
 'Hip thrust': ["Assieds-toi au sol, le haut du dos appuyé contre le bord d'un banc, une barre posée au pli des hanches (avec une mousse pour le confort).",
   "Pose les pieds à plat, écartés à la largeur des hanches, les genoux fléchis.",
   "Pousse dans tes talons et monte les hanches jusqu'à ce que ton buste et tes cuisses forment une ligne droite.",
   "En haut, serre fort les fessiers une seconde, sans creuser le bas du dos.",
   "Redescends lentement les hanches vers le sol.", REP],
 'Gainage': ["Mets-toi face au sol, en appui sur les avant-bras et la pointe des pieds, les coudes sous les épaules.",
   "Aligne la tête, le dos et les jambes : ni fesses en l'air, ni dos creusé.",
   "Serre les abdos et les fessiers, et respire calmement.",
   "Tiens la position le temps voulu, puis repose les genoux au sol."],
 'Tirage vertical prise serrée': ["Fixe une barre à la poulie haute et assieds-toi, les cuisses bloquées sous les coussins.",
   "Saisis la barre, les paumes vers l'avant, les mains plus serrées que la largeur des épaules.",
   "Penche légèrement le buste en arrière, la poitrine sortie.",
   "Tire la barre jusqu'en haut de ta poitrine en ramenant les coudes vers le bas et en serrant les omoplates.",
   "Remonte lentement jusqu'à avoir les bras tendus.", REP],
 'Curl marteau': ["Tiens-toi debout, un haltère dans chaque main, les bras le long du corps, les paumes tournées vers ton corps.",
   "Garde les coudes collés au buste et le haut des bras immobile.",
   "Expire et monte les haltères vers tes épaules sans tourner les poignets : les paumes restent face à face.",
   "Marque un temps en haut en contractant les biceps.",
   "Inspire et redescends lentement.", REP],
 'Soulevé de terre jambes tendues': ["Tiens-toi debout, les pieds écartés à la largeur des hanches, la barre tenue devant les cuisses, les mains à la largeur des épaules.",
   "Garde les jambes presque tendues : les genoux sont à peine fléchis et ne bougent plus.",
   "Penche le buste en avant en poussant les fesses vers l'arrière, le dos bien droit, et laisse descendre la barre le long des jambes.",
   "Descends jusqu'à sentir l'étirement à l'arrière des cuisses, sans arrondir le dos.",
   "Remonte en contractant les fessiers et l'arrière des cuisses.", REP],
 'Oiseau poulie': ["Règle les deux poulies à hauteur d'épaules et tiens-toi au milieu, face à la machine.",
   "Saisis la poignée de droite avec la main gauche et celle de gauche avec la main droite, les bras tendus devant toi.",
   "Écarte les bras vers l'arrière en arc de cercle, les coudes légèrement fléchis, jusqu'à les avoir en ligne avec tes épaules.",
   "Serre les omoplates une seconde.", "Reviens lentement à la position de départ.", REP],
 'Oiseau assis': ["Assieds-toi au bout d'un banc, un haltère dans chaque main, les pieds à plat.",
   "Penche le buste en avant jusqu'à presque toucher tes cuisses, le dos droit, les haltères sous les jambes, les paumes face à face.",
   "Les coudes légèrement fléchis, lève les bras sur les côtés jusqu'à ce qu'ils soient parallèles au sol.",
   "Serre les omoplates une seconde.", "Redescends lentement.", REP],
 'Écartement élastique': ["Debout, tiens un élastique devant toi à hauteur des épaules, les bras tendus, les mains écartées à la largeur des épaules.",
   "Écarte les bras sur les côtés en les gardant tendus, jusqu'à ce que l'élastique touche ta poitrine.",
   "Serre les omoplates une seconde.", "Reviens lentement à la position de départ.", REP],
 'Développé au sol': ["Allonge-toi sur le dos au sol, sous une barre posée dans le rack.",
   "Saisis la barre un peu plus large que les épaules et décroche-la, les bras tendus au-dessus de ta poitrine.",
   "Descends la barre jusqu'à ce que le haut de tes bras touche le sol.",
   "Marque une courte pause, puis pousse la barre vers le haut jusqu'à tendre les bras.",
   "Répète le nombre de répétitions souhaité, puis repose la barre dans le rack."],
 'Squat poids du corps': ["Tiens-toi debout, les pieds écartés à la largeur des épaules, les mains derrière la tête ou les bras tendus devant toi.",
   "Descends en pliant les genoux et en poussant les hanches vers l'arrière, comme pour t'asseoir.",
   "Garde le dos droit, la poitrine haute et les talons au sol.",
   "Descends jusqu'à avoir les cuisses parallèles au sol, puis remonte en poussant dans les talons.", REP],
 'Squat sumo haltère': ["Tiens-toi debout, les pieds bien plus écartés que les épaules, les pointes de pieds tournées vers l'extérieur.",
   "Tiens un haltère à deux mains par une extrémité, les bras tendus entre tes jambes.",
   "Descends en pliant les genoux, qui suivent la direction des pieds, en gardant le dos droit.",
   "Descends jusqu'à avoir les cuisses parallèles au sol, puis remonte en poussant dans les talons.", REP],
 'Presse pieds serrés': ["Assieds-toi à la presse, le dos bien plaqué contre le dossier.",
   "Place tes pieds au milieu du plateau, rapprochés (environ 15 cm d'écart).",
   "Retire les sécurités et tends les jambes sans bloquer les genoux.",
   "Descends lentement le plateau jusqu'à ce que tes genoux forment un angle droit.",
   "Pousse avec tout le pied pour remonter.", "Répète le nombre de répétitions souhaité, puis remets les sécurités."],
 'Leg extension unilatéral': ["Assieds-toi sur la machine, le dos contre le dossier, le coussin posé sur le bas de ta jambe, au-dessus de la cheville.",
   "Tiens les poignées et travaille une seule jambe ; l'autre reste détendue.",
   "Tends la jambe jusqu'en haut en contractant la cuisse.",
   "Marque un temps, puis redescends lentement.", "Fais toutes tes répétitions, puis change de jambe."],
 'Leg curl debout': ["Règle la machine : le coussin se place derrière ta cheville, juste au-dessus du talon.",
   "Tiens-toi debout face à la machine, les mains sur les poignées, la cuisse contre l'appui.",
   "Plie la jambe pour amener le talon vers tes fesses, sans bouger la cuisse.",
   "Marque un temps en haut, puis redescends lentement.", "Fais toutes tes répétitions, puis change de jambe."],
 'Relevé de genoux chaise romaine': ["Installe-toi sur la chaise romaine : les avant-bras sur les appuis, les mains sur les poignées, le dos contre le dossier, les jambes pendantes.",
   "Monte les genoux vers ta poitrine en enroulant légèrement le bassin.",
   "Marque un temps en haut en contractant les abdos.",
   "Redescends lentement les jambes, sans balancer.", REP],
 'Bûcheron poulie': ["Règle la poulie en position haute et fixe une poignée. Tiens-toi de profil, les pieds écartés à la largeur des épaules.",
   "Saisis la poignée à deux mains au-dessus de l'épaule la plus proche de la poulie, les bras tendus.",
   "Tire la poignée en diagonale vers le bas, jusqu'à la hanche opposée, en tournant le buste ; les bras restent tendus.",
   "Laisse pivoter le pied arrière pour accompagner la rotation.",
   "Reviens lentement en contrôlant la charge.", "Fais toutes tes répétitions, puis change de côté."],
 'Presse à cuisses': ["Assieds-toi à la presse, le dos et les fesses bien plaqués contre le dossier.",
   "Place tes pieds au milieu du plateau, écartés à la largeur des épaules.",
   "Tends les jambes pour décoller le plateau, puis retire les sécurités.",
   "Descends lentement le plateau jusqu'à ce que tes genoux forment un angle droit, sans décoller le bas du dos.",
   "Pousse avec tout le pied pour remonter, sans bloquer les genoux en haut.",
   "Répète le nombre de répétitions souhaité, puis remets les sécurités."],
 'Mollets à la presse': ["Assieds-toi à la presse et place la pointe des pieds en bas du plateau, les talons dans le vide.",
   "Tends les jambes, sans bloquer les genoux, et retire les sécurités.",
   "Pousse le plateau avec la pointe des pieds en tendant les chevilles le plus loin possible.",
   "Reviens lentement en laissant les talons descendre pour étirer les mollets.",
   "Répète le nombre de répétitions souhaité, puis remets les sécurités."],
 'Rowing T-bar': ["Bloque une extrémité de la barre dans un coin ou dans le support prévu, et charge l'autre extrémité.",
   "Place-toi au-dessus de la barre, un pied de chaque côté, et glisse une poignée en V sous la barre, près des disques.",
   "Fléchis les genoux et penche le buste en avant, le dos droit, les bras tendus.",
   "Tire la barre vers ta poitrine en serrant les omoplates, les coudes près du corps.",
   "Marque un temps, puis redescends lentement.", REP],
 'Dips triceps': ["Mets-toi en appui sur des barres parallèles, les bras tendus, le buste bien droit.",
   "Garde les coudes près du corps et le buste vertical : ce sont surtout les triceps qui travaillent.",
   "Descends en pliant les coudes jusqu'à ce que tes bras forment un angle droit.",
   "Pousse sur tes mains pour remonter jusqu'à tendre les bras.", REP],
 'Extension poulie un bras': ["Fixe une poignée simple à la poulie haute et tiens-toi face à la machine.",
   "Saisis la poignée d'une main, le coude collé au flanc, l'avant-bras à l'horizontale.",
   "Pousse la poignée vers le bas jusqu'à tendre complètement le bras, sans bouger le coude.",
   "Marque un temps, puis remonte lentement.", "Fais toutes tes répétitions, puis change de bras."],
 'Développé serré haltères': ["Allonge-toi sur un banc plat, un haltère dans chaque main, les bras tendus au-dessus de ta poitrine.",
   "Colle les haltères l'un contre l'autre, les paumes face à face.",
   "Descends les haltères vers le milieu de ta poitrine en gardant les coudes près du corps.",
   "Pousse pour remonter, les haltères toujours collés, jusqu'à tendre les bras.", REP],
 'Box squat': ["Place une box ou un banc derrière toi, et la barre sur le haut de ton dos, posée sur les trapèzes.",
   "Recule jusqu'à la box, les pieds un peu plus écartés que les épaules.",
   "Descends en poussant les hanches vers l'arrière jusqu'à t'asseoir brièvement sur la box, sans te relâcher.",
   "Remonte en poussant dans les talons, le dos droit.", REP],
 'Roulette abdominale': ["Mets-toi à genoux au sol, une roulette abdominale (ou une barre chargée de disques ronds) tenue à deux mains sous tes épaules.",
   "Gaine fort le ventre et serre les fessiers.",
   "Fais rouler vers l'avant en allongeant le corps, aussi loin que tu peux sans creuser le dos.",
   "Reviens en ramenant la roulette vers tes genoux, en contractant les abdos.", REP],
 'Crunch machine': ["Assieds-toi sur la machine, règle le siège et saisis les poignées (ou place les coudes sur les coussins).",
   "Enroule le buste vers l'avant en contractant les abdos, la poitrine vers les genoux.",
   "Marque un temps, puis reviens lentement sans relâcher complètement la tension.", REP],
 'Kickback fessier poulie': ["Fixe une sangle de cheville à la poulie basse et attache-la à une cheville.",
   "Face à la machine, tiens-toi aux montants, le buste légèrement penché en avant.",
   "Pousse la jambe attachée vers l'arrière, presque tendue, en serrant le fessier.",
   "Marque un temps, puis ramène lentement la jambe.", "Fais toutes tes répétitions, puis change de jambe."],
 'Pallof press': ["Règle la poulie à hauteur de poitrine et fixe une poignée. Tiens-toi de profil à la machine, les pieds écartés à la largeur des épaules.",
   "Tiens la poignée à deux mains contre ta poitrine et éloigne-toi d'un pas pour mettre la poulie en tension.",
   "Tends les bras droit devant toi, sans laisser ton buste tourner vers la poulie.",
   "Tiens une à deux secondes, puis ramène les mains contre ta poitrine.",
   "Fais toutes tes répétitions, puis change de côté."],
}
# Familles de prises : un seul exercice dans la liste, la prise se choisit dans la seance ou la routine.
# Chaque prise reste un exercice a part (son nom, son historique). Le premier est celui de la liste.
# famille : (libelle du choix, [(bouton, nom de l'exercice), ...])
FAMILLES = {
 'Tirage vertical': ('Prise', [('Large', 'Tirage vertical'), ('Serrée', 'Tirage vertical prise serrée'),
                               ('Inversée', 'Tirage vertical prise inversée'), ('Neutre', 'Tirage vertical prise neutre')]),
 'Extension poulie': ('Poignée', [('Barre', 'Extension poulie'), ('Corde', 'Extension poulie corde'),
                                  ('Barre en V', 'Extension poulie barre en V'), ('Inversée', 'Extension poulie prise inversée')]),
 'Tractions': ('Prise', [('Normale', 'Tractions'), ('Inversée', 'Tractions supination')]),
 'Rowing barre': ('Prise', [('Normale', 'Rowing barre'), ('Inversée', 'Rowing barre prise inversée')]),
 'Curl barre': ('Prise', [('Normale', 'Curl barre'), ('Inversée', 'Curl inversé barre')]),
 'Développé couché': ('Prise', [('Normale', 'Développé couché'), ('Large', 'Développé couché prise large')]),
 'Développé couché haltères': ('Prise', [('Normale', 'Développé couché haltères'), ('Neutre', 'Développé couché haltères prise neutre')]),
}

# Phrases de A a remplacer une par une : (nom, debut de la phrase fautive, nouvelle phrase ou None pour la retirer).
STEP_FIX = [
 ('Dips', "Abaisse ton corps en fléchissant", "Descends en pliant les coudes et en penchant légèrement le buste en avant, jusqu'à ce que tes bras forment un angle droit."),
 ('Squat', "Tiens la barre en travers", "Place la barre sur le haut de ton dos, posée sur les trapèzes, et tiens-la à deux mains."),
 ('Leg extension', "Assieds-toi sur la machine", "Assieds-toi sur la machine, le dos contre le dossier et le bas des jambes sous le coussin, juste au-dessus des chevilles."),
 ('Leg curl', "Allonge-toi face vers le bas", "Allonge-toi sur le ventre sur la machine, les jambes tendues, le coussin posé à l'arrière des chevilles."),
 ('Écarté poulie', "Tiens-toi debout", "Tiens-toi debout au milieu des deux poulies, les pieds écartés à la largeur des épaules."),
 ('Écarté poulie', "Saisis les poignées avec une prise en pronation", "Saisis une poignée dans chaque main, les bras écartés sur les côtés."),
 ('Tirage horizontal', "Saisis les poignées avec une prise en pronation", "Saisis la poignée en V à deux mains, les paumes face à face, en gardant le dos droit et les épaules relâchées."),
 ('Rowing barre prise inversée', "Tiens une barre avec une prise en pronation", "Tiens la barre en prise supination, les paumes tournées vers le haut, les mains à la largeur des épaules."),
 ('Tirage vertical prise neutre', "Assieds-toi sur la machine de tirage", "Assieds-toi à la machine de tirage vertical et saisis la poignée en V, les paumes face à face."),
 ('Tirage vertical prise neutre', "Règle la cale-genoux", "Règle le coussin des genoux pour bien bloquer tes cuisses."),
 ('Hack squat machine', "Règle la presse", "Installe-toi dans la machine, le dos contre le dossier et les épaules sous les coussins."),
]

# ------------------------------------------------------------------ fabrication
def slug(s): return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def fr(s):
    for a, b in FIX: s = re.sub(a, b, s)
    s = s.strip()
    return s[0].upper() + s[1:]

def main(pa, pb, review=False):
    A = {a['id']: a for a in json.load(open(pa, encoding='utf-8'))}
    B = {b['id']: b for b in json.load(open(pb, encoding='utf-8'))}
    Bs = {slug(k): v for k, v in B.items()}
    src = open(os.path.join(ROOT, 'src', 'js3.js'), encoding='utf-8').read()
    EXI = json.loads(re.search(r'const EXI=(\{.*?\});\n', src).group(1))
    LIB = set(re.findall(r"'([^']+)'", re.search(r'const LIB=(\[.*?\]);\n', src).group(1)))
    assert set(OLD) == set(EXI), ('OLD et EXI different', set(OLD) ^ set(EXI))
    rows = [(n, None, Bs[EXI[n]['i']], OLD[n]) for n in OLD] + [(n, g, B[b], a or None) for g, n, b, a in NEW]
    out, names = {}, set()
    for n, g, b, aid in rows:
        assert n not in names, ('doublon', n); names.add(n)
        if g: assert n not in LIB and g in GROUPS, (n, g)
        a = A[aid] if aid else None
        if n in OWN: st = OWN[n]
        else:
            assert a, ('ni A ni consignes ecrites', n)
            st = [fr(x) for x in a['instruction_steps']['fr']]
        for nm, start, rep in STEP_FIX:
            if nm == n:
                hit = [i for i, x in enumerate(st) if x.startswith(start)]
                assert hit, ('STEP_FIX sans effet', n, start)
                if rep is None: st.pop(hit[0])
                else: st[hit[0]] = rep
        eq = EQUIP_FIX.get(n) or (EQ_A.get(a['equipment']) if a else None) or EQ_B.get(b['equipment'])
        assert eq in EQUIP, ('equipement', n, eq, a and a['equipment'], b['equipment'])
        if n in MUSCLES: m, s = MUSCLES[n]
        elif not g: m, s = EXI[n]['m'], EXI[n]['s']
        else: m, s = [MUS[x] for x in b['primaryMuscles']], [MUS[x] for x in b['secondaryMuscles']]
        assert 2 <= len(st) <= 10 and all(len(x) < 260 for x in st), (n, st)
        for x in st: assert not re.search(r'câble|traîneau|\b(the|your|with)\b', x), (n, x)
        o = dict(eq=eq, m=m, s=s, st=st)
        if g: o['g'] = g
        out[n] = o
        if review:
            print('##', n, '|', eq, '|', ', '.join(m), '/', ', '.join(s), '| A', aid or 'écrit')
            for x in st: print('   ', x)
    fam, seen = {}, set()
    for base, (lab, opts) in FAMILLES.items():
        assert opts[0][1] == base, ('la famille commence par son exercice', base)
        for b_, n in opts:
            assert n in out and n not in seen, ('famille', base, n); seen.add(n)
        fam[base] = [lab, [list(o) for o in opts]]
    dest = os.path.join(ROOT, 'src', 'js3c.js')
    with open(dest, 'w', encoding='utf8', newline='\n') as fh:
        fh.write("/* ===== EXERCICES : consignes, equipement, muscles - fichier genere par tools/gen_exercices.py, ne pas editer a la main ===== */\n")
        fh.write("/* Consignes : exercises-dataset (Hasan Emir Yildirim, MIT ; images Gym visual NON utilisees), corrigees ; ou ecrites pour Forme.\n"
                 "   Liste et muscles : free-exercise-db (domaine public). Voir THIRD_PARTY.txt. */\n")
        fh.write("const EXD=" + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ";\n")
        fh.write("/* familles de prises : {exercice de la liste: [libelle, [[bouton, exercice], ...]]} */\n")
        fh.write("const EXV=" + json.dumps(fam, ensure_ascii=False, separators=(',', ':')) + ";\n")
    nn = sum(1 for o in out.values() if 'g' in o)
    print(len(out), 'exercices ecrits dans', os.path.normpath(dest), '-', os.path.getsize(dest) // 1024, 'Ko ;',
          nn, 'nouveaux ;', sum(1 for n in out if n in OWN), 'consignes ecrites pour Forme')
    eqs = {}
    for o in out.values(): eqs[o['eq']] = eqs.get(o['eq'], 0) + 1
    print(' ', ', '.join('%s %d' % kv for kv in sorted(eqs.items())))

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
if __name__ == '__main__':
    args = [x for x in sys.argv[1:] if x != '--relire']
    if len(args) != 2: sys.exit(__doc__)
    main(args[0], args[1], review='--relire' in sys.argv)
