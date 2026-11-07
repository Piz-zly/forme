"""Test de bout en bout : fluidité et gestes (2026.11.07-4). navigator.vibrate est simulé.

  1. écran mis à jour sans tout refaire (Idiomorph) : pendant la saisie d'une charge en séance, un rendu garde le même
     champ, le focus, la valeur et le curseur ;
  2. geste Retour : ferme une feuille, puis ramène un sous-onglet du Repas au Journal ; avec CloseWatcher (touche Échap)
     et sans (historique, page.go_back) ; pas de boucle ;
  3. balayage du journal du Repas (événements tactiles simulés) : jour précédent / suivant, jamais après aujourd'hui,
     rien pendant une séance ;
  4. ligne du journal tirée à gauche : « Supprimer », toast « Supprimé · Annuler » qui remet exactement la ligne ;
  5. feuille tirée vers le bas : fermée ; geste trop court : reste ouverte ;
  6. vibrations appelées ou non selon Réglages → Vibrations ;
  7. web-vitals chargé seulement quand on appuie sur « Mesurer la fluidité » (version téléphone).

    python3 -m http.server 8765
    python3 tests/t25.py
"""
import datetime, json
from playwright.sync_api import sync_playwright
from commun import check, termine

BASE = 'http://localhost:8765/'
T = datetime.date.today(); D = lambda k: (T - datetime.timedelta(days=k)).isoformat()
MEALS = [{'id': 'm1', 'slot': 'bk', 'name': 'Bol', 'kcal': 380, 'p': 14, 'c': 60, 'f': 8},
         {'id': 'm2', 'slot': 'bk', 'name': 'Café', 'kcal': 20, 'p': 1, 'c': 2, 'f': 0},
         {'id': 'm3', 'slot': 'lu', 'name': 'Plat', 'kcal': 650, 'p': 45, 'c': 70, 'f': 15}]
DATA = {'settings': {'v2': 1, 'goalW': 80, 'startW': 95}, 'weights': {D(0): 92.5}, 'meals': {D(0): MEALS},
        'routines': [{'id': 'r1', 'name': 'Haut', 'exercises': [{'name': 'Développé couché', 'sets': [{'kg': '60', 'reps': '8'}] * 2}]}],
        'ui': {'tab': 'food'}}
VIB = 'navigator.vibrate=p=>{(window.__vib=window.__vib||[]).push(p);return true};'

def ouvre(b, page='index.html', data=None, sans_cw=False, reduit=False):
    ctx = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True,
                        reduced_motion='reduce' if reduit else 'no-preference')
    ctx.add_init_script(VIB + ('delete window.CloseWatcher;' if sans_cw else ''))
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(BASE + page); pg.wait_for_timeout(300)
    pg.evaluate('d=>localStorage.setItem("forme.v1",JSON.stringify(d))', data or DATA)
    pg.reload(); pg.wait_for_timeout(700)
    return ctx, pg, errs

# glisse un doigt de (x0,y0) à (x1,y1) en n pas, sur l'élément sous le point de départ
GLISSE = """([x0,y0,x1,y1,n])=>{const el=document.elementFromPoint(x0,y0);
  const ev=(type,x,y)=>{const t=new Touch({identifier:7,target:el,clientX:x,clientY:y,screenX:x,screenY:y,pageX:x,pageY:y});
    el.dispatchEvent(new TouchEvent(type,{touches:type==='touchend'?[]:[t],targetTouches:type==='touchend'?[]:[t],changedTouches:[t],bubbles:true,cancelable:true}))};
  ev('touchstart',x0,y0);for(let i=1;i<=n;i++)ev('touchmove',x0+(x1-x0)*i/n,y0+(y1-y0)*i/n);ev('touchend',x1,y1);
  return el.className||el.tagName}"""
jour = lambda pg: pg.inner_text('.datebar .d').split('\n')[0]
vib = lambda pg: pg.evaluate('window.__vib||[]')
lu = lambda pg: pg.evaluate('JSON.parse(localStorage.getItem("forme.v1"))')

