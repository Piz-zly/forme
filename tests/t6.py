"""Test de bout en bout : routines.

Creation d'une routine, ajout de deux exercices, reglage des series et des
charges prevues, retour a la liste, demarrage de la seance, et verification que
les valeurs prevues pre-remplissent bien les series.

    python3 -m http.server 8765
    python3 tests/t6.py
"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':412,'height':900},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    print('empty state:', 'Mes routines' in pg.inner_text('#view'))
    pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(300)
    pg.fill('[data-in="rname"]','Half-Body Haut du corps')
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.fill('#exq','developpe couche'); pg.wait_for_timeout(200)
    pg.fill('#exq','Développé couché'); pg.wait_for_timeout(250)
    pg.click('[data-act="g-pickex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.fill('#exq','Tirage vertical'); pg.wait_for_timeout(250)
    pg.click('[data-act="g-pickex"]'); pg.wait_for_timeout(300)
    print('exos:',pg.locator('[data-act="g-rexmenu"]').count())
    pg.click('[data-act="g-rsets"][data-i="0"][data-d="1"]'); pg.wait_for_timeout(250)
    pg.fill('[data-in="rkg"][data-i="0"]','60'); pg.fill('[data-in="rreps"][data-i="0"]','8')
    pg.wait_for_timeout(250)
    print('editor:',pg.inner_text('#view').replace('\n',' | ')[:260])
    pg.screenshot(path='/tmp/r1.png')
    pg.click('[data-act="g-rback"]'); pg.wait_for_timeout(300)
    print('list:',pg.inner_text('#view').replace('\n',' | ')[:220])
    pg.screenshot(path='/tmp/r2.png')
    pg.click('[data-act="g-rstart"]'); pg.wait_for_timeout(500)
    print('session kg prefilled:',pg.input_value('[data-in="set"][data-f="kg"]'),pg.input_value('[data-in="set"][data-f="reps"]'))
    print('sets count ex0:',pg.locator('[data-act="g-check"][data-e="0"]').count())
    pg.screenshot(path='/tmp/r3.png')
    print('ERRS',errs)
    b.close()
