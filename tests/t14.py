"""Test de bout en bout : recherches tolerantes aux fautes de frappe (Fuse.js, vendor/fuse.basic.min.js).

  1. les 15 recherches avec fautes (aliments, exercices) trouvent ce qu'on attend, en tete ;
  2. sans faute, la recherche d'aliments donne exactement les memes resultats qu'avant
     (comparaison avec l'ancien algorithme, recopie ici) ;
  3. pas de resultat absurde pour des mots sans rapport ;
  4. favoris du Repas et bibliotheque du Scan : accents et fautes toleres ;
  5. vitesse : 5 000 aliments fictifs ajoutes a la liste, chaque lettre tapee mesuree.

    python3 -m http.server 8765
    python3 tests/t14.py
"""
import datetime, json, os, random, re, unicodedata
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
rd = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
def jsarr(src, name):
    i = src.index('const %s=' % name) + len('const %s=' % name)
    return json.loads(src[i:src.index(';\n', i)])
FOODS = jsarr(rd('src', 'js2e.js'), 'FOODS')
CIQUAL = jsarr(rd('src', 'js2g.js'), 'CIQUAL')
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

# ---- ancien algorithme de foodSearch (avant Fuse.js), pour la non-regression
def norm(s):
    s = s.lower().replace('œ', 'oe').replace('æ', 'ae')
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    return re.sub(r"[’'\-]", ' ', s)
ALL = [dict(n=f['n'], k=norm(f['n'] + ' ' + f.get('a', '')), top=f.get('top'), cq=0) for f in FOODS] + \
      [dict(n=c[2], k=norm(c[2]), top=None, cq=1) for c in CIQUAL]
def old_search(q):
    t = [w[:-1] if len(w) > 3 and w[-1] in 'sx' else w for w in norm(q).split()]
    res = []
    for f in ALL:
        sc = 0
        for w in t:
            i = f['k'].find(w)
            if i < 0: break
            sc += 0 if i == 0 else 1 if f['k'][i - 1] == ' ' else 3
        else:
            res.append((sc - (.5 if f['top'] else 0) + (1.5 if f['cq'] else 0), len(f['n']), f['n']))
    return [n for _, _, n in sorted(res, key=lambda x: (x[0], x[1]))][:50]

FOOD15 = [('poulé', 'Poulet'), ('yaourt nateur', 'Yaourt nature'), ('brocolis', 'Brocoli'), ('fromgae blanc', 'Fromage blanc'),
          ('saumom', 'Saumon'), ('bannane', 'Banane'), ('pate complete', 'Pâtes complètes'), ('blanc poulet', 'Blanc de poulet'),
          ('steack haché', 'Steak haché'), ('riz basmatti', 'Riz basmati')]
EXO15 = [('devlopé couché', 'Développé couché'), ('tracion', 'Tractions'), ('elevation laterale', 'Élévations latérales'),
         ('couché développé', 'Développé couché'), ('squatt', 'Squat')]
