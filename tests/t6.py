"""Test de bout en bout : routines, une ligne par serie (2026.10.14-2).

  1. ajout d'un exercice : « Combien de series ? » (3 par defaut) ; Annuler = rien n'est ajoute ;
  2. une ligne par serie, poids et repetitions modifiables chacun de son cote, sans redessiner
     l'ecran pendant la saisie ; resume lisible quand les series different ;
  3. ajouter une serie (reprend la derniere), supprimer une serie (au moins une reste) ;
  4. dupliquer : copie profonde (changer la copie ne touche pas l'original) ;
  5. quitter, recharger la page, revenir : tout est garde ;
  6. demarrer la seance : chaque serie pre-remplie avec SON poids et SES repetitions ;
  7. migration de l'ancien format {name, sets:3, kg, reps} : au chargement, a l'import d'une
     sauvegarde et a la synchronisation (compte simule), sans perte.

    python3 -m http.server 8765
    python3 tests/t6.py
"""
import json, os, tempfile
from playwright.sync_api import sync_playwright

URL = 'http://localhost:8765/index.html'
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra != '' and not ok else ''))
    if not ok: fails.append(label)
st = lambda pg: json.loads(pg.evaluate("localStorage.getItem('forme.v1')") or '{}')
sets = lambda e: [(s['kg'], s['reps']) for s in e['sets']]

# routine a l'ancien format, telle qu'enregistree par les versions d'avant 2026.10.14-2
OLD = [{'id': 'old1', 'name': 'Ancienne routine', 'exercises': [
    {'name': 'Squat', 'sets': 3, 'kg': '60', 'reps': '8'},
    {'name': 'Leg curl', 'sets': 0, 'kg': '', 'reps': ''},
    {'name': 'Dips'},
    {'name': 'Développé couché', 'sets': 5, 'kg': 42.5, 'reps': 10},
]}]
OLD_WANT = {'Squat': [('60', '8')] * 3, 'Leg curl': [('', '')] * 3, 'Dips': [('', '')] * 3,
            'Développé couché': [('42.5', '10')] * 5}
