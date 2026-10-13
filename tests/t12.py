"""Test de bout en bout : la table Ciqual (src/js2g.js) dans l'onglet « Chercher » du Repas.

  1. un aliment absent des aliments de base (maquereau) se trouve grace a Ciqual ;
  2. les aliments familiers passent devant Ciqual (« riz » : Riz basmati cuit d'abord) ;
  3. une section parcourue par les puces ne liste que les aliments familiers, avec le
     nombre d'aliments Ciqual en plus ;
  4. un aliment Ciqual : fiche avec la source, quantite en grammes, ajout au journal avec le
     bon calcul ; une boisson Ciqual est en ml.

    python3 -m http.server 8765
    python3 tests/t12.py
"""
import json, os, tempfile
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = open(os.path.join(ROOT, 'src', 'js2g.js'), encoding='utf-8').read()
CIQUAL = json.loads(src[src.index('const CIQUAL=') + len('const CIQUAL='):src.rindex(';')])
SHOT = os.path.join(tempfile.gettempdir(), 't12_ciqual.png')
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

check('plus de 3000 aliments Ciqual', len(CIQUAL) > 3000, len(CIQUAL))

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 412, 'height': 900})
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)
    names = lambda: pg.locator('#bres [data-act="b-pick"] .t').all_inner_texts()

    # 1. maquereau : absent des aliments de base
    pg.fill('#bqin', 'maquereau'); pg.wait_for_timeout(150)
    n = names()
    print('  maquereau :', n[:4])
    check('maquereau trouve via Ciqual', len(n) >= 3 and all('aquereau' in x for x in n[:3]), n[:3])
    rows = pg.locator('#bres [data-act="b-pick"]').all_inner_texts()
    check('lignes Ciqual marquees « Ciqual », familiers non', any('Ciqual' in t for t in rows) and 'Ciqual' not in rows[0], rows[:2])

    # 2. familiers d'abord
    pg.fill('#bqin', 'riz'); pg.wait_for_timeout(150)
    n = names()
    print('  riz :', n[:6])
    check('riz : un aliment familier en tete', n[0] in ('Riz basmati cuit', 'Riz complet cuit', 'Riz cru'), n[:3])
    check('riz : 50 resultats au plus', 0 < len(n) <= 50, len(n))
    pg.fill('#bqin', 'oeufs brouilles'); pg.wait_for_timeout(150)
    n = names()
    check('« oeufs brouilles » trouve (accents, pluriel)', any('brouill' in x.lower() for x in n), n[:4])

    # 3. section : familiers seulement + mention Ciqual
    pg.fill('#bqin', ''); pg.wait_for_timeout(100)
    pg.click('#bchips .chip[data-k="vpo"]'); pg.wait_for_timeout(150)
    more = pg.locator('#bcqmore').inner_text()
    print('  ', more)
    check('section VPO : mention des aliments Ciqual', 'Ciqual' in more and int(more.split()[1]) > 500, more)
    check('section VPO : aucune ligne Ciqual listee', not any('Ciqual' in t for t in pg.locator('#bres [data-act="b-pick"]').all_inner_texts()))

    # 4. fiche d'un aliment Ciqual et ajout au journal
    code = next(o for o in CIQUAL if o[2].startswith('Maquereau') and len(o) == 7)
    pg.fill('#bqin', 'maquereau'); pg.wait_for_timeout(150)
    pg.click('#bres [data-act="b-pick"][data-id="cq%d"]' % code[0]); pg.wait_for_timeout(200)
    sheet = pg.locator('.sheet').last.inner_text()
    check('fiche : source Anses Ciqual', 'Source : Anses, Table Ciqual 2025' in sheet)
    check('fiche : quantite en g, 100 par defaut', pg.input_value('#bqty') == '100' and 'Quantité (g)' in sheet)
    pg.fill('#bqty', '150'); pg.wait_for_timeout(100)
    want = int(code[3] * 1.5 + 0.5)   # arrondi comme l'application
    btn = pg.inner_text('#badd')
    check('calcul : 150 g = %d kcal' % want, ('%d kcal' % want) in btn.replace(' ', '').replace('\xa0', ''), btn)
    pg.screenshot(path=SHOT)
    pg.click('#badd'); pg.wait_for_timeout(300)
    day = pg.evaluate("JSON.stringify(JSON.parse(localStorage.getItem('forme.v1')))")
    check('journal : « 150 g de maquereau… » enregistre', '150 g de maquereau' in day.lower(), day[:200])

    # boisson Ciqual en ml
    drink = next(o for o in CIQUAL if len(o) == 8 and o[1] == 'boisson.jus')
    pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)
    pg.fill('#bqin', drink[2]); pg.wait_for_timeout(150)
    pg.click('#bres [data-act="b-pick"][data-id="cq%d"]' % drink[0]); pg.wait_for_timeout(200)
    check('boisson Ciqual en ml (%s)' % drink[2], 'Quantité (ml)' in pg.locator('.sheet').last.inner_text())

    print('ERRS', errs)
    check('aucune erreur JavaScript', not errs, errs)
    b.close()

print('\n%d echec(s)' % len(fails) if fails else '\nTOUT EST OK')
