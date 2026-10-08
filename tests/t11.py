"""Test de bout en bout : les aliments de base du Repas sont ranges par section et sous-section,
comme la bibliotheque du Scan.

  1. chaque aliment de src/js2e.js apparait dans sa section (puces de « Chercher ») ;
  2. les regles de classement de la bibliotheque (qui servent aux produits scannes) donnent le
     meme rangement que la table des aliments pour au moins 95 % des aliments : cela verifie
     que les deux classements restent coherents.

    python3 -m http.server 8765
    python3 tests/t11.py
"""
import re, json, sys, datetime, os
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
src = open(os.path.join(ROOT, 'src', 'js2e.js'), encoding='utf-8').read()
FOODS = json.loads(src[src.index('const FOODS=') + len('const FOODS='):src.rindex(';')])
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 384, 'height': 900})
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)

    chips = pg.locator('#bchips .chip').all_inner_texts()
    print('  puces :', chips)
    check('puces : Courants puis les sections', chips[0] == 'Courants' and 'VPO' in chips and 'Laitiers' in chips and 'Plats' in chips, chips)

    # 1. tout aliment est dans sa section, sous sa sous-section
    expected = {}
    for f in FOODS: expected.setdefault(f['cat'].split('.')[0], []).append(f['n'])
    total = 0; missing = []
    ids = pg.evaluate("[...document.querySelectorAll('#bchips .chip')].map(c=>c.dataset.k)")
    for k in ids:
        if k == 'top': continue
        pg.click('#bchips .chip[data-k="%s"]' % k); pg.wait_for_timeout(120)
        shown = pg.locator('#bres [data-act="b-pick"] .t').all_inner_texts()
        total += len(shown)
        missing += [n for n in expected.get(k, []) if n not in shown]
        subs = pg.locator('#bres .libsub').count()
        if subs == 0: missing.append('(aucune sous-section pour ' + k + ')')
    check('les %d aliments sont tous affiches dans leur section' % len(FOODS), total == len(FOODS) and not missing, (total, missing[:5]))
    pg.click('#bchips .chip[data-k="vpo"]'); pg.wait_for_timeout(150)
    heads = [h.split('·')[0].strip().lower() for h in pg.locator('#bres .libsub').all_inner_texts()]
    check('VPO : viandes, charcuteries, poissons, œufs', heads == ['viandes', 'charcuteries', 'poissons & fruits de mer', 'œufs'], heads)
    pg.screenshot(path='/tmp/t11_vpo.png')
    # une recherche reste a plat
    pg.fill('#bqin', 'saumon'); pg.wait_for_timeout(150)
    check('recherche : liste a plat', pg.locator('#bres .libsub').count() == 0 and pg.locator('#bres [data-act="b-pick"]').count() >= 3)
    pg.keyboard.press('Escape')
    pg.evaluate("document.querySelector('.scrim')&&document.querySelector('.scrim').remove()")

    # 2. coherence avec les regles de la bibliotheque (produits scannes)
    items = []
    for i, f in enumerate(FOODS):
        items.append(dict(id='f%03d' % i, date=datetime.date.today().isoformat(), name=f['n'], brand='', code='', src='manual',
                          per=dict(kcal=f['k'] + i * 0.01, fat=f['f'], sat=0, carbs=f['c'], sugar=0, salt=0, fiber=0, prot=f['p'], fv=0), additives=[]))
    pg.evaluate("a=>{const s=JSON.parse(localStorage.getItem('forme.v1')||'{}');s.scans=a;localStorage.setItem('forme.v1',JSON.stringify(s))}", items)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="scan"]'); pg.click('[data-act="scan-sub"][data-s="lib"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(500)
    where = pg.evaluate("""()=>{const out={};document.querySelectorAll('#libres .libsec').forEach(sec=>{
      let sub='';sec.querySelectorAll('.libbody > *').forEach(el=>{
        if(el.classList.contains('libsub'))sub=el.textContent.split('·')[0].trim();
        else el.querySelectorAll('.li .t').forEach(t=>{out[t.textContent.replace(/×\\d+/,'').trim()]=sec.querySelector('.libh .grow').textContent.trim()+' > '+sub});
      })});return out}""")
    b.close()

# libelles section > sous-section, lus dans src/js4b.js
js = open(os.path.join(ROOT, 'src', 'js4b.js'), encoding='utf-8').read()
LAB = {}
for m in re.finditer(r"\{id:'(\w+)',s:'[^']*',n:'([^']*)',subs:\[(.*?)\]\}", js):
    for k, n in re.findall(r"\['(\w+)','([^']*)'\]", m.group(3)):
        LAB[m.group(1) + '.' + k] = m.group(2) + ' > ' + n
ok = 0; n_seen = 0; diff = []
for f in FOODS:
    got = where.get(f['n'])
    if got is None: continue   # fusionne avec un aliment identique (ex. Tomate cerise = Tomate) : normal
    n_seen += 1
    if got == LAB[f['cat']]: ok += 1
    else: diff.append((f['n'], got, LAB[f['cat']]))
ratio = ok / n_seen
print('  coherence : %d / %d (%.0f %%)' % (ok, n_seen, ratio * 100))
for d in diff: print('     ', d)
check('rangement table des aliments et regles de la bibliotheque coherents (>= 95 %)', ratio >= .95, '%.0f %%' % (ratio * 100))
check('aucune erreur JS', not errs, errs)
print('\nECHECS:', fails if fails else 'aucun')
sys.exit(1 if fails else 0)