with sync_playwright() as p:
    b = p.chromium.launch()

    # 1. focus et valeur gardés pendant la saisie en séance
    ctx, pg, errs = ouvre(b, data=dict(DATA, ui={'tab': 'gym'}))
    pg.click('[data-act="g-tab"][data-t="sessions"]'); pg.wait_for_timeout(200)
    pg.locator('[data-act="g-rstart"]').first.click(); pg.wait_for_timeout(400)
    kg = pg.locator('input[data-f="kg"]').first
    kg.click(); kg.fill(''); pg.keyboard.type('62,5'); pg.keyboard.press('ArrowLeft')
    pg.evaluate('()=>{document.activeElement.__moi=1}')
    pg.evaluate('()=>document.querySelector(\'[data-act="g-addset"]\').click()'); pg.wait_for_timeout(300)   # rendu complet, focus non déplacé
    st = pg.evaluate('()=>{const a=document.activeElement;return [a.__moi===1,a.value,a.selectionStart,document.querySelectorAll(\'input[data-f="kg"]\').length]}')
    check('séance : après un rendu, même champ, focus, valeur et curseur gardés', st[:3] == [True, '62,5', 3] and st[3] == 3, st)
    check('séance : aucune erreur JavaScript', not errs, errs)
    ctx.close()

    # 2. geste Retour, avec CloseWatcher (Échap) puis sans (historique)
    for sans_cw in (False, True):
        tag = 'Retour (historique)' if sans_cw else 'Retour (CloseWatcher)'
        ctx, pg, errs = ouvre(b, sans_cw=sans_cw)
        retour = (lambda: (pg.go_back(), pg.wait_for_timeout(300))) if sans_cw else (lambda: (pg.keyboard.press('Escape'), pg.wait_for_timeout(300)))
        n0 = pg.evaluate('history.length')
        pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
        check(f'{tag} : feuille ouverte', pg.locator('#layer .sheet').count() == 1)
        retour()
        check(f'{tag} : Retour ferme la feuille', pg.locator('#layer .sheet').count() == 0 and pg.url.endswith('index.html'), pg.url)
        pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(500)
        retour()
        check(f'{tag} : Retour ramène Recettes au Journal', pg.locator('[data-act="food-sub"][data-s="journal"][aria-selected="true"]').count() == 1)
        pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
        pg.locator('#layer .scrim').click(position={'x': 10, 'y': 10}); pg.wait_for_timeout(300)
        if sans_cw:
            check(f'{tag} : feuille fermée au doigt -> entrée d’historique retirée, pas de boucle', pg.evaluate('history.length') <= n0 + 2 and pg.evaluate('history.state') is None, (n0, pg.evaluate('history.length'), pg.evaluate('history.state')))
        check(f'{tag} : aucune erreur JavaScript', not errs, errs)
        ctx.close()

    # 3. balayage de jour, 4. ligne tirée à gauche + Annuler
    ctx, pg, errs = ouvre(b)
    pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(500)
    j0 = jour(pg)
    pg.evaluate(GLISSE, [60, 330, 330, 335, 8]); pg.wait_for_timeout(500)
    check('balayage vers la droite -> jour précédent', jour(pg) != j0 and [15] in vib(pg), (j0, jour(pg), vib(pg)))
    pg.evaluate(GLISSE, [330, 330, 60, 335, 8]); pg.wait_for_timeout(500)
    check('balayage vers la gauche -> retour à aujourd’hui', jour(pg) == j0, jour(pg))
    pg.evaluate(GLISSE, [330, 330, 60, 335, 8]); pg.wait_for_timeout(500)
    check('jamais après aujourd’hui', jour(pg) == j0, jour(pg))
    avant = [e['id'] for e in lu(pg)['meals'][D(0)]]
    r = pg.locator('.entry[data-id="m2"]').bounding_box()
    y = r['y'] + r['height'] / 2
    pg.evaluate(GLISSE, [300, y, 140, y + 3, 8]); pg.wait_for_timeout(300)
    check('ligne tirée à gauche -> bouton « Supprimer », le jour ne change pas', pg.locator('.swdel[data-id="m2"]').count() == 1 and jour(pg) == j0)
    pg.click('.swdel'); pg.wait_for_timeout(300)
    check('Supprimer -> ligne retirée, toast « Supprimé · Annuler », vibration d’avertissement',
          pg.locator('.entry[data-id="m2"]').count() == 0 and 'Supprimé' in pg.inner_text('.toast') and pg.locator('.toast .toastbtn').inner_text() == 'Annuler'
          and [40, 100, 40] in vib(pg) and [e['id'] for e in lu(pg)['meals'][D(0)]] == ['m1', 'm3'])
    pg.click('.toast .toastbtn'); pg.wait_for_timeout(300)
    apres = lu(pg)['meals'][D(0)]
    check('Annuler -> la ligne revient, à la même place, identique', [e['id'] for e in apres] == avant and apres[1] == MEALS[1] and pg.locator('.entry[data-id="m2"]').count() == 1, apres)
    pg.click('[data-act="f-day"][data-n="-1"]'); pg.wait_for_timeout(400)
    check('bouton jour précédent : toujours là', jour(pg) != j0)
    check('journal : aucune erreur JavaScript', not errs, errs)
    ctx.close()
    # moins d'animations : rien ne suit le doigt, mais l'action a lieu
    ctx, pg, errs = ouvre(b, reduit=True)
    pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(300)
    j0 = jour(pg); pg.evaluate(GLISSE, [60, 330, 330, 335, 8]); pg.wait_for_timeout(300)
    check('réduire les animations : le balayage change quand même de jour', jour(pg) != j0, jour(pg))
    ctx.close()
    # pas de balayage pendant une séance
    act = {'id': 'a1', 'name': 'Séance', 'start': 1, 'exercises': []}
    ctx, pg, errs = ouvre(b, data=dict(DATA, active=act))
    pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(300)
    j0 = jour(pg); pg.evaluate(GLISSE, [60, 330, 330, 335, 8]); pg.wait_for_timeout(400)
    check('séance en cours -> pas de balayage de jour', jour(pg) == j0, jour(pg))
    ctx.close()

    # 5. feuille tirée vers le bas, 6. vibrations selon le réglage
    for vibre in (True, False):
        ctx, pg, errs = ouvre(b, data=dict(DATA, settings=dict(DATA['settings'], vibre=vibre), ui={'tab': 'weight'}))
        pg.fill('#wval', '92,1'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(200)
        check(f'vibrations {"activées" if vibre else "coupées"} : pesée enregistrée', (vib(pg) == [[30, 60, 40]]) if vibre else (vib(pg) == []), vib(pg))
        if vibre:
            pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
            g = pg.locator('#layer .grab').bounding_box(); x, y = g['x'] + 20, g['y'] + 2
            pg.evaluate(GLISSE, [x, y, x, y + 40, 4]); pg.wait_for_timeout(400)
            check('feuille tirée de 40 px : reste ouverte et revient en place', pg.locator('#layer .sheet').count() == 1 and pg.evaluate("document.querySelector('#layer .sheet').style.transform") == '')
            check('Réglages : case « Vibrations » cochée', pg.locator('#gvib').is_checked())
            pg.evaluate(GLISSE, [x, y, x, y + 260, 8]); pg.wait_for_timeout(400)
            check('feuille tirée vers le bas : fermée', pg.locator('#layer .sheet').count() == 0)
        check('vibrations : aucune erreur JavaScript', not errs, errs)
        ctx.close()

    # 7. web-vitals chargé seulement à la demande
    ctx, pg, errs = ouvre(b)
    req = []; pg.on('request', lambda r: 'web-vitals' in r.url and req.append(r.url))
    pg.reload(); pg.wait_for_timeout(700)
    check('web-vitals pas chargé au démarrage', not req and pg.evaluate('typeof webVitals') == 'undefined', req)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="perf"]'); pg.wait_for_timeout(800)
    out = pg.inner_text('#perfout')
    check('« Mesurer la fluidité » -> web-vitals chargé une fois, mesure affichée en mots simples', len(req) == 1 and pg.evaluate('typeof webVitals') == 'object'
          and ('Mesure en cours' in out or ('Réaction la plus lente' in out and ' ms (' in out and '>' not in out)), (req, out))
    check('web-vitals : aucune erreur JavaScript', not errs, errs)
    ctx.close()

    # version Claude : démarre, retour et suppression avec Annuler
    ctx, pg, errs = ouvre(b, page='forme.html')
    pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(300)
    pg.click('.entry[data-id="m1"]'); pg.wait_for_timeout(300); pg.click('[data-act="f-del"]'); pg.wait_for_timeout(300)
    pg.click('.toast .toastbtn'); pg.wait_for_timeout(300)
    check('forme.html : suppression puis Annuler', pg.locator('.entry[data-id="m1"]').count() == 1)
    check('forme.html : pas de « Mesurer la fluidité » (téléphone seulement)', pg.locator('[data-act="settings"]').count() == 1 and (pg.click('[data-act="settings"]') or pg.wait_for_timeout(300) or pg.locator('[data-act="perf"]').count() == 0))
    check('forme.html : aucune erreur JavaScript', not errs, errs)
    ctx.close()
    b.close()

termine()
