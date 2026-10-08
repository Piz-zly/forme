#!/usr/bin/env python3
"""Genere src/js2c.js : la liste des recettes embarquees dans Forme.

    python3 tools/gen_recettes.py

Pourquoi un script plutot qu'un tableau ecrit a la main : les calories et les
macros de chaque recette sont CALCULEES a partir des ingredients (table ALIM
ci-dessous, valeurs moyennes pour 100 g), donc elles restent coherentes entre
elles et se corrigent a un seul endroit. Pour changer une quantite ou un
aliment : modifier ici, relancer, puis ./src/build.sh.

Droits : les recettes sont redigees pour l'application. Les ingredients et les
proportions ne sont pas proteges ; les etapes sont ecrites a la main, avec nos
propres mots. Rien n'est recopie d'un site.

Convention des poids : viandes, poissons, riz, pates, quinoa, boulgour et
lentilles corail sont comptes CRUS ; pois chiches et haricots rouges sont
egouttes et deja cuits (conserve).
"""
import json, os, sys

# nom, kcal, proteines, glucides, lipides (pour 100 g), grammes par unite
# unites : g, u (piece), tr (tranche), cas, cac, dose
ALIM = {
 'poulet':   ('blanc de poulet cru',            110, 23.0,  0.0,  1.3, {}),
 'dinde_h':  ('dinde hachee 5 %',               130, 20.0,  0.0,  5.5, {}),
 'boeuf5':   ('boeuf hache 5 %',                125, 21.0,  0.0,  5.0, {}),
 'thon':     ('thon au naturel egoutte',        110, 25.0,  0.0,  1.0, {}),
 'saumon':   ('pave de saumon cru',             200, 20.0,  0.0, 13.0, {}),
 'cabillaud':('filet de cabillaud cru',          80, 18.0,  0.0,  0.7, {}),
 'crevettes':('crevettes cuites decortiquees',   90, 19.0,  0.5,  1.0, {}),
 'jambon':   ('jambon blanc',                  105, 20.0,  0.5,  2.5, {'tr': 45}),
 'oeuf':     ('oeuf|oeufs',                     143, 12.5,  0.7,  9.8, {'u': 55}),
 'skyr':     ('skyr nature',                     62, 11.0,  4.0,  0.2, {}),
 'fb0':      ('fromage blanc 0 %',               46,  7.5,  4.0,  0.2, {}),
 'grec0':    ('yaourt grec 0 %',                 55,  9.5,  4.0,  0.3, {}),
 'cottage':  ('cottage cheese',                  98, 11.0,  3.4,  4.3, {}),
 'mozza_l':  ('mozzarella allegee',             160, 20.0,  1.0,  8.0, {}),
 'feta':     ('feta',                           260, 14.0,  1.0, 21.0, {}),
 'parmesan': ('parmesan rape',                  400, 35.0,  0.0, 28.0, {}),
 'lait':     ('lait demi-ecreme',                46,  3.2,  4.8,  1.6, {}),
 'lait_am':  ("lait d'amande sans sucre",        15,  0.5,  0.3,  1.1, {}),
 'whey':     ('whey (proteine en poudre)',      400, 80.0,  7.0,  5.0, {'dose': 30}),
 'avoine':   ("flocons d'avoine",               372, 13.5, 59.0,  7.0, {}),
 'riz':      ('riz basmati cru',                350,  8.0, 77.0,  0.8, {}),
 'pates':    ('pates cru',                      355, 12.5, 72.0,  1.5, {}),
 'quinoa':   ('quinoa cru',                     360, 14.0, 64.0,  6.0, {}),
 'boulgour': ('boulgour cru',                   340, 12.0, 64.0,  1.5, {}),
 'pdt':      ('pommes de terre',                 77,  2.0, 17.0,  0.1, {}),
 'patate_d': ('patate douce',                    86,  1.6, 20.0,  0.1, {}),
 'lentilles':('lentilles corail seches',        340, 24.0, 50.0,  1.5, {}),
 'pois_ch':  ('pois chiches egouttes',          125,  8.5, 17.0,  2.6, {}),
 'h_rouges': ('haricots rouges egouttes',       110,  8.0, 15.0,  0.5, {}),
 'tofu':     ('tofu ferme',                     120, 13.0,  2.0,  7.0, {}),
 'pain_c':   ('pain complet',                   250,  9.0, 44.0,  3.0, {'tr': 35}),
 'wrap':     ('galette de ble (wrap)|galettes de ble (wraps)', 300, 8.0, 50.0, 7.0, {'u': 60}),
 'pain_b':   ('pain a burger|pains a burger',   270,  9.0, 48.0,  4.0, {'u': 60}),
 'huile':    ("huile d'olive",                  900,  0.0,  0.0,100.0, {'cac': 5, 'cas': 13}),
 'cacahuete':('beurre de cacahuete',            600, 26.0, 12.0, 50.0, {'cac': 5, 'cas': 16}),
 'miel':     ('miel',                           300,  0.3, 75.0,  0.0, {'cac': 7}),
 'cacao':    ('cacao maigre en poudre',         320, 20.0, 10.0, 12.0, {'cac': 4, 'cas': 8}),
 'choc':     ('chocolat noir 70 %',             560,  8.0, 35.0, 40.0, {}),
 'amandes':  ('amandes',                        600, 21.0,  7.0, 53.0, {}),
 'soja':     ('sauce soja',                      60,  8.0,  5.0,  0.0, {'cas': 15, 'cac': 5}),
 'passata':  ('coulis de tomate',                30,  1.5,  5.0,  0.3, {}),
 'banane':   ('banane|bananes',                  90,  1.1, 20.0,  0.3, {'u': 100}),
 'pomme':    ('pomme|pommes',                    52,  0.3, 12.0,  0.2, {'u': 150}),
 'f_rouges': ('fruits rouges',                   45,  0.7,  9.0,  0.3, {}),
 'fraises':  ('fraises surgelees',               33,  0.7,  6.0,  0.3, {}),
 'epinards': ('epinards frais',                  23,  2.9,  1.5,  0.4, {}),
 'brocoli':  ('brocoli',                         34,  2.8,  4.0,  0.4, {}),
 'champi':   ('champignons',                     22,  3.0,  1.0,  0.3, {}),
 'courgette':('courgette',                       17,  1.2,  2.5,  0.3, {}),
 'poivron':  ('poivron',                         28,  1.0,  6.0,  0.3, {}),
 'tomate':   ('tomate',                          18,  0.9,  3.5,  0.2, {}),
 'concombre':('concombre',                       12,  0.6,  2.0,  0.1, {}),
 'oignon':   ('oignon',                          40,  1.1,  8.0,  0.1, {}),
 'h_verts':  ('haricots verts',                  30,  2.0,  4.0,  0.2, {}),
 'salade':   ('salade verte',                    15,  1.3,  1.5,  0.2, {}),
 'avocat':   ('avocat',                         165,  2.0,  2.0, 15.0, {}),
}
VIANDE = {'poulet','dinde_h','boeuf5','thon','saumon','cabillaud','crevettes','jambon'}

