"""Test de bout en bout : partage entrant des pas.

Simule un partage depuis l'application de podometre (adresse avec ?shared=1),
verifie que les chiffres sont extraits, que l'adresse est nettoyee, et que la
carte Journee se remplit. Verifie aussi la mise en page de la fiche d'exercice.

    python3 -m http.server 8765
    python3 tests/t5.py
"""
from playwright.sync_api import sync_playwright
U='http://localhost:8765/index.html?shared=1&title=Step+Counter&text=J%27ai+marche+8+432+pas+aujourd%27hui+et+brule+412+kcal'
with sync_playwright() as p:
    b=p.chromium.launch()
    ctx=b.new_context(viewport={'width':412,'height':900},device_scale_factor=2)
    pg=ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U); pg.wait_for_timeout(900)
    print('url cleaned:',pg.url.endswith('/index.html'))
    print('prefill pas=',pg.input_value('#apas'),'kcal=',pg.input_value('#akcal'))
    pg.screenshot(path='/tmp/s1.png')
    pg.click('[data-act="act-save"]'); pg.wait_for_timeout(500)
    print('card:',pg.inner_text('#view')[:230].replace('\n',' | '))
    # exercise sheet layout check
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-start"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-pickex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-exinfo"]'); pg.wait_for_timeout(400)
    box=pg.locator('#mov').bounding_box(); print('mov box:',box)
    pg.screenshot(path='/tmp/s2.png')
    print('ERRS',errs)
    b.close()
