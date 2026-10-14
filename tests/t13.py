"""Test de bout en bout : bibliotheque d'exercices enrichie (src/js3c.js, tools/gen_exercices.py).

  1. donnees : 175 exercices, tous avec consignes en francais, equipement et muscles ; aucune
     trace des medias de Gym visual (images/, videos/, gymvisual) dans l'application ;
  2. « Ajouter un exercice » : les nouveaux exercices sont dans leur groupe (dont Avant-bras) ;
  3. filtres Muscle et Equipement, seuls et ensemble, avec la recherche (sans accents) ;
  4. familles de prises : un seul exercice dans la liste, choix de la prise dans la routine et la seance ;
  5. fiche d'un nouvel exercice (illustre, sans schema img2) : illustration, consignes, equipement, muscles ;
     fiche d'un exercice illustre : illustration, schema, consignes ;
  6. les 175 exercices ont une illustration : chaque fiche s'ouvre sans image cassee (couleur et
     image simple), chaque vignette de la liste se charge ;
  7. un exercice perso (cree par l'utilisateur, sans illustration) : vignette lettre, fiche propre ;
  8. aucune image cassee, aucune requete en erreur.

    python3 -m http.server 8765
    python3 tests/t13.py
"""
import json, os, re, tempfile
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
rd = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
src = rd('src', 'js3c.js')
EXD = json.loads(src[src.index('const EXD=') + len('const EXD='):src.index(';\n', src.index('const EXD='))])
EXV = json.loads(src[src.index('const EXV=') + len('const EXV='):src.rindex(';')])
HIDDEN = {n for b, (l, o) in EXV.items() for t, n in o if n != b}
SHOT = tempfile.gettempdir()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