# Chaque recette : id, nom, repas, minutes, a l'avance, ingredients, etapes, astuce
# repas : bk petit-dejeuner, lu dejeuner, di diner, sn collation
R = []
def rec(id, nom, repas, minutes, ing, etapes, astuce='', avance=False):
    R.append(dict(id=id, nom=nom, repas=repas, minutes=minutes, ing=ing, etapes=etapes, astuce=astuce, avance=avance))

# ------------------------------------------------------------ petit-dejeuner
rec('pancakes', 'Pancakes banane-avoine protéinés', ['bk'], 12,
 [('banane',1,'u'),('oeuf',2,'u'),('avoine',40,'g'),('whey',1,'dose'),('f_rouges',80,'g')],
 ["Écrase la banane dans un bol, ajoute les œufs, les flocons d’avoine et la whey, puis mélange (ou mixe) jusqu’à obtenir une pâte lisse.",
  "Laisse reposer 2 minutes : les flocons gonflent et la pâte épaissit.",
  "Fais cuire de petites louches dans une poêle antiadhésive chaude, 2 minutes de chaque côté.",
  "Dresse avec les fruits rouges. Une cuillère de skyr par-dessus, si tu en as, est un vrai plus."],
 'La pâte se garde une nuit au frais : tu peux la préparer la veille.')
