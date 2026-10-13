"""Test de bout en bout : seance de musculation.

Verifie la barre de repos (etat au repos, en repos, -15, +15, choix de duree),
l'ajout d'un exercice, la validation d'une serie, et l'animation de la fiche
d'exercice. Captures dans /tmp/g*.png.

    python3 -m http.server 8765   # depuis la racine du projet
    python3 tests/t4.py
"""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':412,'height':900},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    print('bar before session:',pg.locator('#rbar').count())
    pg.click('[data-act="g-new"]') if pg.locator('[data-act="g-new"]').count() else pg.click('text=Nouvelle séance')
    pg.wait_for_timeout(400)
    print('bar idle:',pg.locator('#rbar').count(), pg.inner_text('#rbar').replace('\n',' '))
    # add exercise
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-pickex"]'); pg.wait_for_timeout(400)
    print('after pick:',pg.inner_text('#view')[:90].replace('\n',' | '))
    pg.screenshot(path='/tmp/g1.png')
    # fill a set and validate
    pg.fill('[data-in="set"][data-f="kg"]','60'); pg.fill('[data-in="set"][data-f="reps"]','8')
    pg.click('[data-act="g-check"]'); pg.wait_for_timeout(1300)
    print('bar running:',pg.inner_text('#rbar').replace('\n',' '))
    pg.screenshot(path='/tmp/g2.png')
    pg.click('[data-act="g-rest-more"]'); pg.wait_for_timeout(200)
    print('after +15:',pg.inner_text('#rbar').replace('\n',' '))
    pg.click('[data-act="g-rest-dur"]'); pg.wait_for_timeout(300)
    print('durs:',pg.locator('.dur').count())
    pg.screenshot(path='/tmp/g3.png')
    pg.click('[data-act="g-rest-set"][data-s="60"]'); pg.wait_for_timeout(300)
    print('after set 60:',pg.inner_text('#rbar').replace('\n',' '))
    # exercise info with movement
    pg.click('[data-act="g-exinfo"]'); pg.wait_for_timeout(300)
    f1=pg.get_attribute('#mov','data-f'); pg.wait_for_timeout(1100); f2=pg.get_attribute('#mov','data-f')
    print('anim frames:',f1,'->',f2,'cap:',pg.inner_text('#movcap'))
    pg.screenshot(path='/tmp/g4.png')
    pg.locator('#movbtn').click(force=True); pg.wait_for_timeout(1200)
    print('paused stays:',pg.get_attribute('#mov','data-f'))
    pg.click('[data-act="close"]'); pg.wait_for_timeout(200)
    pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(300)
    print('bar hidden off gym:',pg.locator('#rbar').count())
    print('ERRS',errs)
    b.close()