# 1. donnees
new = [n for n, e in EXD.items() if e.get('g')]
check('175 exercices dont 115 nouveaux', len(EXD) == 175 and len(new) == 115, (len(EXD), len(new)))
bad = [n for n, e in EXD.items() if not (e['st'] and e['eq'] and e['m'])]
check('chaque exercice a consignes, equipement, muscle principal', not bad, bad[:5])
txt = ' '.join(x for e in EXD.values() for x in e['st'])
check('consignes sans « câble », « traîneau » ni anglais', not re.search(r'câble|traîneau|\b(the|your|with)\b', txt))
app = rd('index.html') + rd('forme.html') + rd('sw.js')
check('aucune reference aux medias de Gym visual', not re.search(r'gymvisual|gif_url|videos/|images/\d{4}', app))
check('aucun dossier de medias copie', not any(os.path.exists(os.path.join(ROOT, d)) for d in ('images', 'videos')))

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 412, 'height': 900})
    pg = ctx.new_page(); errs = []; badreq = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('response', lambda r: r.status >= 400 and badreq.append((r.status, r.url)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    names = lambda: pg.locator('#exlist [data-act="g-pickex"] .t').all_inner_texts()
    subs = lambda: pg.locator('#exlist [data-act="g-pickex"] .small').all_inner_texts()

    # 2. groupes
    heads = [h.strip().capitalize() for h in pg.locator('#exlist .sec').all_inner_texts()]
    print('  groupes :', heads)
    check('groupe Avant-bras ajoute', 'Avant-bras' in heads, heads)
    allnames = names()
    check('les %d exercices (hors prises) sont dans la liste' % (len(EXD) - len(HIDDEN)), all(n in allnames for n in EXD if n not in HIDDEN), [n for n in EXD if n not in allnames and n not in HIDDEN][:5])
    check('les prises ne sont pas listees a part', not any(n in allnames for n in HIDDEN), [n for n in HIDDEN if n in allnames])
    check('« Tirage vertical » une seule fois, avec « 4 prises »', allnames.count('Tirage vertical') == 1 and '4 prises' in pg.inner_text('#exlist'))
    pg.fill('#exq', 'tirage vertical'); pg.wait_for_timeout(150)
    check('recherche « tirage vertical » : la famille + un bras', names() == ['Tirage vertical', 'Tirage vertical un bras'], names())
    pg.fill('#exq', 'corde'); pg.wait_for_timeout(150)
    check('recherche « corde » : la prise corde directement', 'Extension poulie corde' in names() and 'Extension poulie' not in names(), names())
    pg.fill('#exq', '')

    # 3. filtres
    pg.select_option('[data-ch="exmus"]', 'Fessiers'); pg.wait_for_timeout(150)
    s = subs()
    check('filtre Fessiers : %d exercices, tous a fessiers en principal' % len(s), len(s) >= 6 and all(x.startswith('Fessiers') or ', Fessiers' in x.split('·')[0] for x in s), s[:4])
    pg.select_option('[data-ch="exeq"]', 'Poulie'); pg.wait_for_timeout(150)
    n2 = names(); s = subs()
    print('  fessiers + poulie :', n2)
    check('filtre Fessiers + Poulie', n2 and all(x.endswith('· Poulie') for x in s) and 'Kickback fessier poulie' in n2, n2)
    pg.select_option('[data-ch="exmus"]', ''); pg.select_option('[data-ch="exeq"]', 'Machine guidée'); pg.wait_for_timeout(150)
    n3 = names()
    check('filtre Machine guidee : les exercices Smith', len(n3) == 6 and all('Smith' in x for x in n3), n3)
    pg.fill('#exq', 'developpe'); pg.wait_for_timeout(150)
    n4 = names()
    check('recherche « developpe » + Machine guidee', sorted(n4) == ['Développé couché Smith', 'Développé incliné Smith', 'Développé épaules Smith'], n4)
    pg.select_option('[data-ch="exeq"]', 'Kettlebell'); pg.wait_for_timeout(150)
    check('aucun resultat : message clair', 'Aucun exercice avec ces filtres' in pg.inner_text('#exlist'))
    pg.select_option('[data-ch="exeq"]', ''); pg.fill('#exq', 'curl concentre'); pg.wait_for_timeout(150)
    check('recherche sans accents : curl concentre', names() == ['Curl concentré'], names())
    pg.screenshot(path=os.path.join(SHOT, 't13_liste.png'))

    # 4. fiche d'un nouvel exercice (illustration ajoutee en 2026.10.14, pas de schema img2)
    pg.click('#exlist [data-act="g-pickex"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-exinfo"][data-name="Curl concentré"]'); pg.wait_for_timeout(300)
    sh = pg.locator('.sheet').last
    t = sh.inner_text().lower()
    check('fiche nouvelle : consignes', 'comment faire' in t and sh.locator('.exsteps li').count() == len(EXD['Curl concentré']['st']))
    check('fiche nouvelle : equipement et muscles', 'équipement' in t and 'haltères' in t and 'biceps' in t)
    check('fiche nouvelle : illustration depart + arrivee', sh.locator('#mov img').count() == 2 and pg.get_attribute('#mov', 'data-id') == 'concentration-curl')
    check('fiche nouvelle : pas de schema img2 (absent pour les nouveaux)', sh.locator('img.mmap').count() == 0)
    pg.wait_for_timeout(300)
    broken = pg.evaluate("[...document.querySelectorAll('.sheet img')].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)")
    check('fiche nouvelle : aucune image cassee', not broken, broken)
    pg.screenshot(path=os.path.join(SHOT, 't13_fiche_nouvelle.png'))
    pg.click('.sheet [data-act="close"]'); pg.wait_for_timeout(300)

    # fiche d'un exercice illustre
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.fill('#exq', 'Soulevé de terre'); pg.wait_for_timeout(150)
    pg.click('#exlist [data-act="g-pickex"][data-name="Soulevé de terre"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-exinfo"][data-name="Soulevé de terre"]'); pg.wait_for_timeout(600)
    sh = pg.locator('.sheet').last
    t = sh.inner_text()
    check('fiche illustree : illustration + schema', sh.locator('#mov img').count() >= 1 and sh.locator('img.mmap').count() == 1)
    check('soulevé de terre : ischio-jambiers en secondaire', 'Ischio-jambiers' in t and 'Lombaires' in t)
    check('fiche illustree : consignes', sh.locator('.exsteps li').count() >= 4)
    broken = pg.evaluate("[...document.querySelectorAll('.sheet img')].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.src)")
    check('aucune image cassee dans la fiche', not broken, broken)
    pg.screenshot(path=os.path.join(SHOT, 't13_fiche_illustree.png'), full_page=True)

    # 4. familles de prises dans la routine puis dans la seance
    pg.click('.sheet [data-act="close"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.fill('#exq', 'tirage vertical'); pg.wait_for_timeout(150)
    pg.click('#exlist [data-act="g-pickex"][data-name="Tirage vertical"]'); pg.wait_for_timeout(300)
    chips = pg.locator('[data-act="g-rgrip"]').all_inner_texts()
    check('routine : choix de prise Large / Serrée / Inversée / Neutre', chips == ['Large', 'Serrée', 'Inversée', 'Neutre'], chips)
    pg.click('[data-act="g-rgrip"][data-n="Tirage vertical prise serrée"]'); pg.wait_for_timeout(300)
    st = json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
    rn = [e['name'] for r in st['routines'] for e in r['exercises']]
    check('routine : la prise serree est enregistree', 'Tirage vertical prise serrée' in rn, rn)
    check('routine : bouton Serrée actif', pg.get_attribute('[data-act="g-rgrip"][data-n="Tirage vertical prise serrée"]', 'aria-pressed') == 'true')
    pg.click('[data-act="g-rstart"]'); pg.wait_for_timeout(500)
    check('seance : la prise de la routine est reprise', pg.get_attribute('[data-act="g-grip"][data-n="Tirage vertical prise serrée"]', 'aria-pressed') == 'true')
    pg.click('[data-act="g-grip"][data-n="Tirage vertical prise neutre"]'); pg.wait_for_timeout(300)
    st = json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
    an = [e['name'] for e in st['active']['exercises']]
    check('seance : passage en prise neutre', 'Tirage vertical prise neutre' in an, an)
    pg.screenshot(path=os.path.join(SHOT, 't13_prises.png'))

    # 6. les 175 fiches : illustration presente et chargee, en couleur puis en image simple
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(500)
    res = pg.evaluate('''async names=>{
      const out={sans:[],casse:[],un:[]};
      const load=()=>Promise.all([...document.querySelectorAll('.sheet img')].map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})));
      const bad=()=>[...document.querySelectorAll('.sheet img')].filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src'));
      const open=n=>{const b=document.createElement('button');b.dataset.act='g-exinfo';b.dataset.name=n;document.body.append(b);b.click();b.remove()};
      const click=q=>document.querySelector(q).click();
      for(const n of names){
        open(n);
        const m=document.querySelectorAll('#mov img');
        if(!m.length)out.sans.push(n);
        if(m.length==1)out.un.push(n);
        await load(); out.casse.push(...bad());
        click('#redbtn'); await load(); out.casse.push(...bad()); click('#redbtn');
        click('.sheet [data-act="close"]');
      }
      return out}''', list(EXD))
    print('  une seule position :', res['un'])
    check('les 175 exercices ont une illustration', not res['sans'], res['sans'][:5])
    check('aucune image cassee dans les 175 fiches (couleur et simple)', not res['casse'], res['casse'][:5])
    check('une seule position : Gainage, Gainage lateral, Flexion laterale', sorted(res['un']) == sorted(['Gainage', 'Gainage latéral', 'Flexion latérale haltère']), res['un'])
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    th = pg.evaluate('''async()=>{const im=[...document.querySelectorAll('#exlist img.thumb')];
      im.forEach(i=>i.loading='eager');
      await Promise.all(im.map(i=>i.complete?0:new Promise(r=>{i.onload=i.onerror=r})));
      return {n:im.length,ph:document.querySelectorAll('#exlist .thumb.ph').length,bad:im.filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src'))}}''')
    check('liste : %d vignettes, toutes chargees, aucune lettre a la place' % th['n'], th['n'] == len(EXD) - len(HIDDEN) and not th['bad'] and th['ph'] == 0, th)

    # 7. exercice perso sans illustration : vignette lettre et fiche propre
    pg.fill('#exq', 'Mon mouvement maison'); pg.wait_for_timeout(150)
    pg.click('[data-act="g-newex"]'); pg.wait_for_timeout(300)
    check('exercice perso : vignette lettre', pg.locator('.thumb.ph').filter(has_text='M').count() >= 1)
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(300)
    pg.fill('#exq', 'Mon mouvement maison'); pg.wait_for_timeout(150)
    check('exercice perso : vignette lettre dans la liste', pg.locator('#exlist [data-name="Mon mouvement maison"] .thumb.ph').count() == 1)
    pg.evaluate("(()=>{const b=document.createElement('button');b.dataset.act='g-exinfo';b.dataset.name='Mon mouvement maison';document.body.append(b);b.click();b.remove()})()"); pg.wait_for_timeout(300)
    sh = pg.locator('.sheet').last
    check('exercice perso : fiche « Pas d’illustration », aucune image', 'Pas d’illustration' in sh.inner_text() and sh.locator('img').count() == 0)
    pg.screenshot(path=os.path.join(SHOT, 't13_perso.png'))

    print('ERRS', errs)
    check('aucune erreur JavaScript', not errs, errs)
    check('aucune requete en erreur', not badreq, badreq[:5])
    b.close()

print('\n%d echec(s)' % len(fails) if fails else '\nTOUT EST OK')