rec('skyrbowl', 'Bol de skyr croustillant', ['bk','sn'], 5,
 [('skyr',200,'g'),('avoine',30,'g'),('f_rouges',100,'g'),('amandes',10,'g'),('miel',1,'cac')],
 ["Fais griller les flocons d’avoine 3 minutes dans une poêle sèche, en remuant, jusqu’à ce qu’ils sentent bon.",
  "Verse le skyr dans un bol et pose les fruits rouges dessus.",
  "Ajoute les flocons grillés, les amandes concassées et un filet de miel."],
 'Les flocons grillés peuvent être faits pour toute la semaine et rangés dans une boîte.')
rec('omelette', 'Omelette jambon-épinards', ['bk','lu','di'], 10,
 [('oeuf',3,'u'),('epinards',80,'g'),('mozza_l',30,'g'),('jambon',1,'tr'),('pain_c',1,'tr')],
 ["Fais tomber les épinards 2 minutes dans une poêle antiadhésive, puis retire-les et presse-les légèrement.",
  "Bats les œufs avec une pincée de sel et de poivre, verse-les dans la poêle chaude.",
  "Quand l’omelette commence à prendre, garnis une moitié d’épinards, de jambon coupé en morceaux et de mozzarella.",
  "Replie, laisse fondre 1 minute et sers avec la tranche de pain complet grillée."])
rec('overnight', 'Overnight oats chocolat-banane', ['bk'], 5,
 [('avoine',45,'g'),('fb0',150,'g'),('whey',20,'g'),('lait_am',100,'ml'),('cacao',1,'cas'),('banane',0.5,'u')],
 ["Dans un bocal, mélange les flocons d’avoine, le cacao et la whey.",
  "Ajoute le fromage blanc et le lait d’amande, remue bien pour qu’il n’y ait pas de grumeaux.",
  "Ferme et mets au frigo toute la nuit.",
  "Le matin, ajoute la banane en rondelles et mange froid, ou 1 minute au micro-ondes."],
 'Se garde 2 jours au frais : fais-en deux d’un coup.', avance=True)
rec('porridge', 'Porridge protéiné pomme-cannelle', ['bk'], 8,
 [('avoine',50,'g'),('lait',200,'ml'),('whey',20,'g'),('pomme',1,'u'),('amandes',10,'g')],
 ["Fais chauffer les flocons d’avoine avec le lait à feu doux 4 minutes, en remuant, jusqu’à ce que ce soit crémeux.",
  "Hors du feu, laisse tiédir 1 minute puis incorpore la whey (sinon elle fait des grumeaux).",
  "Coupe la pomme en dés, fais-la revenir 2 minutes à la poêle avec de la cannelle.",
  "Verse sur le porridge et ajoute les amandes."])
rec('tartine_cottage', 'Tartines cottage, œuf et avocat', ['bk','lu'], 12,
 [('pain_c',2,'tr'),('cottage',100,'g'),('oeuf',2,'u'),('avocat',40,'g')],
 ["Fais cuire les œufs 9 minutes dans l’eau bouillante, passe-les sous l’eau froide et écale-les.",
  "Grille le pain.",
  "Étale le cottage cheese, ajoute l’avocat écrasé à la fourchette, puis les œufs en rondelles.",
  "Poivre, un peu de piment ou de paprika, et c’est prêt."])
rec('mugcake', 'Mug cake chocolat protéiné', ['bk','sn'], 5,
 [('oeuf',1,'u'),('whey',1,'dose'),('avoine',20,'g'),('cacao',1,'cas'),('fb0',50,'g')],
 ["Dans un grand mug, mélange tous les ingrédients à la fourchette jusqu’à avoir une pâte sans grumeaux. Ajoute une demi-cuillère à café de levure si tu en as.",
  "Passe au micro-ondes 1 min 15 à 1 min 30 : le centre doit être juste pris.",
  "Laisse reposer 1 minute avant de manger, directement dans le mug."],
 'Ne dépasse pas 1 min 30, sinon il devient sec.')

# ------------------------------------------------------------ collations
rec('fb_amandes', 'Fromage blanc, amandes et miel', ['sn'], 2,
 [('fb0',200,'g'),('miel',1,'cac'),('amandes',15,'g')],
 ["Verse le fromage blanc dans un bol.", "Ajoute les amandes concassées et le miel."])
