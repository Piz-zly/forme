"""Test de bout en bout : ajouter un aliment de base en le cherchant (onglet « Chercher »).

    python3 -m http.server 8765
    python3 tests/t9.py [forme.html]
"""
import sys, datetime
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
TODAY = datetime.date.today().isoformat()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 384, 'height': 900}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts' not in m.text and 'net::' not in m.text else None)
    pg.goto('http://localhost:8765/' + PAGE)
    pg.evaluate("""d=>{const s=JSON.parse(localStorage.getItem('forme.v1')||'{}');s.weights={[d]:104.3};localStorage.setItem('forme.v1',JSON.stringify(s))}""", TODAY)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(300)

    pg.click('[data-act="f-add"][data-slot="bk"]'); pg.wait_for_timeout(300)
    tabs = pg.locator('.rcslotseg button').all_inner_texts()
    print('  onglets:', tabs)
    check('Chercher est le premier onglet', tabs and tabs[0] == 'Chercher', tabs)
    check('liste des courants affichee', pg.locator('[data-act="b-pick"]').count() == 24, pg.locator('[data-act="b-pick"]').count())
    pg.screenshot(path='/tmp/t9_a_liste.png')

    # recherche
    pg.fill('#bqin', 'oeuf'); pg.wait_for_timeout(200)
    first = pg.locator('[data-act="b-pick"] .t').first.inner_text()
    check('« oeuf » trouve Œuf entier en premier', first == 'Œuf entier', first)
    pg.fill('#bqin', 'oeufs'); pg.wait_for_timeout(200)
    check('pluriel « oeufs »', pg.locator('[data-act="b-pick"] .t').first.inner_text() == 'Œuf entier')
    pg.fill('#bqin', 'epinards'); pg.wait_for_timeout(200)
    check('« epinards » sans accent', 'pinard' in pg.inner_text('#bres').lower(), pg.inner_text('#bres')[:80])
    pg.fill('#bqin', 'poulet cuit'); pg.wait_for_timeout(200)
    check('deux mots', pg.locator('[data-act="b-pick"] .t').first.inner_text() == 'Blanc de poulet cuit', pg.locator('[data-act="b-pick"] .t').first.inner_text())
    pg.fill('#bqin', 'zzzz'); pg.wait_for_timeout(200)
    check('message si rien', 'Aucun aliment' in pg.inner_text('#bres'))
    pg.fill('#bqin', ''); pg.wait_for_timeout(200)
    pg.click('[data-act="b-cat"][data-k="fl"]'); pg.wait_for_timeout(200)
    res = pg.inner_text('#bres')
    check('section Fruits & légumes', pg.locator('[data-act="b-pick"]').count() > 3 and 'Banane' in res)
    check('sous-sections affichees', all(x in res.lower() for x in ['fruits & compotes', 'légumes & pommes de terre', 'fruits secs']), res[:200])

    # choix de l'oeuf
    pg.fill('#bqin', 'oeuf'); pg.wait_for_timeout(200)
    pg.click('[data-act="b-pick"]'); pg.wait_for_timeout(300)
    txt = pg.inner_text('#layer')
    pg.screenshot(path='/tmp/t9_b_qte.png')
    check('1 oeuf = ~79 kcal', 'Ajouter · 79 kcal' in txt, txt[-120:])
    pg.fill('#bqty', '2'); pg.wait_for_timeout(200)
    check('2 oeufs = ~157 kcal', 'Ajouter · 157 kcal' in pg.inner_text('#layer'), pg.inner_text('#badd'))
    pg.click('#bunits button >> nth=0'); pg.wait_for_timeout(200)
    check('passage en g garde la quantite', pg.input_value('#bqty') == '110', pg.input_value('#bqty'))
    print('  quantite en g:', pg.input_value('#bqty'), pg.inner_text('#badd'))
    pg.click('#bunits button >> nth=1'); pg.wait_for_timeout(200)
    pg.fill('#bqty', '2'); pg.wait_for_timeout(200)
    pg.click('#bfav'); pg.click('#badd'); pg.wait_for_timeout(400)
    view = pg.inner_text('#view')
    check('entree « 2 œufs » dans le journal', '2 œufs' in view, view[:300])
    fav = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).foods.map(f=>f.name)")
    check('ajoute aux favoris', '2 œufs' in fav, fav)

    # riz en grammes
    pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)
    check('recherche remise a zero', pg.input_value('#bqin') == '')
    pg.fill('#bqin', 'riz basmati'); pg.wait_for_timeout(200)
    pg.click('[data-act="b-pick"]'); pg.wait_for_timeout(300)
    check('riz : 1 portion par defaut', 'Ajouter · 195 kcal' in pg.inner_text('#layer'), pg.inner_text('#badd'))
    pg.click('#bunits button >> nth=0'); pg.wait_for_timeout(200)
    check('1 portion = 150 g', pg.input_value('#bqty') == '150', pg.input_value('#bqty'))
    pg.click('#bquick .chip >> nth=2'); pg.wait_for_timeout(200)
    check('puce 150 g', pg.input_value('#bqty') == '150', pg.input_value('#bqty'))
    pg.click('#badd'); pg.wait_for_timeout(400)
    check('entree « 150 g de riz basmati cuit »', '150 g de riz basmati cuit' in pg.inner_text('#view'), pg.inner_text('#view')[:300])

    # pain : unite + elision
    pg.click('[data-act="f-add"][data-slot="sn"]'); pg.wait_for_timeout(300)
    pg.fill('#bqin', 'huile'); pg.wait_for_timeout(200)
    pg.click('[data-act="b-pick"]'); pg.wait_for_timeout(300)
    pg.click('#badd'); pg.wait_for_timeout(400)
    print('  huile ->', [l for l in pg.inner_text('#view').split('\n') if 'huile' in l.lower()])

    # retour + autres onglets
    pg.click('[data-act="f-add"][data-slot="di"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="b-pick"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="b-back"]'); pg.wait_for_timeout(300)
    check('retour a la liste', pg.locator('#bqin').count() == 1)
    for t in ['Scanner', 'Favoris', 'Manuel']:
        pg.click(f'.rcslotseg button:has-text("{t}")'); pg.wait_for_timeout(250)
    check('onglet Manuel affiche', pg.locator('#layer .inp').count() > 0)
    pg.click('.rcslotseg button:has-text("Chercher")'); pg.wait_for_timeout(250)
    check('retour sur Chercher', pg.locator('#bqin').count() == 1)
    ov = pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth && document.querySelector('#layer').scrollWidth<=document.querySelector('#layer').clientWidth+1")
    check('pas de defilement horizontal', ov)
    pg.screenshot(path='/tmp/t9_c_onglets.png')

    print('ERRS', errs)
    check('aucune erreur JS', not errs, errs)
    b.close()
print('\nECHECS:', fails if fails else 'aucun')
sys.exit(1 if fails else 0)
