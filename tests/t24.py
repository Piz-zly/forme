"""Test de bout en bout : esthétique (novembre 2026).

  1. icônes Phosphor : barre d'onglets (duotone au repos, pleine sur l'onglet actif), roue des
     Réglages, chevrons ; toutes dessinées (aucune icône vide), dans les trois ambiances ; le rebond
     de l'onglet actif est coupé avec « réduire les animations » ;
  2. emojis Fluent (style Flat) des quatre repas, en couleur, dans leur pastille ;
  3. chiffres qui défilent (countUp.js) : valeur finale exacte, rejoués seulement si la valeur change,
     jamais avec « réduire les animations » ni pendant une séance ;
  4. confettis : une salve quand un palier est franchi, une seule fois par palier (S.settings.fete),
     aucune au premier affichage ni avec « réduire les animations » ;
  aucune erreur JavaScript, sur index.html et forme.html.

    python3 -m http.server 8765
    python3 tests/t24.py
"""
from playwright.sync_api import sync_playwright
import datetime
from commun import check, clean, termine

BASE = 'http://localhost:8765/'
T = datetime.date.today().isoformat()
DATA = {'settings': {'kcal': 2200, 'goalW': 80, 'startW': 95, 'step': 2.5, 'steps': 10000},
        'weights': {T: 92.5},
        'meals': {T: [{'id': 'm1', 'slot': 'lu', 'name': 'Plat', 'kcal': 650, 'p': 45, 'c': 70, 'f': 15},
                      {'id': 'm2', 'slot': 'bk', 'name': 'Bol', 'kcal': 380, 'p': 14, 'c': 60, 'f': 8}]},
        'act': {T: {'s': 8400, 'k': 2450}}}

def ouvre(b, page, theme, reduit=False, data=None):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce' if reduit else 'no-preference')
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
    pg.goto(BASE + page); pg.wait_for_timeout(300)
    d = dict(data or {}); d['settings'] = dict(d.get('settings', {}), theme=theme, v2=1)
    pg.evaluate('d=>localStorage.setItem("forme.v1",JSON.stringify(d))', d)
    pg.reload(); pg.wait_for_timeout(600)
    return ctx, pg, errs