rec('mousse_choco', 'Crème chocolat-skyr', ['sn'], 5,
 [('skyr',200,'g'),('cacao',1,'cas'),('miel',1,'cac'),('choc',10,'g')],
 ["Mélange le skyr, le cacao et le miel au fouet jusqu’à obtenir une crème bien lisse.",
  "Râpe le chocolat noir par-dessus.",
  "Laisse 20 minutes au frigo : la texture devient plus mousseuse."])
rec('grec_banane', 'Bol grec, banane et cacahuète', ['sn','bk'], 3,
 [('grec0',150,'g'),('cacahuete',1,'cas'),('banane',0.5,'u')],
 ["Mets le yaourt grec dans un bol.", "Coupe la banane en rondelles et pose-les dessus.",
  "Termine avec le beurre de cacahuète, réchauffé 10 secondes pour qu’il coule."])
rec('oeufs_durs', 'Œufs durs et crudités', ['sn'], 10,
 [('oeuf',2,'u'),('concombre',100,'g'),('tomate',100,'g')],
 ["Plonge les œufs dans l’eau bouillante 9 minutes, puis dans l’eau froide.",
  "Coupe le concombre en bâtonnets et les tomates en quartiers.",
  "Écale les œufs, sale, poivre, ajoute du paprika."],
 'Cuits en avance, les œufs durs se gardent 4 jours au frigo, avec leur coquille.', avance=True)
rec('roules_jambon', 'Roulés jambon-cottage', ['sn'], 5,
 [('jambon',2,'tr'),('cottage',80,'g'),('concombre',50,'g')],
 ["Étale le cottage cheese sur les tranches de jambon.", "Ajoute un bâtonnet de concombre sur chacune.",
  "Roule serré et coupe en deux si tu veux des bouchées."])
rec('glace_skyr', 'Glace express skyr-fraise', ['sn'], 5,
 [('skyr',200,'g'),('fraises',150,'g'),('miel',1,'cac')],
 ["Sors les fraises du congélateur 5 minutes avant, pour que le mixeur ne force pas.",
  "Mixe les fraises avec le skyr et le miel jusqu’à obtenir une crème épaisse.",
  "Mange tout de suite à la cuillère, ou mets 30 minutes au congélateur pour une texture de glace."])
rec('verrine_cheesecake', 'Verrine façon cheesecake au skyr', ['sn','bk'], 8,
 [('skyr',200,'g'),('avoine',20,'g'),('f_rouges',80,'g'),('miel',1,'cac')],
 ["Mixe grossièrement les flocons d’avoine pour faire une poudre, tasse-la au fond d’un verre avec 1 cuillère à café d’eau pour faire une base.",
  "Mélange le skyr avec le miel et étale-le sur la base.",
  "Recouvre de fruits rouges et laisse 30 minutes au frais."])
rec('boules_energie', 'Boules énergie cacahuète-avoine (4)', ['sn'], 10,
 [('avoine',30,'g'),('whey',20,'g'),('cacahuete',15,'g'),('miel',1,'cac'),('lait',20,'ml')],
 ["Mélange tous les ingrédients dans un bol jusqu’à avoir une pâte qui se tient. Ajoute quelques gouttes de lait si c’est trop sec.",
  "Forme 4 boules avec les mains mouillées.",
  "Mets-les 15 minutes au frigo pour qu’elles durcissent."],
 'Double ou triple la quantité : elles se gardent 5 jours au frais.', avance=True)

# ------------------------------------------------------------ dejeuner / diner
rec('bowl_poulet', 'Bowl poulet, riz et brocoli', ['lu','di'], 25,
 [('poulet',150,'g'),('riz',70,'g'),('brocoli',150,'g'),('huile',1,'cac'),('soja',1,'cas')],
 ["Mets le riz à cuire dans l’eau bouillante salée (environ 12 minutes).",
  "Coupe le poulet en dés et fais-le dorer 6 à 8 minutes à la poêle avec l’huile, jusqu’à ce qu’il ne soit plus rose au centre.",
  "Cuis le brocoli 5 minutes à la vapeur ou dans l’eau du riz, pour qu’il reste croquant.",
  "Mélange le poulet avec la sauce soja, puis assemble le tout dans un bol."],
 'Idéal en meal prep : 4 portions se gardent 3 jours au frigo.', avance=True)
