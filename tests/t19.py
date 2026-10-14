"""Test de bout en bout : Muscu, progression (2026.10.14-5). Seances fictives uniquement.

  1. records en direct : charge max, 1RM estime, repetitions a cette charge, volume ; un seul a la fois ;
     echauffement ignore ; premier enregistrement d'un exercice = pas de record ; banniere qui s'efface ;
     records gardes avec la seance ; un import ne declenche rien ;
  2. types de serie : choix par le numero, lettres É / E / D, sauves dans la seance, la routine, l'historique ;
     ancien format sans type = serie normale ; volume sans l'echauffement ;
  3. suggestion de charge : +palier, rester, rien sous le minimum ni au poids du corps ; pre-remplissage ;
     reglages (palier, fourchette, desactivation), refus d'une fourchette incoherente ;
  4. series par muscle sur 7 jours : principal 1, secondaire 0,5, echauffement et exercice inconnu ignores,
     tri, decimales, repere, carte repliable ;
  5. ecran allume : sans navigator.wakeLock, avec un faux wakeLock (demande, retour au premier plan,
     relache a la fin et a l'abandon, reglage coupe), demande refusee ; forme.html ne fait rien.

    python3 -m http.server 8765
    python3 tests/t19.py
"""
import datetime, json, re
from playwright.sync_api import sync_playwright

BASE = 'http://localhost:8765/'
TODAY = datetime.date.today()
D = lambda k: (TODAY - datetime.timedelta(days=k)).isoformat()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if not ok and extra != '' else ''))
    if not ok: fails.append(label)
clean = lambda t: re.sub(r'[  ]', ' ', t)
S_ = lambda kg, reps, t=None: dict(kg=kg, reps=reps, **({'t': t} if t else {}))
SESSIONS = [
    dict(id='s1', date=D(10), name='Jambes', dur=50, exercises=[
        dict(name='Squat', sets=[S_(140, 3, 'w'), S_(97.5, 5), S_(97.5, 5)])]),
    dict(id='s2', date=D(3), name='Haut', dur=45, exercises=[
        dict(name='Développé couché', sets=[S_(60, 12), S_(60, 12), S_(60, 13)])]),
    dict(id='s3', date=D(2), name='Bras', dur=40, exercises=[
        dict(name='Curl barre', sets=[S_(35, 8), S_(30, 11)]),
        dict(name='Pompes', sets=[S_(0, 15)])]),
    dict(id='s4', date=D(1), name='Divers', dur=30, exercises=[
        dict(name='Leg curl', sets=[S_(40, 10), S_(40, 11)]),
        dict(name='Leg extension', sets=[S_(20, 15, 'w')]),
        dict(name='Mon exo à moi', sets=[S_(10, 10)])]),
]
ROUT = [dict(id='r1', name='Test', exercises=[
    dict(name='Squat', sets=[S_('40', '10', 'w'), S_('100', '5'), S_('100', '5'), S_('95', '6')]),
    dict(name='Développé couché', sets=[S_('', ''), S_('', ''), S_('', '')]),
    dict(name='Curl barre', sets=[S_('30', '12')]),
    dict(name='Leg curl', sets=[S_('', '')]),
    dict(name='Pompes', sets=[S_('', '')]),
    dict(name='Hip thrust', sets=[S_('80', '10')]),
])]

FAKE_WL = """
window.__wl={req:0,rel:0,live:null,refuse:false};
Object.defineProperty(Navigator.prototype,'wakeLock',{configurable:true,get(){return {request(type){
  window.__wl.req++;
  if(window.__wl.refuse)return Promise.reject(new DOMException('refus','NotAllowedError'));
  const ls=[];const s={type,released:false,addEventListener(n,f){if(n==='release')ls.push(f)},
    release(){if(!s.released){s.released=true;window.__wl.rel++;if(window.__wl.live===s)window.__wl.live=null;ls.forEach(f=>f())}return Promise.resolve()}};
  window.__wl.live=s;return Promise.resolve(s);}}}});
window.__vis='visible';
Object.defineProperty(Document.prototype,'visibilityState',{configurable:true,get(){return window.__vis}});
Object.defineProperty(Document.prototype,'hidden',{configurable:true,get(){return window.__vis!=='visible'}});
"""
NO_WL = "Object.defineProperty(Navigator.prototype,'wakeLock',{configurable:true,get(){return undefined}});"

