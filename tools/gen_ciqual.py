#!/usr/bin/env python3
"""Genere src/js2g.js : les aliments de la table Ciqual (Anses), pour la recherche du Repas.

    python3 tools/gen_ciqual.py "Table Ciqual 2025_FR_2025_11_03.xlsx"

Source : Anses, Table de composition nutritionnelle des aliments Ciqual 2025
(https://doi.org/10.57745/RDMHWY), Licence Ouverte Etalab 2.0. Le fichier Excel
(1,5 Mo) se telecharge sur recherche.data.gouv.fr ; il ne va PAS dans le depot :
seules les colonnes utiles sont gardees ici.

Les 321 aliments de base (tools/gen_aliments.py) restent prioritaires : noms
familiers, unites usuelles. Ciqual les complete, en grammes seulement.

Pour chaque aliment : code Ciqual, rangement « section.sous-section » (le meme que
SLIB dans src/js4b.js), nom, kcal, proteines, glucides, lipides pour 100 g.
  kcal      : energie Reglement UE 1169/2011 (a defaut : N x Jones avec fibres)
  proteines : N x facteur de Jones
  « traces » et « < x » comptent pour 0 ; une valeur absente (« - ») aussi, mais un
  aliment sans calories ou sans au moins deux des trois macros est ecarte.
Lecture du .xlsx avec la bibliotheque standard (zipfile + xml), sans dependance.
"""
import json, os, re, sys, zipfile
import xml.etree.ElementTree as ET

N = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'

def read_xlsx(path):
    z = zipfile.ZipFile(path)
    ss = [''.join(t.text or '' for t in si.iter(N + 't'))
          for si in ET.fromstring(z.read('xl/sharedStrings.xml')).iter(N + 'si')]
    rows = []
    for r in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).iter(N + 'row'):
        d = {}
        for c in r.iter(N + 'c'):
            col = re.match(r'[A-Z]+', c.get('r')).group()
            v = c.find(N + 'v')
            if v is None:
                t = c.find(N + 'is')
                d[col] = ''.join(x.text or '' for x in t.iter(N + 't')) if t is not None else ''
            else:
                d[col] = ss[int(v.text)] if c.get('t') == 's' else v.text
        rows.append(d)
    return rows

# Colonnes du fichier 2025 (verifiees par les en-tetes ci-dessous).
COLS = dict(grp='B', sgrp='C', code='G', nom='H', kcal='K', kcal2='M', p='O', c='Q', f='R')
HEAD = dict(grp='alim_ssgrp_code', sgrp='alim_ssssgrp_code', code='alim_code', nom='alim_nom_fr',
            kcal='1169', kcal2='Jones', p='Jones', c='Glucides', f='Lipides')

# Rangement : sous-sous-groupe Ciqual d'abord, sinon sous-groupe. None = ecarte.
CAT = {
    '0101': 'plat.plat', '0102': 'plat.soupe', '0103': 'plat.plat', '0104': 'plat.pizza',
    '0105': 'plat.sandwich', '0106': 'plat.pizza',
    '0201': 'fl.legumes', '0202': 'fl.legumes', '0203': 'fec.legumineuses', '0204': 'fl.fruits',
    '020404': 'fl.secs', '0205': 'fl.secs',
    '0301': 'fec.pates', '0302': 'fec.pain', '0303': 'snack.chips', '0304': 'fec.pates', '0305': 'fec.pates',
    '0401': 'vpo.viande', '0402': 'vpo.viande', '0403': 'vpo.charcut', '0404': 'vpo.viande',
    '0405': 'vpo.poisson', '0406': 'vpo.poisson', '0407': 'vpo.poisson', '0408': 'vpo.poisson',
    '0409': 'vpo.poisson', '0410': 'vpo.oeuf',
    '0501': 'lait.lait', '050201': 'lait.yaourt', '050202': 'lait.yaourt', '050203': 'sucre.dessert',
    '050204': 'sucre.dessert', '050205': 'sucre.dessert', '0503': 'lait.fromage', '0504': 'lait.creme',
    '0601': None,                                           # eaux : 0 kcal, des marques
    '060201': 'boisson.jus', '060202': 'boisson.jus', '060203': 'boisson.jus', '060204': 'lait.lait',
    '060205': 'boisson.veg', '060206': 'boisson.cafe', '060207': 'boisson.cafe', '0603': 'boisson.alcool',
    '0701': 'sucre.sucre', '0702': 'sucre.choco', '0703': 'sucre.choco', '0704': 'sucre.tartiner',
    '0705': 'fec.pain', '0706': 'sucre.biscuit', '0707': 'fec.cereales', '0708': 'snack.barre',
    '0709': 'sucre.biscuit',
    '0801': 'sucre.dessert', '0802': 'sucre.dessert', '0803': 'sucre.dessert',
    '0901': 'lait.creme', '0902': 'gras.huile', '0903': 'lait.creme', '0904': 'gras.huile', '0905': 'gras.huile',
    '1001': 'gras.sauce', '1002': 'gras.sauce', '1003': 'gras.sauce', '1004': None, '1005': 'gras.sauce',
    '1006': 'gras.sauce', '1007': 'gras.sauce', '1008': None, '1009': 'fec.legumineuses',
    '1010': 'fec.legumineuses',
    '1101': None, '1102': None, '1103': None, '1104': None,  # aliments infantiles
    '0000': None,                                           # aliments « moyens » sans groupe
}
# Boissons : quantite en ml (100 ml ~ 100 g a l'echelle de l'application).
ML = ('0501', '0602', '0603')
ML_NOT = ('050103', '060207')