rec('poulet_champi', 'Poulet crémeux, champignons et pâtes', ['lu','di'], 25,
 [('poulet',150,'g'),('champi',150,'g'),('fb0',80,'g'),('oignon',50,'g'),('huile',1,'cac'),('pates',70,'g')],
 ["Mets les pâtes à cuire selon le temps du paquet.",
  "Dore le poulet en morceaux avec l’huile, 6 minutes, puis réserve.",
  "Dans la même poêle, fais revenir l’oignon émincé et les champignons coupés 5 minutes.",
  "Remets le poulet, ajoute le fromage blanc hors du feu avec une cuillère de moutarde, sel et poivre.",
  "Mélange avec les pâtes égouttées et un peu d’eau de cuisson."])
rec('wrap_poulet', 'Wrap poulet-crudités sauce fromage blanc', ['lu','di'], 15,
 [('wrap',1,'u'),('poulet',120,'g'),('fb0',50,'g'),('salade',40,'g'),('tomate',80,'g'),('huile',1,'cac')],
 ["Coupe le poulet en lamelles et fais-le dorer 6 minutes avec l’huile, épices au choix (paprika, cumin).",
  "Mélange le fromage blanc avec du sel, du poivre, de l’ail en poudre et un peu de jus de citron.",
  "Étale la sauce sur le wrap, ajoute la salade, la tomate en dés et le poulet.",
  "Roule serré, coupe en deux."])
rec('wrap_thon', 'Wrap thon-avocat', ['lu','di'], 8,
 [('wrap',1,'u'),('thon',100,'g'),('avocat',50,'g'),('tomate',80,'g'),('fb0',40,'g')],
 ["Écrase l’avocat à la fourchette avec le fromage blanc, du sel, du poivre et du citron.",
  "Étale sur le wrap, ajoute le thon émietté et la tomate en dés.",
  "Roule et coupe en deux."])
rec('chili', 'Chili con carne léger', ['lu','di'], 35,
 [('boeuf5',125,'g'),('h_rouges',120,'g'),('passata',150,'g'),('poivron',100,'g'),('oignon',50,'g'),('riz',60,'g')],
 ["Fais revenir l’oignon et le poivron en dés 4 minutes dans une casserole antiadhésive.",
  "Ajoute le bœuf et émiette-le jusqu’à ce qu’il soit bien coloré.",
  "Verse le coulis de tomate et les haricots rouges, ajoute cumin, paprika et piment. Laisse mijoter 15 minutes à feu doux.",
  "Pendant ce temps, cuis le riz. Sers le chili sur le riz."],
 'Meilleur le lendemain, et il se congèle très bien.', avance=True)
rec('pates_thon', 'Pâtes thon-tomate gratinées', ['lu','di'], 25,
 [('pates',80,'g'),('thon',100,'g'),('passata',150,'g'),('mozza_l',40,'g'),('courgette',100,'g')],
 ["Cuis les pâtes selon le paquet et chauffe le four à 200 °C (ou le gril).",
  "Fais revenir la courgette en dés 5 minutes, ajoute le coulis et le thon émietté, assaisonne avec de l’origan.",
  "Mélange avec les pâtes, verse dans un plat, couvre de mozzarella.",
  "Passe 8 minutes au four, jusqu’à ce que le dessus soit doré."])
rec('pates_skyr', 'Pâtes crémeuses au skyr, poulet et épinards', ['lu','di'], 20,
 [('pates',75,'g'),('poulet',120,'g'),('skyr',100,'g'),('epinards',100,'g'),('parmesan',10,'g'),('huile',1,'cac')],
 ["Cuis les pâtes ; garde un verre d’eau de cuisson.",
  "Fais dorer le poulet en dés à la poêle avec l’huile 6 minutes, ajoute les épinards et laisse-les tomber.",
  "Hors du feu, mélange le skyr avec le parmesan et 3 cuillères d’eau de cuisson, pour obtenir une sauce lisse.",
  "Ajoute les pâtes et le poulet, remue vite. Ne remets surtout pas sur le feu : le skyr tournerait."],
 'Le skyr chauffé trop fort devient granuleux : mélange toujours hors du feu.')