with sync_playwright() as p:
    b = p.chromium.launch()
    for page in ('index.html', 'forme.html'):
        for theme in ('lune', 'sakura', 'nuit'):
            ctx, pg, errs = ouvre(b, page, theme)
            t = f'{page} {theme}'
            # 1. icônes Phosphor
            check(f'{t} : 4 onglets avec icône au repos et icône active',
                  pg.locator('.tab .ico.off').count() == 4 and pg.locator('.tab .ico.on').count() == 4)
            for tab in ('weight', 'food', 'gym', 'scan'):
                pg.click(f'.tab[data-t="{tab}"]'); pg.wait_for_timeout(200)
                vis = pg.evaluate("""t=>{const b=document.querySelector('.tab[data-t="'+t+'"]');
                  return [b.querySelector('.ico.on').checkVisibility(),b.querySelector('.ico.off').checkVisibility()]}""", tab)
                check(f'{t} : onglet {tab} actif = icône pleine seule', vis == [True, False], vis)
            check(f'{t} : roue des Réglages', pg.locator('[data-act="settings"] svg.ico').count() == 1)
            vides = pg.evaluate("()=>[...document.querySelectorAll('svg.ico')].filter(s=>!s.firstElementChild).length")
            check(f'{t} : aucune icône vide', vides == 0, vides)
            coul = pg.evaluate("()=>getComputedStyle(document.querySelector('.tab[aria-selected=\"true\"] .ico.on')).color")
            check(f'{t} : icône active colorée (pas transparente)', 'rgba(0, 0, 0, 0)' not in coul, coul)
            # 2. emojis Fluent des repas, dans une pastille
            pg.click('.tab[data-t="food"]'); pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(200)
            emo = pg.evaluate("""()=>[...document.querySelectorAll('.sloticon')].map(s=>{const v=s.querySelector('svg.ico');
              return v&&v.getBoundingClientRect().width>0&&v.querySelector('path[fill^="#"]')?1:0})""")
            check(f'{t} : 4 repas avec leur emoji en couleur', len(emo) >= 4 and all(emo), emo)
            check(f'{t} : aucune erreur JavaScript', not errs, errs)
            ctx.close()
        # rebond coupé si le téléphone demande moins d'animations
        ctx, pg, errs = ouvre(b, page, 'lune', reduit=True, data=DATA)
        pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(100)
        an = pg.evaluate("()=>getComputedStyle(document.querySelector('.tab[data-t=\"food\"] .ico.on')).animationName")
        check(f'{page} : réduire les animations -> pas de rebond', an == 'none', an)
        # 3. chiffres : rien ne défile avec « réduire les animations »
        pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(50)
        check(f'{page} : réduire les animations -> chiffres affichés tout de suite', clean(pg.inner_text('[data-cu="act-s"]')) == '8 400')
        ctx.close()
        # 3. chiffres qui défilent
        ctx, pg, errs = ouvre(b, page, 'lune', data=dict(DATA, ui={'tab': 'gym'}))   # démarre sur Muscu : aucun chiffre vu
        pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(50)
        vu = clean(pg.inner_text('[data-cu="act-s"]'))
        check(f'{page} : les pas défilent à l’arrivée', vu != '8 400', vu)
        pg.wait_for_timeout(1300)
        fin = {k: clean(pg.inner_text(f'[data-cu="{k}"]')) for k in ('act-s', 'act-k', 'act-e', 'w-left', 'w-done')}
        check(f'{page} : chiffres finaux exacts', fin == {'act-s': '8 400', 'act-k': '2 450', 'act-e': '1 030', 'w-left': '2,5', 'w-done': '2,5'}, fin)
        pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(50)
        k1 = clean(pg.inner_text('[data-cu="food-kcal"]'))
        pg.wait_for_timeout(1300)
        check(f'{page} : total du Repas défile puis 1 030', k1 != '1 030' and clean(pg.inner_text('[data-cu="food-kcal"]')) == '1 030', k1)
        pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(50)
        check(f'{page} : valeur inchangée -> pas de nouveau défilement', clean(pg.inner_text('[data-cu="act-s"]')) == '8 400')
        # pendant une séance : rien ne défile
        pg.click('.tab[data-t="gym"]'); pg.click('[data-act="g-tab"][data-t="sessions"]'); pg.click('[data-act="g-start"]'); pg.wait_for_timeout(300)
        pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(50)
        pg.click('[data-act="act-edit"]'); pg.fill('#apas', '9000'); pg.click('[data-act="act-save"]'); pg.wait_for_timeout(50)
        check(f'{page} : séance en cours -> pas de défilement', clean(pg.inner_text('[data-cu="act-s"]')) == '9 000')
        check(f'{page} : chiffres sans erreur JavaScript', not errs, errs)
        ctx.close()
        # 4. confettis : une seule fois par palier, jamais avec « réduire les animations »
        for reduit in (False, True):
            ctx, pg, errs = ouvre(b, page, 'lune', reduit=reduit, data=dict(DATA, weights={T: 93.4}))
            pg.evaluate('()=>{window.nbFete=0;const c=window.confetti;window.confetti=Object.assign((...a)=>{window.nbFete++;return c(...a)},c)}')
            fete = lambda: pg.evaluate('window.nbFete')
            st = lambda: pg.evaluate('JSON.parse(localStorage.getItem("forme.v1")).settings.fete')
            pg.click('.tab[data-t="food"]'); pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(100)
            check(f'{page} : premier affichage -> palier noté sans fête', fete() == 0 and st() and st()['n'] == 0, (fete(), st()))
            def pese(v):
                pg.fill('#wval', v); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(100)
            pese('92,4')
            if reduit:
                check(f'{page} : réduire les animations -> pas de confettis', fete() == 0, fete())
            else:
                check(f'{page} : palier franchi -> une salve (2 appels : confettis + étoiles)', fete() == 2, fete())
                check(f'{page} : palier fêté retenu dans les données', st()['n'] == 1, st())
                pese('92,3'); pese('93,1'); pese('92,2')
                check(f'{page} : pesées corrigées -> pas de nouvelle fête', fete() == 2, fete())
            check(f'{page} : confettis sans erreur JavaScript', not errs, errs)
            ctx.close()
    b.close()

termine()
