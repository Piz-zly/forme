"""Test de bout en bout : nombres de 1 000 et plus (bug corrige en 2026.11.07).

L'appli ecrit « 2 200 » avec une espace fine ; avant la correction, la relecture donnait 2.
  1. Reglages : objectif 2 200 kcal et 10 000 pas inchanges apres Enregistrer sans rien toucher ;
  2. journal : un aliment a 1 200 kcal reste a 1 200 apres ouverture et Enregistrer ;
  3. Journee : « 8 400 » pas tapes avec une espace donnent 8400.
Sur index.html (telephone) et forme.html (Claude).

    python3 -m http.server 8765
    python3 tests/t20.py
"""
import datetime, json
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8765/'
TODAY = datetime.date.today().isoformat()
from commun import check, fails, termine
state = lambda pg: json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))

with sync_playwright() as p:
    b = p.chromium.launch()
    for page in ('index.html', 'forme.html'):
        ctx = b.new_context(viewport={'width': 412, 'height': 900})
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + page); pg.wait_for_timeout(500)
        pg.evaluate("""d=>localStorage.setItem('forme.v1',JSON.stringify({settings:{kcal:2200,steps:10000,v2:1},
          meals:{[d]:[{id:'x1',slot:'lu',name:'Pizza',kcal:1200,p:40,c:130,f:50}]}}))""", TODAY)
        pg.reload(); pg.wait_for_timeout(500)

        pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
        pg.click('[data-act="set-save"]'); pg.wait_for_timeout(300)
        s = state(pg)['settings']
        check(page + ' : Réglages, 2 200 kcal gardées', s['kcal'] == 2200, s['kcal'])
        check(page + ' : Réglages, 10 000 pas gardés', s['steps'] == 10000, s['steps'])

        pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(300)
        pg.click('[data-act="f-edit"][data-id="x1"]'); pg.wait_for_timeout(300)
        pg.click('[data-act="f-save"]'); pg.wait_for_timeout(300)
        k = state(pg)['meals'][TODAY][0]['kcal']
        check(page + ' : aliment à 1 200 kcal gardé', k == 1200, k)

        pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(300)
        pg.click('[data-act="act-edit"] >> nth=0'); pg.wait_for_timeout(300)
        pg.fill('#apas', '8 400'); pg.click('[data-act="act-save"]'); pg.wait_for_timeout(300)
        a = state(pg).get('act', {}).get(TODAY, {})
        check(page + ' : « 8 400 » pas donnent 8400', a.get('s') == 8400, a)
        check(page + ' : aucune erreur JavaScript', not errs, errs)
        ctx.close()
    b.close()

termine()