rec('saumon_patate', 'Saumon, patate douce et haricots verts', ['di','lu'], 30,
 [('saumon',130,'g'),('patate_d',200,'g'),('h_verts',150,'g')],
 ["Chauffe le four à 200 °C. Coupe la patate douce en bâtonnets et enfourne-la 25 minutes avec du sel et du paprika.",
  "Au bout de 12 minutes, ajoute le saumon sur la plaque avec un peu de citron.",
  "Cuis les haricots verts 8 minutes à l’eau bouillante.",
  "Sers le tout ensemble."])
rec('cabillaud_quinoa', 'Cabillaud au four, quinoa et courgettes', ['di','lu'], 30,
 [('cabillaud',180,'g'),('quinoa',60,'g'),('courgette',200,'g'),('huile',1,'cac'),('tomate',100,'g')],
 ["Chauffe le four à 190 °C. Pose le cabillaud sur une feuille de papier cuisson, avec les tomates en rondelles, l’huile, le sel et le citron. Referme en papillote.",
  "Enfourne 15 minutes.",
  "Cuis le quinoa 12 minutes à l’eau bouillante, égoutte.",
  "Poêle la courgette en rondelles 6 minutes et sers avec le poisson et le quinoa."])
rec('pizza_wrap', 'Pizza wrap express', ['lu','di'], 12,
 [('wrap',1,'u'),('passata',50,'g'),('mozza_l',60,'g'),('jambon',2,'tr'),('champi',50,'g')],
 ["Chauffe le four à 220 °C. Pose le wrap sur une plaque.",
  "Étale le coulis assaisonné d’origan, ajoute le jambon coupé, les champignons en lamelles, puis la mozzarella.",
  "Enfourne 7 à 8 minutes, jusqu’à ce que le bord soit croustillant."],
 'Servie avec une salade, elle devient un vrai repas.')
rec('burger', 'Burger maison et frites de patate douce', ['lu','di'], 35,
 [('pain_b',1,'u'),('boeuf5',130,'g'),('mozza_l',30,'g'),('salade',30,'g'),('tomate',60,'g'),('patate_d',150,'g'),('huile',1,'cac')],
 ["Chauffe le four à 210 °C. Coupe la patate douce en frites, mélange avec l’huile, sel et paprika, et enfourne 25 minutes en retournant à mi-cuisson.",
  "Forme un steak avec le bœuf, sale et poivre, et fais-le cuire 3 minutes de chaque côté dans une poêle très chaude.",
  "Pose la mozzarella sur le steak pour qu’elle fonde en fin de cuisson.",
  "Monte le burger avec la salade et la tomate."])
rec('dahl', 'Dahl de lentilles corail et yaourt grec', ['lu','di'], 25,
 [('lentilles',80,'g'),('passata',100,'g'),('oignon',60,'g'),('epinards',80,'g'),('huile',1,'cac'),('riz',30,'g'),('grec0',100,'g')],
 ["Fais revenir l’oignon émincé dans l’huile avec une cuillère à café de curry, 3 minutes.",
  "Ajoute les lentilles rincées, le coulis et 250 ml d’eau. Laisse cuire 15 minutes, jusqu’à ce que les lentilles se défassent.",
  "Ajoute les épinards en fin de cuisson. Cuis le riz à part.",
  "Sers avec le riz et le yaourt grec par-dessus."],
 'Végétarien et très économique. Il se congèle en portions.', avance=True)
rec('bowl_tofu', 'Bowl tofu croustillant, riz et légumes', ['lu','di'], 25,
 [('tofu',150,'g'),('riz',60,'g'),('poivron',100,'g'),('brocoli',100,'g'),('soja',1,'cas'),('huile',1,'cac'),('cacahuete',1,'cac')],
 ["Presse le tofu dans du papier absorbant 10 minutes, puis coupe-le en cubes.",
  "Fais dorer les cubes à la poêle avec l’huile, 8 minutes, en les retournant.",
  "Cuis le riz ; fais sauter le poivron et le brocoli 5 minutes.",
  "Mélange la sauce soja, le beurre de cacahuète et un peu d’eau chaude pour faire la sauce, et verse sur le bol."])
rec('salade_pois_chiches', 'Salade pois chiches, thon et feta', ['lu','di'], 10,
 [('pois_ch',120,'g'),('thon',100,'g'),('feta',30,'g'),('concombre',100,'g'),('tomate',100,'g'),('oignon',30,'g'),('huile',1,'cac')],
 ["Rince et égoutte les pois chiches.",
  "Coupe le concombre, la tomate et l’oignon en petits dés.",
  "Mélange tout avec le thon émietté et la feta en cubes.",
  "Assaisonne avec l’huile, du citron, du sel, du poivre et de l’origan."],
 'Se transporte très bien dans une boîte, sans réchauffer.', avance=True)