with sync_playwright() as pw:
    b = pw.chromium.launch()
    def page(init=None, file='index.html'):
        ctx = b.new_context(viewport={'width': 384, 'height': 860})
        if file == 'forme.html':   # forme.html ne declare pas de charset (la page de Claude l'ajoute)
            ctx.route('**/forme.html', lambda r: r.fulfill(response=r.fetch(), headers={'content-type': 'text/html; charset=utf-8'}))
        if init: ctx.add_init_script(init)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(BASE + file); pg.wait_for_timeout(300)
        return ctx, pg, errs
    def seed(pg, settings=None, **o):
        st0 = {'v2': 1}; st0.update(settings or {})
        pg.evaluate("s=>localStorage.setItem('forme.v1',JSON.stringify(s))", dict(o, settings=st0))
        pg.reload(); pg.wait_for_timeout(500)
    st = lambda pg: json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
    def gym(pg):
        pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(250)
    def card(pg, name):
        return pg.locator('#view .card.ex').filter(has=pg.locator('b', has_text=re.compile('^' + re.escape(name) + '$')))
    def setrow(pg, name, si, kg=None, reps=None):
        c = card(pg, name)
        if kg is not None: c.locator('[data-in="set"][data-f="kg"]').nth(si).fill(str(kg))
        if reps is not None: c.locator('[data-in="set"][data-f="reps"]').nth(si).fill(str(reps))
    def ok(pg, name, si):
        card(pg, name).locator('[data-act="g-check"]').nth(si).click(); pg.wait_for_timeout(120)
    def cancel(pg):   # le bouton est en bas de page, sous la barre de repos fixe : clic envoye directement
        pg.locator('[data-act="g-cancel"]').dispatch_event('click'); pg.wait_for_timeout(200)
        pg.locator('#layer .btn.danger').click()
    ban = lambda pg: clean(pg.inner_text('#prban')) if pg.locator('#prban').count() else ''

    # ---------- 1, 2, 3 : une seance a partir d'une routine ----------
    ctx, pg, errs = page(NO_WL)
    seed(pg, sessions=SESSIONS, routines=ROUT)
    gym(pg)
    # routine : type garde apres chargement (migRoutines), libelle « Échauff. »
    pg.click('[data-act="g-redit"][data-id="r1"]'); pg.wait_for_timeout(250)
    n0 = pg.locator('.rsets .n').first
    check('routine : série d’échauffement affichée', n0.inner_text().strip() == 'Échauff.', n0.inner_text())
    check('routine : séries normales numérotées sans l’échauffement',
          [x.strip() for x in pg.locator('.card.ex').first.locator('.rsets .n').all_inner_texts()] == ['Échauff.', 'Série 1', 'Série 2', 'Série 3'])
    # changer le type d'une serie de routine
    pg.locator('.card.ex').nth(2).locator('.rsets .n').first.click(); pg.wait_for_timeout(200)
    check('feuille des 4 types', pg.locator('[data-act="g-stype-ok"]').count() == 4)
    pg.click('[data-act="g-stype-ok"][data-t="d"]'); pg.wait_for_timeout(200)
    check('routine : drop set enregistré', st(pg)['routines'][0]['exercises'][2]['sets'][0].get('t') == 'd')
    pg.locator('.card.ex').nth(2).locator('.rsets .n').first.click(); pg.wait_for_timeout(200)
    pg.click('[data-act="g-stype-ok"][data-t=""]'); pg.wait_for_timeout(200)
    check('routine : retour en normale (pas de champ t)', 't' not in st(pg)['routines'][0]['exercises'][2]['sets'][0])
    # dupliquer garde les types
    pg.click('[data-act="g-rdup"]'); pg.wait_for_timeout(200)
    r2 = st(pg)['routines'][1]
    check('routine dupliquée : type gardé', r2['exercises'][0]['sets'][0].get('t') == 'w')
    pg.click('[data-act="g-rback"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-rstart"][data-id="r1"]'); pg.wait_for_timeout(400)
    a = st(pg)['active']
    check('séance : type repris de la routine', a['exercises'][0]['sets'][0].get('t') == 'w' and 't' not in a['exercises'][0]['sets'][1])
    labs = [x.strip() for x in card(pg, 'Squat').locator('.sets .n').all_inner_texts()]
    check('séance : É puis 1, 2, 3', labs == ['É', '1', '2', '3'], labs)

    # suggestions en haut des exercices (seance precedente)
    sug = lambda name: clean(card(pg, name).locator('button.sug').inner_text()) if card(pg, name).locator('button.sug').count() else ''
    s_dc = sug('Développé couché')
    check('suggestion +2,5 kg (toutes à 12 ou plus)', 'Suggestion' in s_dc and '62,5 kg' in s_dc and '+2,5' in s_dc and '10' in s_dc, s_dc)
    s_lc = sug('Leg curl')
    check('suggestion « reste » (10 à 11 reps)', 'reste à 40 kg' in s_lc and '12' in s_lc, s_lc)
    check('pas de suggestion sous 10 reps', sug('Curl barre') == '')
    check('pas de suggestion au poids du corps', sug('Pompes') == '')
    check('pas de suggestion sans historique', sug('Hip thrust') == '')
    check('suggestion jamais en rouge (couleur douce)',
          pg.evaluate("getComputedStyle(document.querySelector('button.sug')).color") != pg.evaluate("getComputedStyle(document.querySelector('#app')).getPropertyValue('--c-gym')"))
    # appui : pre-remplit seulement
    kg0 = [x for x in card(pg, 'Développé couché').locator('[data-in="set"][data-f="kg"]').evaluate_all('e=>e.map(x=>x.value)')]
    card(pg, 'Développé couché').locator('button.sug').click(); pg.wait_for_timeout(200)
    kg1 = card(pg, 'Développé couché').locator('[data-in="set"][data-f="kg"]').evaluate_all('e=>e.map(x=>x.value)')
    a = st(pg)['active']
    check('appui sur la suggestion : charge pré-remplie', kg0 == ['', '', ''] and kg1 == ['62.5'] * 3, (kg0, kg1))
    check('appui sur la suggestion : rien de validé', not any(s['done'] for s in a['exercises'][1]['sets']))

    # records
    ok(pg, 'Squat', 0)
    check('échauffement : pas de record', ban(pg) == '')
    ok(pg, 'Squat', 1)
    t = ban(pg)
    check('record de charge (échauffement à 140 ignoré)', t == '🏆 Record ! Squat 100 kg × 5 (avant : 97,5 × 5)', t)
    check('bannière sous la série, ne bloque rien',
          pg.evaluate("getComputedStyle(document.querySelector('#prban')).pointerEvents") == 'none'
          and pg.evaluate("document.querySelector('#prban').previousElementSibling.querySelector('[data-act=\"g-check\"]')!==null"))
    # la saisie continue pendant la banniere
    setrow(pg, 'Squat', 2, 100, 5)
    ok(pg, 'Squat', 2)
    check('même série refaite : pas de record (séance en cours comptée)', ban(pg) == '', ban(pg))
    ok(pg, 'Squat', 3)
    t = ban(pg)
    check('record de volume (95 × 6 = 570)', t.startswith('🏆 Record de volume ! Squat 95 × 6 = 570 kg (avant : 500)'), t)
    pg.wait_for_timeout(5400)
    check('la bannière s’efface d’elle-même', pg.locator('#prban').count() == 0)
    ok(pg, 'Curl barre', 0)
    t = ban(pg)
    check('record de répétitions à la même charge (30 × 12, avant 30 × 11)', t == '🏆 Record ! Curl barre 30 kg × 12 (avant : 30 × 11)', t)
    setrow(pg, 'Leg curl', 0, 45, 9)
    ok(pg, 'Leg curl', 0)
    t = ban(pg)
    check('record de charge prioritaire sur les autres', t.startswith('🏆 Record ! Leg curl 45 kg × 9'), t)
    ok(pg, 'Hip thrust', 0)
    check('premier enregistrement d’un exercice : pas de record', ban(pg) == '', ban(pg))
    # 1RM : meilleur 100 x 5 = 116,7 ; 92,5 x 10 = 123,3 sans battre la charge (100) ; aucune serie a 92,5
    pg.click('[data-act="g-addset"][data-e="0"]'); pg.wait_for_timeout(150)
    setrow(pg, 'Squat', 4, 92.5, 10)
    ok(pg, 'Squat', 4)
    t = ban(pg)
    check('record de 1RM estimé', t.startswith('🏆 Record de 1RM estimé ! Squat 123,3 kg (avant : 116,7)'), t)
    # decocher retire le record
    ok(pg, 'Squat', 4)
    check('décocher : record retiré', 'pr' not in st(pg)['active']['exercises'][0]['sets'][4])
    ok(pg, 'Squat', 4)

    # types en seance : E (echec)
    card(pg, 'Squat').locator('.sets .n').nth(3).click(); pg.wait_for_timeout(200)
    pg.click('[data-act="g-stype-ok"][data-t="f"]'); pg.wait_for_timeout(200)
    labs = [x.strip() for x in card(pg, 'Squat').locator('.sets .n').all_inner_texts()]
    check('séance : échec marqué E', labs == ['É', '1', '2', 'E', '3'], labs)
    check('E et D en couleur douce, É en gris',
          pg.evaluate("(()=>{const n=[...document.querySelectorAll('.sets .n')];return getComputedStyle(n[0]).opacity<1})()"))

    # suggestion en direct (Developpe couche 62,5 x 10, 62,5 x 11)
    setrow(pg, 'Développé couché', 0, None, 10); ok(pg, 'Développé couché', 0)
    setrow(pg, 'Développé couché', 1, None, 11); ok(pg, 'Développé couché', 1)
    live = clean(card(pg, 'Développé couché').locator('div.sug').text_content())
    check('suggestion en direct : reste et vise 12', 'reste à 62,5 kg' in live and '12 répétitions' in live, live)
    setrow(pg, 'Développé couché', 2, None, 8); ok(pg, 'Développé couché', 2)
    check('suggestion en direct : rien si une série < 10', card(pg, 'Développé couché').locator('div.sug').count() == 0)
    pg.screenshot(path='/tmp/t19_seance.png', full_page=True)
    over = pg.evaluate("[...document.querySelectorAll('.sug')].filter(x=>x.scrollWidth>x.clientWidth+1).map(x=>x.textContent)")
    check('suggestions sur une seule ligne à 384 px', not over and pg.locator('.sug').count() >= 3, over)
    print('     marge restante (px) :', pg.evaluate("[...document.querySelectorAll('.sug')].map(x=>{const s=x.querySelector('[aria-hidden]')||x;const r=document.createRange();r.selectNodeContents(s);return Math.round(x.clientWidth-24-r.getBoundingClientRect().width)})"))

    # fin de seance : types, records et volume
    pg.click('[data-act="g-finish"]'); pg.wait_for_timeout(200)
    pg.locator('#layer .btn', has_text='Terminer').click(); pg.wait_for_timeout(400)
    fin = clean(pg.inner_text('#layer'))
    check('fin : records battus listés', 'records battus' in fin.lower() and 'Squat 100 kg × 5' in fin, fin[:300])
    o = st(pg); ses = next(s for s in o['sessions'] if s['date'] == D(0))
    sq = ses['exercises'][0]['sets']
    check('séance enregistrée : types gardés', sq[0].get('t') == 'w' and sq[3].get('t') == 'f' and 't' not in sq[1])
    check('séance enregistrée : liste des records', [r['k'] for r in ses.get('prs', [])][:2] == ['kg', 'vol'], ses.get('prs'))
    vol = sum(s['kg'] * s['reps'] for e in ses['exercises'] for s in e['sets'] if s.get('t') != 'w')
    m = re.search(r'Volume\s*([\d  ]+)\s*kg', fin)
    check('volume sans l’échauffement', m and int(re.sub(r'\D', '', m.group(1))) == int(vol + .5), (m and m.group(1), vol))
    pg.click('#layer [data-act="close"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-view"][data-id="%s"]' % ses['id']); pg.wait_for_timeout(250)
    det = clean(pg.inner_text('#layer'))
    check('historique : É et E affichés, records rappelés', 'É · 40 × 10' in det and 'E · 95 × 6' in det and '🏆' in det, det[-500:])
    pg.click('[data-act="g-redo"]'); pg.wait_for_timeout(300)
    check('Refaire : types repris', st(pg)['active']['exercises'][0]['sets'][0].get('t') == 'w')
    cancel(pg); pg.wait_for_timeout(200)

    # un import (seance plus forte ajoutee) ne declenche rien
    o = st(pg); o['sessions'].append(dict(id='imp', date=D(5), name='Import', dur=30, exercises=[dict(name='Squat', sets=[S_(200, 5)])]))
    seed(pg, **o); gym(pg)
    check('import : aucune bannière', pg.locator('#prban').count() == 0)

    # ---------- reglages ----------
    def settings(pg):
        pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    settings(pg)
    check('réglages Muscu présents', all(pg.locator(x).count() == 1 for x in ['#gpc', '#gsug', '#gslo', '#gshi']))
    check('réglage écran allumé (téléphone) + batterie', pg.locator('#gwl').count() == 1 and 'batterie' in pg.inner_text('#layer'))
    pg.fill('#gslo', '12'); pg.fill('#gshi', '10'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(200)
    check('fourchette incohérente refusée', pg.locator('#layer .sheet').count() == 1 and st(pg)['settings'].get('sugMax', 12) == 12)
    pg.fill('#gslo', '8'); pg.fill('#gshi', '11'); pg.fill('#gpc', '5'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    g = st(pg)['settings']
    check('réglages enregistrés', g['sugMin'] == 8 and g['sugMax'] == 11 and g['pasCharge'] == 5, g)
    pg.click('[data-act="g-rstart"][data-id="r1"]'); pg.wait_for_timeout(400)
    s_lc = sug('Leg curl')
    check('nouveaux réglages : 45 × 9 (>= 8) -> reste à 45 kg, vise 11', 'reste à 45 kg' in s_lc and '11' in s_lc, s_lc)
    s_dc = sug('Développé couché')
    check('nouveau réglage : 62,5 × 10/11/8 (>= 8) -> reste à 62,5 kg', 'reste à 62,5 kg' in s_dc, s_dc)
    settings(pg); pg.uncheck('#gsug'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    check('suggestions coupées : plus rien', pg.locator('.sug').count() == 0)
    settings(pg); pg.check('#gsug'); pg.fill('#gslo', '10'); pg.fill('#gshi', '12'); pg.fill('#gpc', '2,5'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    cancel(pg); pg.wait_for_timeout(200)
    check('aucune erreur (séance, records, types, suggestions)', not errs, errs)
    ctx.close()

    # ---------- 4 : series par muscle ----------
    ctx, pg, errs = page(NO_WL)
    seed(pg, sessions=SESSIONS)
    gym(pg); pg.click('[data-act="g-tab"][data-t="progress"]'); pg.wait_for_timeout(300)
    txt = clean(pg.inner_text('#view'))
    check('carte « Séries par muscle (7 jours) »', 'Séries par muscle (7 jours)' in txt)
    rows = [(clean(r.locator('span').inner_text()), clean(r.locator('b').inner_text())) for r in pg.locator('.musr').all()]
    exp = {'Pectoraux': '4', 'Biceps': '2', 'Épaules': '2', 'Ischio-jambiers': '2', 'Triceps': '2', 'Avant-bras': '1', 'Mollets': '1', 'Abdominaux': '0,5'}
    check('séries par muscle : 1 principal, 0,5 secondaire, 7 jours', dict(rows) == exp, rows)
    check('tri du plus au moins travaillé', [r[0] for r in rows] == ['Pectoraux', 'Biceps', 'Épaules', 'Ischio-jambiers', 'Triceps', 'Avant-bras', 'Mollets', 'Abdominaux'], rows)
    check('échauffement et séance de plus de 7 jours ignorés (pas de Quadriceps)', 'Quadriceps' not in dict(rows))
    check('repère courant affiché', 'Repère courant : 10 à 20 séries par muscle et par semaine' in txt)
    check('noms cohérents avec les filtres', all(m in ['Pectoraux', 'Grand dorsal', 'Milieu du dos', 'Lombaires', 'Trapèzes', 'Épaules', 'Biceps', 'Triceps', 'Avant-bras', 'Quadriceps', 'Ischio-jambiers', 'Fessiers', 'Mollets', 'Adducteurs', 'Abducteurs', 'Abdominaux'] for m, _ in rows))
    check('progression : exercice à échauffement seul absent de la liste', 'Leg extension' not in txt)
    pg.screenshot(path='/tmp/t19_muscles.png', full_page=True)
    pg.click('[data-act="g-mus"]'); pg.wait_for_timeout(200)
    check('carte repliable', pg.locator('.musr').count() == 0 and pg.get_attribute('[data-act="g-mus"]', 'aria-expanded') == 'false')
    pg.reload(); pg.wait_for_timeout(400); gym(pg); pg.click('[data-act="g-tab"][data-t="progress"]'); pg.wait_for_timeout(200)
    check('repli gardé après rechargement', pg.locator('.musr').count() == 0)
    check('pas de données synchronisées pour le repli', 'gMusClosed' not in json.dumps(st(pg).get('settings', {})))
    pg.click('[data-act="g-mus"]'); pg.wait_for_timeout(200)
    check('aucune erreur (séries par muscle)', not errs, errs)
    ctx.close()

    # ---------- 5 : ecran allume ----------
    # a) sans wakeLock : rien ne casse
    ctx, pg, errs = page(NO_WL)
    seed(pg, sessions=SESSIONS)
    gym(pg); pg.click('text=Nouvelle séance'); pg.wait_for_timeout(1300)
    pg.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    check('sans wakeLock : séance ouverte, aucune erreur, aucun message', pg.locator('#view .field [data-in="sname"]').count() == 1 and not errs, errs)
    ctx.close()
    # b) faux wakeLock
    ctx, pg, errs = page(FAKE_WL)
    seed(pg, sessions=SESSIONS)
    gym(pg)
    pg.wait_for_timeout(1200)
    check('pas de verrou sans séance', pg.evaluate('__wl.req') == 0)
    pg.click('text=Nouvelle séance'); pg.wait_for_timeout(1300)
    check('séance en cours : verrou demandé une fois', pg.evaluate('__wl.req') == 1 and pg.evaluate('!!__wl.live'))
    pg.wait_for_timeout(1500)
    check('pas de nouvelle demande tant qu’il tient', pg.evaluate('__wl.req') == 1)
    # arriere-plan : le navigateur retire le verrou
    pg.evaluate("__vis='hidden';__wl.live&&__wl.live.release();document.dispatchEvent(new Event('visibilitychange'))")
    pg.wait_for_timeout(1300)
    check('en arrière-plan : pas de demande', pg.evaluate('__wl.req') == 1)
    pg.evaluate("__vis='visible';document.dispatchEvent(new Event('visibilitychange'))"); pg.wait_for_timeout(300)
    check('retour au premier plan : redemandé', pg.evaluate('__wl.req') == 2 and pg.evaluate('!!__wl.live'))
    cancel(pg); pg.wait_for_timeout(1300)
    check('abandon : verrou relâché', pg.evaluate('!__wl.live'))
    pg.click('text=Nouvelle séance'); pg.wait_for_timeout(1300)
    check('nouvelle séance : redemandé', pg.evaluate('!!__wl.live'))
    pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(200); pg.locator('[data-act="g-pickex"]').first.click(); pg.wait_for_timeout(300)
    pg.locator('[data-in="set"][data-f="kg"]').first.fill('20'); pg.locator('[data-in="set"][data-f="reps"]').first.fill('10')
    pg.locator('[data-act="g-check"]').first.click(); pg.wait_for_timeout(150)
    pg.click('[data-act="g-finish"]'); pg.wait_for_timeout(200); pg.locator('#layer .btn', has_text='Terminer').click(); pg.wait_for_timeout(1300)
    check('fin de séance : verrou relâché', pg.evaluate('!__wl.live'))
    pg.click('#layer [data-act="close"]'); pg.wait_for_timeout(200)
    # reglage coupe
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(200); pg.uncheck('#gwl'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(200)
    n = pg.evaluate('__wl.req')
    pg.click('text=Nouvelle séance'); pg.wait_for_timeout(1300)
    check('réglage coupé : pas de demande', pg.evaluate('__wl.req') == n and pg.evaluate('!__wl.live'))
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(200); pg.check('#gwl'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(1300)
    check('réglage remis : demandé', pg.evaluate('!!__wl.live'))
    check('aucune erreur (faux wakeLock)', not errs, errs)
    ctx.close()
    # c) demande refusee
    ctx, pg, errs = page(FAKE_WL + "window.__wl.refuse=true;")
    seed(pg, sessions=SESSIONS)
    gym(pg); pg.click('text=Nouvelle séance'); pg.wait_for_timeout(2400)
    check('refus : une seule tentative, rien ne casse', pg.evaluate('__wl.req') == 1 and not errs and pg.locator('.toast:visible').count() == 0, (pg.evaluate('__wl.req'), errs))
    ctx.close()
    # d) forme.html : rien de special
    ctx, pg, errs = page(FAKE_WL, 'forme.html')
    seed(pg, sessions=SESSIONS)
    gym(pg); pg.click('text=Nouvelle séance'); pg.wait_for_timeout(1300)
    check('forme.html : aucun verrou demandé', pg.evaluate('__wl.req') == 0)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(200)
    check('forme.html : pas de réglage écran allumé, réglages Muscu présents', pg.locator('#gwl').count() == 0 and pg.locator('#gsug').count() == 1)
    pg.locator('#layer .scrim').click(position={'x': 10, 'y': 10}); pg.wait_for_timeout(300)
    cancel(pg); pg.wait_for_timeout(200)
    pg.click('[data-act="g-tab"][data-t="progress"]'); pg.wait_for_timeout(200)
    check('forme.html : carte séries par muscle', pg.locator('.musr').count() == 8)
    check('aucune erreur (forme.html)', not errs, errs)
    ctx.close()
    b.close()

print('\n' + ('TOUT EST OK' if not fails else '%d ECHEC(S) : %s' % (len(fails), fails)))