def val(s):
    """'12,5' -> 12.5 ; 'traces' et '< 0,5' -> 0 ; '-' ou vide -> None."""
    s = (s or '').strip()
    if s in ('', '-'): return None
    if s == 'traces' or s.startswith('<'): return 0.0
    return float(s.replace(',', '.'))

def joli(n):
    """Espaces normalises, ligature oe des mots courants, majuscule initiale."""
    n = re.sub(r'\s+', ' ', n).strip()
    n = re.sub(r'\b(o|O|bo|Bo|co|Co|sœ)eu(f|fs|r|rs)\b', lambda m: m.group(1).replace('o', 'œ').replace('O', 'Œ') + 'u' + m.group(2), n)
    return n[0].upper() + n[1:]

def main(path):
    rows = read_xlsx(path)
    head = rows[0]
    for k, frag in HEAD.items():
        assert frag in head.get(COLS[k], ''), ('colonne inattendue', k, COLS[k], head.get(COLS[k]))
    out, skipped, cats = [], {}, {}
    for r in rows[1:]:
        g = lambda k: r.get(COLS[k], '')
        sg, grp = g('sgrp'), g('grp')
        cat = CAT[sg] if sg in CAT else CAT.get(grp, 'manque')
        assert cat != 'manque', ('groupe Ciqual non range', grp, sg, g('nom'))
        if cat is None:
            skipped['groupe ecarte'] = skipped.get('groupe ecarte', 0) + 1; continue
        k = val(g('kcal'))
        if k is None: k = val(g('kcal2'))
        mac = [val(g(x)) for x in ('p', 'c', 'f')]
        if k is None or sum(m is None for m in mac) >= 2:
            skipped['valeurs manquantes'] = skipped.get('valeurs manquantes', 0) + 1; continue
        p, c, f = (round(m or 0, 1) for m in mac)
        p, c, f = (int(x) if x == int(x) else x for x in (p, c, f))
        assert 0 <= k <= 900 and p + c + f <= 101, g('nom')
        o = [int(g('code')), cat, joli(g('nom')), round(k), p, c, f]
        if (grp in ML or sg[:4] in ML) and sg not in ML_NOT and 'poudre' not in o[2].lower():
            o.append(1)
        out.append(o)
        cats[cat] = cats.get(cat, 0) + 1
    out.sort(key=lambda o: o[0])
    here = os.path.dirname(os.path.abspath(__file__))
    dest = os.path.join(here, '..', 'src', 'js2g.js')
    with open(dest, 'w', encoding='utf8', newline='\n') as fh:
        fh.write("/* ===== TABLE CIQUAL - fichier genere par tools/gen_ciqual.py, ne pas editer a la main ===== */\n")
        fh.write("/* Source : Anses, Table de composition nutritionnelle des aliments Ciqual 2025, Licence Ouverte Etalab 2.0. */\n")
        fh.write("/* [code Ciqual, rangement, nom, kcal, prot., gluc., lip. pour 100 g, (1 = boisson en ml)] */\n")
        fh.write("const CIQUAL=" + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ";\n")
    print(len(out), 'aliments Ciqual ecrits dans', os.path.normpath(dest), '-', os.path.getsize(dest) // 1024, 'Ko')
    print('  ecartes :', skipped)
    print(' ', ', '.join('%s %d' % kv for kv in sorted(cats.items())))

if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
