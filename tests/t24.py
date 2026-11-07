"""Test de bout en bout : esthétique (novembre 2026).

  1. icônes Phosphor : barre d'onglets (duotone au repos, pleine sur l'onglet actif), roue des
     Réglages, chevrons ; toutes dessinées (aucune icône vide), dans les trois ambiances ; le rebond
     de l'onglet actif est coupé avec « réduire les animations » ;
  aucune erreur JavaScript, sur index.html et forme.html.

    python3 -m http.server 8765
    python3 tests/t24.py
"""
from playwright.sync_api import sync_playwright
from commun import check, termine

BASE = 'http://localhost:8765/'

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
            check(f'{t} : aucune erreur JavaScript', not errs, errs)
            ctx.close()
        # rebond coupé si le téléphone demande moins d'animations
        ctx, pg, errs = ouvre(b, page, 'lune', reduit=True)
        pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(100)
        an = pg.evaluate("()=>getComputedStyle(document.querySelector('.tab[data-t=\"food\"] .ico.on')).animationName")
        check(f'{page} : réduire les animations -> pas de rebond', an == 'none', an)
        ctx.close()
    b.close()

termine()
