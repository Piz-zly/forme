"""Test de bout en bout : protection des données enregistrées (nettoyage, 2026.11).

  1. données illisibles dans le navigateur : l'appli démarre, prévient, garde une copie exacte sous
     forme.v1.abime ; la copie n'est pas écrasée par une seconde panne ; des données normales ne
     créent aucune copie ;
  2. stockage plein (setItem refusé) : un message prévient, l'appli continue ; pas de message en rafale.

    python3 -m http.server 8765
    python3 tests/t22.py
"""
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8765/'
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if not ok and extra != '' else ''))
    if not ok: fails.append(label)
BROKEN = '{"settings":{"kcal":2200},"weights":{"2026-11-01":9'   # coupé en plein milieu
FULL = """()=>{const set=Storage.prototype.setItem;Storage.prototype.setItem=function(k,v){if(k==='forme.v1')throw new DOMException('plein','QuotaExceededError');return set.call(this,k,v)}}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    for page in ('index.html', 'forme.html'):
        pg = b.new_page(viewport={'width': 412, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + page); pg.wait_for_timeout(300)
        pg.evaluate('()=>localStorage.clear()'); pg.reload(); pg.wait_for_timeout(400)
        check(page + ' : données normales, pas de copie ni de message',
              pg.evaluate("localStorage.getItem('forme.v1.abime')") is None and pg.locator('#layer .sheet').count() == 0)

        pg.evaluate('r=>localStorage.setItem("forme.v1",r)', BROKEN); pg.reload(); pg.wait_for_timeout(500)
        check(page + ' : données illisibles, copie exacte gardée', pg.evaluate("localStorage.getItem('forme.v1.abime')") == BROKEN)
        check(page + ' : données illisibles, feuille d’alerte', 'illisibles' in pg.inner_text('#layer'))
        check(page + ' : l’appli démarre (onglet Poids affiché)', pg.locator('#view .card').count() > 0)
        pg.click('#layer [data-act="close"]')
        pg.evaluate('()=>localStorage.setItem("forme.v1","pas du json")'); pg.reload(); pg.wait_for_timeout(500)
        check(page + ' : seconde panne, la première copie reste', pg.evaluate("localStorage.getItem('forme.v1.abime')") == BROKEN)

        pg.evaluate('()=>localStorage.clear()'); pg.reload(); pg.wait_for_timeout(400)
        pg.evaluate(FULL)
        pg.fill('#wval', '82,4'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(100)
        t = pg.inner_text('.toast') if pg.locator('.toast').count() else ''
        check(page + ' : stockage plein, message', 'Enregistrement impossible' in t, t)
        pg.wait_for_timeout(2400)
        pg.click('[data-act="w-step"][data-s="0.1"]'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(100)
        t = pg.inner_text('.toast') if pg.locator('.toast').count() else ''
        check(page + ' : pas de second message dans la minute', 'Enregistrement impossible' not in t, t)
        check(page + ' : aucune erreur JavaScript', not errs, errs)
        pg.close()
    b.close()

print('\n' + ('TOUT EST OK' if not fails else '%d ECHEC(S) : %s' % (len(fails), fails)))
