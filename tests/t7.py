"""Test de bout en bout : muscles en rouge.

Ouvre une fiche d'exercice, verifie que l'image coloree est bien chargee, que la
bascule "Image simple" change la source, et qu'aucune image ne manque (404).

    python3 -m http.server 8765
    python3 tests/t7.py
"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':412,'height':900},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]; miss=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.on('response',lambda r: miss.append(r.url) if r.status>=400 else None)
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-start"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-pickex"]'); pg.wait_for_timeout(400)
    pg.click('[data-act="g-exinfo"]'); pg.wait_for_timeout(600)
    print('src0:',pg.get_attribute('#mov img','src'))
    pg.screenshot(path='/tmp/x1.png')
    pg.locator('#redbtn').click(force=True); pg.wait_for_timeout(500)
    print('apres bascule:',pg.get_attribute('#mov img','src'), pg.inner_text('#redbtn'))
    pg.screenshot(path='/tmp/x2.png')
    pg.locator('#redbtn').click(force=True); pg.wait_for_timeout(1300)
    print('anim f:',pg.get_attribute('#mov','data-f'),'cap',pg.inner_text('#movcap'))
    srcs=pg.eval_on_selector_all('#mov img','e=>e.map(x=>x.src.split("/").pop())')
    print('srcs:',srcs)
    nat=pg.eval_on_selector_all('#mov img','e=>e.map(x=>x.naturalWidth)')
    print('chargées:',nat)
    print('404:',[u for u in miss if 'ill/' in u][:5])
    print('ERRS',errs)
    b.close()