EXACT = ['poulet', 'riz', 'oeufs', 'yaourt grec', 'pain complet', 'thon', 'lait', 'pomme', 'fromage blanc 0', 'huile olive', 'banane', 'sau']
ABSURD = ['voiture', 'ordinateur', 'xyzzy', 'téléphone', 'chaussure']
first = lambda l, want: bool(l) and norm(want) in norm(l[0])

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 412, 'height': 900})
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    check('Fuse.js charge (fichier local)', pg.evaluate("typeof Fuse") == 'function')
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)
    def fs(q):
        pg.fill('#bqin', q); pg.wait_for_timeout(60)
        return pg.locator('#bres [data-act="b-pick"] .t').all_inner_texts()

    print('-- 15 recherches avec fautes')
    for q, want in FOOD15:
        r = fs(q)
        check('aliment  %-16s -> %-16s' % (q, want), first(r, want), r[:3])
    print('-- sans faute : memes resultats qu\'avant')
    for q in EXACT:
        r, o = fs(q), old_search(q)
        check('identique : %-14s (%d resultats)' % (q, len(r)), r == o, (r[:4], o[:4]))
    print('-- mots sans rapport : rien d\'absurde')
    for q in ABSURD:
        r = fs(q)
        print('   %-12s -> %s' % (q, r[:3]))
        check('pas de resultat pour « %s »' % q, len(r) == 0, r[:3])

    # exercices
    pg.keyboard.press('Escape'); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="gym"]'); pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(200)
    def es(q):
        pg.fill('#exq', q); pg.wait_for_timeout(60)
        return pg.locator('#exlist [data-act="g-pickex"] .t').all_inner_texts()
    for q, want in EXO15:
        r = es(q)
        check('exercice %-18s -> %-20s' % (q, want), first(r, want), r[:3])
    r = es('développé couché')
    check('exercice sans faute : « Développé couché » en premier', r[:1] == ['Développé couché'], r[:3])
    r = es('voiture')
    check('exercice : rien pour « voiture »', not r, r[:3])

    # favoris et bibliotheque du Scan
    today = datetime.date.today().isoformat()
    scans = [dict(id='p%d' % i, date=today, name=n, brand=br, code='', src='manual', additives=[],
                  per=dict(kcal=120, fat=5, sat=1, carbs=12, sugar=3, salt=.2, fiber=1, prot=6, fv=0))
             for i, (n, br) in enumerate([('Yaourt grec nature', 'Fage'), ('Pâtes complètes', 'Barilla'), ('Saumon fumé', 'Labeyrie'), ('Chocolat noir 70 %', 'Lindt')])]
    favs = [dict(id='f1', name='Porridge protéiné', kcal=350, p=25, c=45, f=8), dict(id='f2', name='Crêpe complète', kcal=400, p=20, c=40, f=15)]
    pg.evaluate("([a,b])=>{const s=JSON.parse(localStorage.getItem('forme.v1')||'{}');s.scans=a;s.foods=b;localStorage.setItem('forme.v1',JSON.stringify(s))}", [scans, favs])
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="add-tab"][data-t="mine"]'); pg.wait_for_timeout(200)
    for q, want in [('crepe', 'Crêpe complète'), ('porige', 'Porridge protéiné'), ('protéiné porridge', 'Porridge protéiné')]:
        pg.fill('#favq', q); pg.wait_for_timeout(80)
        r = pg.locator('#favlist .t').all_inner_texts()
        check('favoris  %-18s -> %s' % (q, want), r[:1] == [want], r)
    pg.keyboard.press('Escape'); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(400)
    pg.click('.tab[data-t="scan"]'); pg.click('[data-act="scan-sub"][data-s="lib"]'); pg.wait_for_timeout(200)
    for q, want in [('saumom', 'Saumon fumé'), ('pates completes', 'Pâtes complètes'), ('lint', 'Chocolat noir 70 %'), ('nature yaourt', 'Yaourt grec nature')]:
        pg.fill('#libq', q); pg.wait_for_timeout(100)
        r = pg.locator('[data-act="lib-open"] .t').all_inner_texts()
        check('Scan     %-18s -> %s' % (q, want), len(r) == 1 and r[0].startswith(want), r)

    # vitesse : 5 000 aliments fictifs en plus de la vraie liste
    random.seed(1)
    words = sorted({w for c in CIQUAL for w in re.findall(r'[a-zà-ÿœ]{4,}', c[2].lower())})
    fake = [[900000 + i, 'autre.autre', 'Essai %d %s %s %s' % (i, *random.sample(words, 3)), 100, 5, 10, 3] for i in range(5000)]
    html = rd('index.html').replace('const CIQUAL=[', 'const CIQUAL=' + json.dumps(fake, ensure_ascii=False)[:-1] + ',', 1)
    pg2 = ctx.new_page(); pg2.on('pageerror', lambda e: errs.append(str(e)))
    pg2.route('**/index.html', lambda r: r.fulfill(status=200, content_type='text/html; charset=utf-8', body=html))
    pg2.goto('http://localhost:8765/index.html'); pg2.wait_for_timeout(2500)   # vocabulaire construit apres 1,5 s
    pg2.click('.tab[data-t="food"]'); pg2.click('[data-act="f-add"][data-slot="lu"]'); pg2.wait_for_timeout(300)
    n = pg2.evaluate("document.querySelectorAll('#bres [data-act=\"b-pick\"]').length")
    times = pg2.evaluate("""qs=>{const el=document.querySelector('#bqin'),out=[];
      for(const q of qs){for(let i=1;i<=q.length;i++){el.value=q.slice(0,i);const t=performance.now();
        el.dispatchEvent(new Event('input',{bubbles:true}));out.push(performance.now()-t)}}return out}""", [q for q, _ in FOOD15])
    total = 3524 + 5000
    print('   %d frappes sur %d aliments : moyenne %.1f ms, pire %.1f ms' % (len(times), total, sum(times) / len(times), max(times)))
    r = pg2.locator('#bres [data-act="b-pick"] .t').all_inner_texts()
    check('avec 5 000 aliments en plus : « riz basmatti » trouve Riz basmati', first(r, 'Riz basmati'), r[:3])
    check('chaque lettre tapee prend moins de 50 ms (pire : %.0f ms)' % max(times), max(times) < 50)

    print('ERRS', errs)
    check('aucune erreur JavaScript', not errs, errs)
    b.close()

print('\n%d echec(s)' % len(fails) if fails else '\nTOUT EST OK')
