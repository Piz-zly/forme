"""Test de bout en bout : animations douces (src/js1b.js, outil maison).

Chaque scenario est joue deux fois : telephone normal, puis « reduire les animations » active.
  1. journal du Repas : un aliment ajoute apparait (et il est bien enregistre) ;
  2. journal : suppression -> donnee retiree tout de suite, copie inerte qui s'efface puis disparait ;
     deux suppressions coup sur coup : les deux comptent, aucune erreur ;
  3. routine : « Monter » -> les deux exercices glissent ;
  4. pesees : la nouvelle pesee apparait ;
  5. bibliotheque du Scan : produit retire -> copie qui s'efface ; pendant une recherche, rien ne s'anime ;
  6. plafond : plus de 60 lignes a l'ecran -> rien ne s'anime.
Avec « reduire les animations » : aucune animation, et exactement le meme resultat.

    python3 -m http.server 8765
    python3 tests/t15.py
"""
import datetime, json
from playwright.sync_api import sync_playwright

TODAY = datetime.date.today()
D = lambda n: (TODAY - datetime.timedelta(days=n)).isoformat()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

SPY = """window.__anims=[];const _a=Element.prototype.animate;
Element.prototype.animate=function(k,o){window.__anims.push({ak:this.dataset&&this.dataset.ak||null,ghost:this.getAttribute('aria-hidden')==='true',kf:JSON.stringify(k[0])});return _a.call(this,k,o)};"""
def prod(i, name):
    return dict(id='p%d' % i, date=TODAY.isoformat(), name=name, brand='', code='', src='manual', additives=[],
                per=dict(kcal=120, fat=5, sat=1, carbs=12, sugar=3, salt=.2, fiber=1, prot=6, fv=0))
SEED = dict(
    meals={TODAY.isoformat(): [dict(id='e1', slot='lu', name='Pomme', kcal=52, p=0.3, c=14, f=0.2),
                               dict(id='e2', slot='lu', name='Yaourt nature', kcal=70, p=5, c=7, f=2),
                               dict(id='e3', slot='lu', name='Pain complet', kcal=90, p=3, c=15, f=1)]},
    weights={D(3): 95.0, D(2): 94.7, D(1): 94.5},
    scans=[prod(1, 'Saumon fumé'), prod(2, 'Skyr nature'), prod(3, 'Pain complet tranché'), prod(4, 'Thon au naturel')])   # p1 et p4 : même section