rec('wok_crevettes', 'Wok de crevettes à l’ail, riz et poivrons', ['lu','di'], 20,
 [('crevettes',180,'g'),('riz',70,'g'),('poivron',150,'g'),('courgette',100,'g'),('huile',1,'cac'),('soja',1,'cac')],
 ["Cuis le riz dans l’eau bouillante salée.",
  "Fais sauter le poivron et la courgette en lamelles à feu vif avec l’huile, 6 minutes.",
  "Ajoute les crevettes, une gousse d’ail écrasée et la sauce soja, 2 minutes seulement pour ne pas les durcir.",
  "Sers sur le riz."])
rec('boulettes_dinde', 'Boulettes de dinde, sauce tomate et boulgour', ['lu','di'], 30,
 [('dinde_h',150,'g'),('passata',150,'g'),('boulgour',70,'g'),('courgette',100,'g'),('parmesan',10,'g')],
 ["Mélange la dinde hachée avec le parmesan, du sel, du poivre et des herbes, puis forme 6 petites boulettes.",
  "Fais-les dorer 5 minutes à la poêle antiadhésive en les roulant.",
  "Ajoute la courgette en dés et le coulis, laisse mijoter 10 minutes à couvert.",
  "Cuis le boulgour 10 minutes dans de l’eau bouillante salée et sers avec les boulettes."],
 'Les boulettes se congèlent crues, bien séparées sur une plaque.', avance=True)
rec('shakshuka', 'Shakshuka aux pois chiches', ['lu','di','bk'], 25,
 [('oeuf',3,'u'),('passata',200,'g'),('poivron',100,'g'),('oignon',60,'g'),('pois_ch',80,'g'),('pain_c',1,'tr')],
 ["Fais revenir l’oignon et le poivron en dés 5 minutes dans une poêle avec couvercle.",
  "Ajoute le coulis, les pois chiches, du cumin et du paprika, laisse mijoter 8 minutes.",
  "Creuse trois petits puits, casse un œuf dans chacun, couvre et laisse cuire 5 à 6 minutes, jusqu’à ce que le blanc soit pris.",
  "Sers avec le pain grillé pour tremper."])
rec('cesar', 'Salade César allégée au poulet', ['lu','di'], 20,
 [('poulet',150,'g'),('salade',100,'g'),('pain_c',0.6,'tr'),('parmesan',15,'g'),('grec0',60,'g'),('huile',1,'cac'),('tomate',80,'g')],
 ["Fais dorer le poulet en lamelles avec l’huile, 6 à 8 minutes, puis laisse-le tiédir.",
  "Coupe le pain en petits cubes et fais-les griller à la poêle sèche pour faire des croûtons.",
  "Mélange le yaourt grec avec le parmesan râpé, un peu de citron, de moutarde et de l’ail en poudre : c’est la sauce.",
  "Assemble la salade, le poulet, les tomates et les croûtons, puis nappe de sauce."])
rec('steak_pdt', 'Steak haché, pommes de terre rôties et haricots verts', ['lu','di'], 35,
 [('boeuf5',150,'g'),('pdt',250,'g'),('h_verts',150,'g')],
 ["Chauffe le four à 210 °C. Coupe les pommes de terre en quartiers, sel, paprika, et enfourne 30 minutes sur du papier cuisson.",
  "Cuis les haricots verts 8 minutes dans l’eau bouillante.",
  "Forme un steak avec le bœuf et fais-le cuire 3 à 4 minutes de chaque côté dans une poêle sans matière grasse.",
  "Sers avec une pointe de moutarde."])
rec('poulet_tikka', 'Poulet façon tikka au yaourt, riz et concombre', ['lu','di'], 30,
 [('poulet',150,'g'),('grec0',80,'g'),('riz',70,'g'),('concombre',80,'g'),('huile',1,'cac')],
 ["Mélange le yaourt avec une cuillère à café de curry, de paprika, de l’ail, du sel et du citron. Plonge le poulet en cubes dedans (15 minutes minimum, ou toute la nuit).",
  "Fais dorer le poulet à la poêle avec l’huile, 8 minutes, en le retournant.",
  "Cuis le riz ; coupe le concombre en dés.",
  "Sers le poulet sur le riz avec le concombre."],
 'Mariné la veille, il est encore plus tendre.', avance=True)

