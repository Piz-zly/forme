"""Test de bout en bout : ambiance Lune + Kikkō (2026.11).

  1. Lune : la lune détaillée est là et chargée (image en data URI, naturalWidth > 0), en haut à droite,
     avec son halo ; le motif Kikkō .kk est là, devant la lune ; plus aucun nuage .cl ; étoiles gardées ;
     cartes à --panel .8 ;
  2. Sakura et Néon : rien de .ln n'est visible ; leur --panel ne change pas ;
  3. aucune erreur JavaScript, sur index.html et forme.html.

    python3 -m http.server 8765
    python3 tests/t23.py
"""
from playwright.sync_api import sync_playwright
from commun import check, termine

BASE = 'http://localhost:8765/'
PANEL = {'lune': 'rgba(35,28,71,.8)', 'sakura': 'rgba(255,255,255,.80)', 'nuit': '#15152E'}

with sync_playwright() as p:
    b = p.chromium.launch()
    for page in ('index.html', 'forme.html'):
        for theme in ('lune', 'sakura', 'nuit'):
            pg = b.new_page(viewport={'width': 412, 'height': 915}); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto(BASE + page); pg.wait_for_timeout(300)
            pg.evaluate('t=>localStorage.setItem("forme.v1",JSON.stringify({settings:{theme:t,v2:1}}))', theme)
            pg.reload(); pg.wait_for_timeout(600)
            panel = pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--panel').trim()")
            check(f'{page} {theme} : --panel', panel == PANEL[theme], panel)
            vis = pg.evaluate("()=>[...document.querySelectorAll('.ln, .ln *')].some(e=>e.checkVisibility())")
            if theme != 'lune':
                check(f'{page} {theme} : rien de la Lune n’est visible', not vis)
            else:
                img = pg.evaluate("""()=>{const i=document.querySelector('.ln .moon img');if(!i)return null;
                  const r=i.getBoundingClientRect();return {w:i.naturalWidth,src:i.src.slice(0,23),x:r.left+r.width/2,y:r.top+r.height/2,vis:i.checkVisibility()}}""")
                check(f'{page} lune : image de la lune chargée', bool(img) and img['w'] > 0 and img['vis'], img)
                check(f'{page} lune : image intégrée dans la page', bool(img) and img['src'] == 'data:image/webp;base64,', img)
                check(f'{page} lune : en haut à droite', bool(img) and img['x'] > 206 and img['y'] < 300, img)
                check(f'{page} lune : halo', pg.locator('.ln .moon .mglow').count() == 1)
                order = pg.evaluate("()=>{const m=document.querySelector('.ln .moon'),k=document.querySelector('.ln .kk');return !!(m&&k&&m.compareDocumentPosition(k)&Node.DOCUMENT_POSITION_FOLLOWING)&&k.checkVisibility()}")
                check(f'{page} lune : motif Kikkō présent, devant la lune', order)
                check(f'{page} lune : plus aucun nuage', pg.locator('.ln .cl').count() == 0)
                check(f'{page} lune : étoiles gardées', pg.locator('.ln .stars').count() == 1 and pg.locator('.deco .pt').count() == 9)
            check(f'{page} {theme} : aucune erreur JavaScript', not errs, errs)
            pg.close()
    b.close()

termine()