def migrated_ok(routines):
    r = next((x for x in routines if x['id'] == 'old1'), None)
    if not r: return False, 'routine absente'
    got = {e['name']: sets(e) for e in r['exercises']}
    clean = all(set(e) == {'name', 'sets'} and all(set(s) == {'kg', 'reps'} for s in e['sets']) for e in r['exercises'])
    return got == OLD_WANT and clean and r['name'] == 'Ancienne routine' and [e['name'] for e in r['exercises']] == list(OLD_WANT), got

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- parcours normal ----------
    ctx = b.new_context(viewport={'width': 412, 'height': 900}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-rnew"]'); pg.wait_for_timeout(300)
    pg.fill('[data-in="rname"]', 'Haut du corps')
    def pick(name):
        pg.click('[data-act="g-addex"]'); pg.wait_for_timeout(250)
        pg.fill('#exq', name); pg.wait_for_timeout(200)
        pg.click('#exlist [data-act="g-pickex"][data-name="%s"]' % name); pg.wait_for_timeout(250)

    # 1. nombre de series, Annuler
    pick('Développé couché')
    sh = pg.locator('.sheet').last
    check('feuille « Combien de séries ? »', 'Combien de séries ?' in sh.inner_text())
    check('pastilles 1 à 8, 3 par défaut', pg.locator('[data-act="g-rcnt"]').count() == 8 and pg.get_attribute('[data-act="g-rcnt"][aria-pressed="true"]', 'data-n') == '3')
    pg.click('.sheet [data-act="close"]'); pg.wait_for_timeout(250)
    r = st(pg)['routines'][-1]
    check('Annuler : l\'exercice n\'est pas ajouté', r['exercises'] == [] and pg.locator('[data-act="g-rexmenu"]').count() == 0, r['exercises'])
    pick('Développé couché')
    pg.click('[data-act="g-rcnt"][data-n="5"]'); pg.click('[data-act="g-rcnt"][data-n="3"]'); pg.wait_for_timeout(100)
    check('une seule pastille choisie', pg.locator('[data-act="g-rcnt"][aria-pressed="true"]').count() == 1)
    pg.click('[data-act="g-rcok"]'); pg.wait_for_timeout(300)
    rows = lambda i: pg.locator('[data-in="rset"][data-f="kg"][data-i="%d"]' % i).count()
    check('Valider : 3 lignes Série 1, Série 2, Série 3', rows(0) == 3 and all(('Série %d' % k) in pg.inner_text('#view') for k in (1, 2, 3)))
    check('enregistré au nouveau format', st(pg)['routines'][-1]['exercises'] == [{'name': 'Développé couché', 'sets': [{'kg': '', 'reps': ''}] * 3}], st(pg)['routines'][-1]['exercises'])

    # 2. saisie serie par serie, sans redessiner
    pg.evaluate("document.querySelector('#view').dataset.mark='1'")
    vals = [('60', '10'), ('70', '8'), ('75', '6')]
    for k, (kg, rp) in enumerate(vals):
        pg.fill('[data-in="rset"][data-i="0"][data-s="%d"][data-f="kg"]' % k, kg)
        pg.fill('[data-in="rset"][data-i="0"][data-s="%d"][data-f="reps"]' % k, rp)
    pg.wait_for_timeout(200)
    check('valeurs différentes par série, enregistrées', sets(st(pg)['routines'][-1]['exercises'][0]) == vals, sets(st(pg)['routines'][-1]['exercises'][0]))
    focus = pg.evaluate("(()=>{const a=document.activeElement;return a&&a.isConnected?a.dataset.s+a.dataset.f:''})()")
    check('saisie sans redessiner l\'écran (le champ garde la main)', focus == '2reps', focus)
    check('résumé « 3 séries · 60–75 kg · 6–10 reps »', pg.inner_text('#rsum0') == '3 séries · 60–75 kg · 6–10 reps', pg.inner_text('#rsum0'))
    check('clavier : décimal pour le poids, numérique pour les répétitions',
          pg.get_attribute('[data-in="rset"][data-s="0"][data-f="kg"]', 'inputmode') == 'decimal' and pg.get_attribute('[data-in="rset"][data-s="0"][data-f="reps"]', 'inputmode') == 'numeric')
    h = pg.evaluate("[...document.querySelectorAll('#view .rsets .rin,#view .rsets .rstep,#view [data-act=\"g-raddset\"]')].map(x=>x.getBoundingClientRect().height)")
    check('cibles tactiles d\'au moins 44 px', min(h) >= 44, min(h))
    pg.screenshot(path=os.path.join(tempfile.gettempdir(), 't6_series.png'))

    # 3. ajouter, supprimer
    pg.click('[data-act="g-raddset"][data-i="0"]'); pg.wait_for_timeout(250)
    e0 = st(pg)['routines'][-1]['exercises'][0]
    check('ajouter : la 4e série reprend 75 × 6', sets(e0) == vals + [('75', '6')], sets(e0))
    pg.fill('[data-in="rset"][data-i="0"][data-s="3"][data-f="kg"]', '77,5'); pg.wait_for_timeout(100)
    pg.click('[data-act="g-rdelset"][data-i="0"][data-s="1"]'); pg.wait_for_timeout(250)
    e0 = st(pg)['routines'][-1]['exercises'][0]
    check('supprimer la série 2 : les autres gardent leurs valeurs', sets(e0) == [('60', '10'), ('75', '6'), ('77,5', '6')], sets(e0))
    check('écran à jour après suppression', [pg.input_value('[data-in="rset"][data-i="0"][data-s="%d"][data-f="kg"]' % k) for k in range(3)] == ['60', '75', '77,5'])
    for _ in range(2):
        pg.click('[data-act="g-rdelset"][data-i="0"][data-s="0"]'); pg.wait_for_timeout(200)
    check('dernière série : bouton supprimer désactivé', pg.is_disabled('[data-act="g-rdelset"][data-i="0"][data-s="0"]'))
    pg.evaluate("document.querySelector('[data-act=\"g-rdelset\"][data-i=\"0\"][data-s=\"0\"]').removeAttribute('disabled')")
    pg.click('[data-act="g-rdelset"][data-i="0"][data-s="0"]'); pg.wait_for_timeout(200)
    e0 = st(pg)['routines'][-1]['exercises'][0]
    check('au moins une série reste', sets(e0) == [('77,5', '6')], sets(e0))
    for k in range(2):
        pg.click('[data-act="g-raddset"][data-i="0"]'); pg.wait_for_timeout(200)
    for k, (kg, rp) in enumerate(vals):
        pg.fill('[data-in="rset"][data-i="0"][data-s="%d"][data-f="kg"]' % k, kg)
        pg.fill('[data-in="rset"][data-i="0"][data-s="%d"][data-f="reps"]' % k, rp)
    pick('Tirage vertical')
    pg.click('[data-act="g-rcnt"][data-n="2"]'); pg.click('[data-act="g-rcok"]'); pg.wait_for_timeout(300)
    for k, (kg, rp) in enumerate([('50', '12'), ('55', '10')]):
        pg.fill('[data-in="rset"][data-i="1"][data-s="%d"][data-f="kg"]' % k, kg)
        pg.fill('[data-in="rset"][data-i="1"][data-s="%d"][data-f="reps"]' % k, rp)
    pg.wait_for_timeout(200)
    r = st(pg)['routines'][-1]; rid = r['id']
    WANT = {'Développé couché': vals, 'Tirage vertical': [('50', '12'), ('55', '10')]}
    check('deux exercices, 3 et 2 séries', {e['name']: sets(e) for e in r['exercises']} == WANT, r['exercises'])
    check('résumé identique : « 2 séries · 50–55 kg · 10–12 reps »', pg.inner_text('#rsum1') == '2 séries · 50–55 kg · 10–12 reps', pg.inner_text('#rsum1'))
    pg.click('[data-act="g-raddset"][data-i="1"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="g-rdelset"][data-i="1"][data-s="2"]'); pg.wait_for_timeout(200)

    # changer de prise : les series restent
    pg.click('[data-act="g-rgrip"][data-n="Tirage vertical prise serrée"]'); pg.wait_for_timeout(250)
    r = st(pg)['routines'][-1]
    check('changer de prise : séries gardées', r['exercises'][1]['name'] == 'Tirage vertical prise serrée' and sets(r['exercises'][1]) == WANT['Tirage vertical'], r['exercises'][1])
    pg.click('[data-act="g-rgrip"][data-n="Tirage vertical"]'); pg.wait_for_timeout(250)

    # 4. dupliquer
    pg.click('[data-act="g-rdup"]'); pg.wait_for_timeout(300)
    pg.fill('[data-in="rset"][data-i="0"][data-s="0"][data-f="kg"]', '99'); pg.wait_for_timeout(150)
    rs = st(pg)['routines']; orig = next(x for x in rs if x['id'] == rid); copy = rs[-1]
    check('dupliquer : la copie change, pas l\'original', copy['id'] != rid and copy['exercises'][0]['sets'][0]['kg'] == '99' and sets(orig['exercises'][0]) == vals, (sets(orig['exercises'][0]), copy['exercises'][0]['sets'][0]))
    pg.click('[data-act="g-rdel"]'); pg.wait_for_timeout(200); pg.click('.sheet [data-act="confirm-ok"]'); pg.wait_for_timeout(250)

    # 5. quitter, recharger, revenir
    pg.click('.tab[data-t="weight"]'); pg.wait_for_timeout(200)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    lst = pg.inner_text('#view')
    check('liste : « 2 exercices · 5 séries »', '2 exercices · 5 séries' in lst, lst[:300])
    pg.click('[data-act="g-redit"][data-id="%s"]' % rid); pg.wait_for_timeout(300)
    got = [(pg.input_value('[data-in="rset"][data-i="0"][data-s="%d"][data-f="kg"]' % k), pg.input_value('[data-in="rset"][data-i="0"][data-s="%d"][data-f="reps"]' % k)) for k in range(3)]
    check('après rechargement : chaque série a gardé ses valeurs', got == vals and rows(1) == 2, got)

    # 6. demarrer
    pg.click('[data-act="g-rstart"]'); pg.wait_for_timeout(500)
    sv = lambda e, s, f: pg.input_value('[data-in="set"][data-e="%d"][data-s="%d"][data-f="%s"]' % (e, s, f))
    got = [[(sv(e, s, 'kg'), sv(e, s, 'reps')) for s in range(n)] for e, n in ((0, 3), (1, 2))]
    check('séance : chaque série pré-remplie avec SA valeur', got == [vals, WANT['Tirage vertical']], got)
    check('séance : 3 + 2 séries', pg.locator('[data-act="g-check"][data-e="0"]').count() == 3 and pg.locator('[data-act="g-check"][data-e="1"]').count() == 2)
    act = st(pg)['active']
    check('séance : format inchangé {kg, reps, done}', all(set(s) == {'kg', 'reps', 'done'} and s['done'] is False for e in act['exercises'] for s in e['sets']))
    pg.screenshot(path=os.path.join(tempfile.gettempdir(), 't6_seance.png'))
    check('aucune erreur JavaScript (parcours)', not errs, errs)
    ctx.close()

    # ---------- migration au chargement ----------
    ctx = b.new_context(viewport={'width': 412, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(300)
    pg.evaluate("r=>localStorage.setItem('forme.v1',JSON.stringify({routines:r,sessions:[],exercises:[]}))", OLD)
    pg.reload(); pg.wait_for_timeout(500)
    ok, got = migrated_ok(st(pg)['routines'])
    check('chargement : ancienne routine convertie sans perte', ok, got)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-redit"][data-id="old1"]'); pg.wait_for_timeout(300)
    check('chargement : 3 lignes à 60 × 8 pour le squat', [pg.input_value('[data-in="rset"][data-i="0"][data-s="%d"][data-f="kg"]' % k) for k in range(3)] == ['60'] * 3 and rows(0) == 3)
    pg.click('[data-act="g-rstart"]'); pg.wait_for_timeout(400)
    check('chargement : séance pré-remplie 60 × 8 et 42.5 × 10', sv(0, 2, 'kg') == '60' and sv(0, 2, 'reps') == '8' and sv(3, 4, 'kg') == '42.5' and sv(3, 4, 'reps') == '10')
    pg.reload(); pg.wait_for_timeout(400)
    ok, got = migrated_ok(st(pg)['routines'])
    check('chargement : conversion stable au rechargement suivant', ok, got)
    check('aucune erreur JavaScript (chargement)', not errs, errs)
    ctx.close()

    # ---------- migration a l'import d'une sauvegarde ----------
    ctx = b.new_context(viewport={'width': 412, 'height': 900}); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(400)
    f = os.path.join(tempfile.gettempdir(), 't6_sauvegarde_ancienne.json')
    json.dump({'app': 'forme', 'v': 1, 'date': '2026-10-01', 'data': {'routines': OLD, 'sessions': [], 'exercises': []}}, open(f, 'w', encoding='utf-8'), ensure_ascii=False)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(300)
    pg.set_input_files('[data-ch="imp"]', f); pg.wait_for_timeout(300)
    pg.click('.sheet [data-act="confirm-ok"]'); pg.wait_for_timeout(400)
    ok, got = migrated_ok(st(pg)['routines'])
    check('import : ancienne sauvegarde convertie sans perte', ok, got)
    pg.click('.tab[data-t="gym"]'); pg.wait_for_timeout(300)
    pg.click('[data-act="g-redit"][data-id="old1"]'); pg.wait_for_timeout(300)
    check('import : l\'éditeur montre 5 séries à 42.5 × 10', rows(3) == 5 and pg.input_value('[data-in="rset"][data-i="3"][data-s="4"][data-f="kg"]') == '42.5')
    check('aucune erreur JavaScript (import)', not errs, errs)
    os.remove(f); ctx.close()

    # ---------- migration a la synchronisation (compte simule) ----------
    FAKE = """(()=>{const OLD=%s;window.__sent=[];
      const coll={get:async()=>({docs:[{id:'routines',data:()=>({t:9e12,v:JSON.parse(JSON.stringify(OLD))})}]}),
                  doc:id=>({set:async x=>{window.__sent.push([id,JSON.parse(JSON.stringify(x))])}})};
      window.claude={use:async k=>k==='db'?{collection:()=>coll}:k==='user'?{id:async()=>'u-test'}:null};})()""" % json.dumps(OLD)
    ctx = b.new_context(viewport={'width': 412, 'height': 900}); ctx.add_init_script(FAKE); pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL); pg.wait_for_timeout(1500)
    ok, got = migrated_ok(st(pg)['routines'])
    check('synchro : routine reçue à l\'ancien format convertie', ok, got)
    sent = [x for k, x in pg.evaluate('window.__sent') if k == 'routines']
    ok2, got2 = migrated_ok(sent[-1]['v']) if sent else (False, 'rien renvoyé')
    check('synchro : la version convertie est renvoyée au compte', ok2, got2)
    check('aucune erreur JavaScript (synchro)', not errs, errs)
    ctx.close()
    b.close()

print('\n%d echec(s) : %s' % (len(fails), fails) if fails else '\nTOUT EST OK')