# ---------------------------------------------------------------- calcul
def calc(ing):
    kcal = p = c = f = 0.0
    for key, q, unit in ing:
        nom, k, pp, cc, ff, units = ALIM[key]
        g = q if unit in ('g', 'ml') else q * units[unit]
        kcal += k * g / 100; p += pp * g / 100; c += cc * g / 100; f += ff * g / 100
    return round(kcal), round(p, 1), round(c, 1), round(f, 1)

UNITES = {'g': 'g', 'ml': 'ml', 'cas': 'càs', 'cac': 'càc', 'tr': 'tranche|tranches', 'dose': 'dose|doses', 'u': ''}

def accents(s):
    # La table ALIM est ecrite sans accents pour rester lisible ; on les remet ici.
    out = s
    for a, b in [('boeuf','bœuf'),('oeuf','œuf'),('galette de ble','galette de blé'),('galettes de ble','galettes de blé'),
                 ('egoutte','égoutté'),('egouttes','égouttés'),('hache','haché'),('hachee','hachée'),('allegee','allégée'),
                 ('ecreme','écrémé'),('surgelees','surgelées'),('decortiquees','décortiquées'),('cacahuete','cacahuète'),
                 ('pates cru','pâtes crues'),('epinards','épinards'),('pain a burger','pain à burger'),('pains a burger','pains à burger'),
                 ('lait demi-ecreme','lait demi-écrémé'),("lait d'amande","lait d’amande"),("huile d'olive","huile d’olive"),
                 ("flocons d'avoine","flocons d’avoine"),('proteine','protéine'),('pave','pavé')]:
        out = out.replace(a, b)
    return out

def libelle(key, unit):
    nom = ALIM[key][0]
    return accents(nom)

out = []
for r in R:
    kcal, p, c, f = calc(r['ing'])
    veg = not any(k in VIANDE for k, _, _ in r['ing'])
    ing = []
    for key, q, unit in r['ing']:
        ing.append([q, UNITES[unit], libelle(key, unit)])
    out.append(dict(id=r['id'], n=r['nom'], s=r['repas'], t=r['minutes'], k=kcal, p=p, c=c, f=f,
                    veg=1 if veg else 0, prep=1 if r['avance'] else 0, ing=ing, st=r['etapes'], tip=r['astuce']))

# controles : un repas complet doit avoir des macros plausibles
for o in out:
    calc_kcal = 4 * o['p'] + 4 * o['c'] + 9 * o['f']
    ecart = abs(calc_kcal - o['k']) / max(o['k'], 1)
    assert ecart < 0.08, (o['id'], o['k'], round(calc_kcal), 'ecart trop grand (Atwater)')
    assert o['p'] >= 15, (o['id'], 'pas assez de proteines')
    assert 2 <= o['t'] <= 40, o['id']
    assert len(o['st']) >= 2, o['id']
ids = [o['id'] for o in out]
assert len(ids) == len(set(ids)), 'identifiants en double'

here = os.path.dirname(os.path.abspath(__file__))
dest = os.path.join(here, '..', 'src', 'js2c.js')
with open(dest, 'w', encoding='utf8') as fh:
    fh.write("/* ===== RECETTES - fichier genere par tools/gen_recettes.py, ne pas editer a la main ===== */\n")
    fh.write("/* Valeurs par portion, calculees d'apres des valeurs moyennes pour 100 g : indicatives. */\n")
    fh.write("const RECIPES=" + json.dumps(out, ensure_ascii=False, indent=0, separators=(',', ':')).replace('\n', '') + ";\n")

print(len(out), 'recettes ecrites dans', os.path.normpath(dest))
for o in sorted(out, key=lambda x: x['n']):
    print('%-3s %-52s %4d kcal  P%5.1f  G%5.1f  L%5.1f  %2d min %s%s' % (
        ','.join(o['s']), o['n'][:52], o['k'], o['p'], o['c'], o['f'], o['t'], 'V' if o['veg'] else ' ', 'A' if o['prep'] else ' '))
