"""Test de bout en bout : repas proposé selon l'heure, une seule règle partout (nettoyage, 2026.11).

Avant 10 h petit-déjeuner, 10 h-15 h déjeuner, 15 h-18 h collation, ensuite dîner. Horloge simulée.
  1. Scan → « Ajouter au journal » : repas choisi par défaut ;
  2. Semaine → « Ajouter une recette » aujourd'hui : repas sélectionné (un autre jour : déjeuner) ;
  3. Recettes : « ton prochain repas » (pas de collation sur cet écran : dîner de 15 h à 18 h ;
     un autre jour que aujourd'hui commence au petit-déjeuner).

    python3 -m http.server 8765
    python3 tests/t21.py
"""
import datetime, re
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8765/'
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if not ok and extra != '' else ''))
    if not ok: fails.append(label)
SCAN = {'id': 'p1', 'date': '2026-01-01', 'name': 'Yaourt', 'brand': '', 'code': '', 'src': 'manual',
        'per': {'kcal': 60, 'fat': 3, 'sat': 2, 'carbs': 5, 'sugar': 5, 'salt': .1, 'fiber': 0, 'prot': 4, 'fv': 0}, 'additives': []}
# accents remplacés par \S{1,3} : forme.html servie en local n'a pas de <meta charset> (« dã©j. »)
NAMES = {'bk': r'petit-d\S{1,3}j\.', 'lu': r'd\S{1,3}jeuner', 'di': r'd\S{1,3}ner'}
next_is = lambda t, k: re.search(r'prochain repas \(' + NAMES[k] + r'\)', t) is not None
# heure -> (Scan et Semaine, Recettes)
CASES = [(9, 59, 'bk', 'bk'), (10, 0, 'lu', 'lu'), (14, 59, 'lu', 'lu'), (15, 0, 'sn', 'di'), (17, 59, 'sn', 'di'), (18, 0, 'di', 'di'), (23, 30, 'di', 'di')]

with sync_playwright() as p:
    b = p.chromium.launch()
    for page in ('index.html', 'forme.html'):
        for h, m, want, want_rc in CASES:
            hh = '%02d:%02d' % (h, m)
            pg = b.new_page(viewport={'width': 412, 'height': 900}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.clock.install(time=datetime.datetime(2026, 11, 10, h, m))
            pg.goto(BASE + page); pg.wait_for_timeout(300)
            pg.evaluate('s=>localStorage.setItem("forme.v1",JSON.stringify({settings:{v2:1},scans:[s]}))', SCAN)
            pg.reload(); pg.wait_for_timeout(400)
            pg.click('.tab[data-t="scan"]'); pg.click('[data-act="s-open"]'); pg.wait_for_timeout(200)
            pg.click('[data-act="s-journal"]'); pg.wait_for_timeout(200)
            v = pg.input_value('#js')
            check(f'{page} {hh} : Scan propose {want}', v == want, v)
            pg.locator('#layer .scrim').click(position={'x': 10, 'y': 10})
            pg.click('.tab[data-t="food"]'); pg.click('[data-act="food-sub"][data-s="week"]'); pg.wait_for_timeout(200)
            pg.click('[data-act="pl-add"] >> nth=0'); pg.wait_for_timeout(200)
            v = pg.get_attribute('[data-act="pl-slot"][aria-selected="true"]', 'data-s')
            check(f'{page} {hh} : Semaine (aujourd’hui) propose {want}', v == want, v)
            pg.locator('#layer .scrim').click(position={'x': 10, 'y': 10})
            pg.click('[data-act="pl-add"] >> nth=2'); pg.wait_for_timeout(200)
            v = pg.get_attribute('[data-act="pl-slot"][aria-selected="true"]', 'data-s')
            check(f'{page} {hh} : Semaine (autre jour) garde le déjeuner', v == 'lu', v)
            pg.locator('#layer .scrim').click(position={'x': 10, 'y': 10})
            pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(200)
            t = pg.inner_text('#view')
            check(f'{page} {hh} : Recettes visent {want_rc}', next_is(t, want_rc))
            pg.click('[data-act="f-day"][data-n="-1"]'); pg.wait_for_timeout(200)
            check(f'{page} {hh} : Recettes, jour passé : petit-déjeuner', next_is(pg.inner_text('#view'), 'bk'))
            check(f'{page} {hh} : aucune erreur JavaScript', not errs, errs)
            pg.close()
    b.close()

print('\n' + ('TOUT EST OK' if not fails else '%d ECHEC(S) : %s' % (len(fails), fails)))