def scenario(b, reduced):
    tag = '[réduit] ' if reduced else '[normal] '
    ctx = b.new_context(viewport={'width': 412, 'height': 900}, reduced_motion='reduce' if reduced else 'no-preference')
    ctx.add_init_script(SPY)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(300)
    pg.evaluate("s=>{const o=JSON.parse(localStorage.getItem('forme.v1')||'{}');Object.assign(o,s);localStorage.setItem('forme.v1',JSON.stringify(o))}", SEED)
    pg.reload(); pg.wait_for_timeout(400)
    st = lambda: json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
    anims = lambda: pg.evaluate("window.__anims.splice(0)")
    ghosts = lambda: pg.locator('#view [aria-hidden="true"].entry, #view [aria-hidden="true"].li, #view [aria-hidden="true"].ex').count()

    # 1. ajout d'un aliment
    pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(200); anims()
    pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(250)
    pg.fill('#bqin', 'banane'); pg.wait_for_timeout(100)
    pg.click('#bres [data-act="b-pick"]'); pg.wait_for_timeout(150)
    pg.click('#badd'); pg.wait_for_timeout(50)
    a = anims(); ids = [e['id'] for e in st()['meals'][TODAY.isoformat()]]
    check(tag + 'aliment ajouté : enregistré et affiché', len(ids) == 4 and pg.locator('#view .entry[data-ak="%s"]' % ids[-1]).count() == 1)
    appear = [x for x in a if x['ak'] == ids[-1] and '"opacity":0' in x['kf']]
    check(tag + ('aucune animation' if reduced else 'il apparaît en douceur'), (not a) if reduced else len(appear) == 1, a)

    # 2. suppression, puis deux suppressions coup sur coup
    pg.click('#view .entry[data-ak="e1"]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-act="f-del"]')
    ids = [e['id'] for e in st()['meals'][TODAY.isoformat()]]
    g1 = ghosts()
    check(tag + 'suppression enregistrée tout de suite', 'e1' not in ids and pg.locator('#view .entry[data-ak="e1"]').count() == 0, ids)
    check(tag + ('pas de copie qui s\'efface' if reduced else 'copie inerte qui s\'efface'), g1 == (0 if reduced else 1), g1)
    pg.click('#view .entry[data-ak="e2"]'); pg.wait_for_timeout(30)        # pendant l'effacement
    pg.click('.sheet [data-act="f-del"]'); pg.wait_for_timeout(30)
    pg.click('#view .entry[data-ak="e3"]'); pg.wait_for_timeout(30)
    pg.click('.sheet [data-act="f-del"]')
    ids = [e['id'] for e in st()['meals'][TODAY.isoformat()]]
    check(tag + 'deux suppressions coup sur coup : les deux comptent', not ({'e2', 'e3'} & set(ids)) and len(ids) == 1, ids)
    pg.wait_for_timeout(450)
    check(tag + 'plus aucune copie après l\'effacement', ghosts() == 0 and pg.locator('#view .entry').count() == 1)
    a = anims()
    check(tag + ('aucune animation' if reduced else 'animations jouées pour les suppressions'), (not a) if reduced else any(x['ghost'] for x in a), a[:3])

    # 3. routine : Monter
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(200)
    for n in ('Squat', 'Leg curl'):
        pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(200)
        pg.fill('#exq', n); pg.wait_for_timeout(100)
        pg.click('#exlist [data-act="g-pickex"][data-name="%s"]' % n); pg.wait_for_timeout(200)
        pg.click('.sheet [data-act="g-rcok"]'); pg.wait_for_timeout(200)  # routine : « Combien de séries ? » (3 par défaut)
    anims()
    pg.click('[data-act="g-rexmenu"][data-i="1"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-rmove"][data-i="1"][data-d="-1"]'); pg.wait_for_timeout(50)
    order = [e['name'] for e in st()['routines'][-1]['exercises']]
    a = anims(); moved = {x['ak'] for x in a if 'translate' in x['kf']}
    check(tag + 'routine : ordre enregistré (Leg curl, Squat)', order == ['Leg curl', 'Squat'], order)
    check(tag + ('aucune animation' if reduced else 'les deux exercices glissent'), (not a) if reduced else moved == {'Squat#1', 'Leg curl#1'}, a)

    # 4. pesee
    pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(250); anims()
    pg.fill('#wval', '103,5'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(50)
    a = anims()
    check(tag + 'pesée enregistrée', st()['weights'].get(TODAY.isoformat()) == 103.5)
    check(tag + ('aucune animation' if reduced else 'la pesée apparaît'), (not a) if reduced else any(x['ak'] == 'w' + TODAY.isoformat() and '"opacity":0' in x['kf'] for x in a), a)

    # 5. bibliotheque du Scan
    pg.click('.tab[data-t="scan"]'); pg.click('[data-act="scan-sub"][data-s="lib"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(200); anims()
    pg.click('[data-act="lib-open"][data-id="p1"]'); pg.wait_for_timeout(200)
    pg.click('.sheet [data-act="lib-del"]'); pg.wait_for_timeout(150)
    pg.click('.sheet [data-act="confirm-ok"]'); pg.wait_for_timeout(30)
    left = [p['id'] for p in st()['scans']]
    check(tag + 'produit retiré tout de suite', left == ['p2', 'p3', 'p4'], left)
    g = ghosts(); a = anims()
    check(tag + ('rien ne s\'anime' if reduced else 'copie du produit qui s\'efface'), (not a and g == 0) if reduced else (g == 1 and any(x['ghost'] for x in a)), (g, a))
    pg.wait_for_timeout(400)
    pg.fill('#libq', 'sky'); pg.wait_for_timeout(100)
    pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(100); pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(100)
    check(tag + 'recherche dans la bibliothèque : aucune animation', not anims())

    check(tag + 'aucune erreur JavaScript', not errs, errs)
    ctx.close()

def cap(b):
    ctx = b.new_context(viewport={'width': 412, 'height': 900}); ctx.add_init_script(SPY)
    pg = ctx.new_page()
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(300)
    w = {D(i): 100 + i / 10 for i in range(1, 81)}
    pg.evaluate("w=>{const o=JSON.parse(localStorage.getItem('forme.v1')||'{}');o.weights=w;localStorage.setItem('forme.v1',JSON.stringify(o))}", w)
    pg.reload(); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="w-all"]'); pg.wait_for_timeout(200); pg.evaluate('window.__anims.splice(0)')
    pg.fill('#wval', '99,5'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(50)
    n = pg.locator('#view [data-ak]').count(); a = pg.evaluate('window.__anims.splice(0)')
    check('plafond : %d pesées affichées, aucune animation' % n, n > 60 and not a, a[:2])
    ctx.close()

with sync_playwright() as p:
    b = p.chromium.launch()
    cap(b)
    scenario(b, reduced=False)
    scenario(b, reduced=True)
    b.close()
print('\n%d echec(s)' % len(fails) if fails else '\nTOUT EST OK')
