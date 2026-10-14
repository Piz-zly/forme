"""Test de bout en bout : ameliorations du Repas (2026.10.14-4). Donnees fictives uniquement.

  1. calories rapides (Manuel) : raccourcis, nom facultatif « Ajout rapide », favori seulement avec un nom ;
  2. copier un repas / une journee (28 derniers jours seulement), nouveaux identifiants ;
  3. repas types : enregistrer, retrouver dans Favoris, ajouter en un geste, supprimer ;
  4. « Souvent a ce repas » : 2 fois au moins sur 60 jours, 4 au plus, masque pendant une recherche ;
  5. fiche d'un aliment : source ; corriger les valeurs (ajouts futurs, rechargement, retablir) ; cru / cuit ;
  6. recette perso : portions, « Calculer les valeurs » ;
  7. Semaine : planning, ✓ vers le journal, liste de courses additionnee par rayon, cases, ajouts, frigo ;
  8. frigo : « Mon frigo », « Avec mon frigo », pastilles, sel/poivre/huile toujours presents ;
  9. Bilan : serie qui pardonne, aujourd'hui non note ne casse pas, barres, calendrier, toucher un jour ;
 10. synchro des nouvelles tranches (compte simule) : envoi et reception, corrections appliquees.

    python3 -m http.server 8765
    python3 tests/t17.py
"""
import datetime, json, re
from playwright.sync_api import sync_playwright

URL = 'http://localhost:8765/index.html'
TODAY = datetime.date.today()
D = lambda k: (TODAY - datetime.timedelta(days=k)).isoformat()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra != '' and not ok else ''))
    if not ok: fails.append(label)
clean = lambda t: re.sub(r'[  ]', ' ', t)
E = lambda i, slot, name, k, p=10, c=20, f=5: dict(id=i, slot=slot, name=name, kcal=k, p=p, c=c, f=f)

with sync_playwright() as pw:
    b = pw.chromium.launch()
    def page(init=None):
        ctx = b.new_context(viewport={'width': 412, 'height': 900})
        if init: ctx.add_init_script(init)
        pg = ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(URL); pg.wait_for_timeout(300)
        return ctx, pg, errs
    def seed(pg, **o):
        pg.evaluate("s=>localStorage.setItem('forme.v1',JSON.stringify(Object.assign({settings:{v2:1,kcal:2000,auto:false,p:150,c:200,f:60}},s)))", o)
        pg.reload(); pg.wait_for_timeout(500)
    st = lambda pg: json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
    def food(pg, sub='journal'):
        pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(200)
        pg.click('[data-act="food-sub"][data-s="%s"]' % sub); pg.wait_for_timeout(250)
    def add(pg, slot, tab):
        pg.click('[data-act="f-add"][data-slot="%s"]' % slot); pg.wait_for_timeout(250)
        pg.click('[data-act="add-tab"][data-t="%s"]' % tab); pg.wait_for_timeout(250)
    today = lambda pg: st(pg).get('meals', {}).get(D(0), [])

    # ---------- 1. calories rapides ----------
    ctx, pg, errs = page(); seed(pg)
    food(pg); add(pg, 'lu', 'manual')
    check('Manuel : favori caché sans nom', not pg.is_visible('#mfavrow'))
    pg.click('[data-act="m-plus"][data-v="200"]'); pg.click('[data-act="m-plus"][data-v="200"]'); pg.click('[data-act="m-plus"][data-v="100"]')
    check('raccourcis : +200 +200 +100 = 500', pg.input_value('#mk') == '500', pg.input_value('#mk'))
    pg.click('[data-act="f-manual"]'); pg.wait_for_timeout(250)
    e = today(pg)
    check('sans nom : « Ajout rapide », 500 kcal, pas de favori', len(e) == 1 and e[0]['name'] == 'Ajout rapide' and e[0]['kcal'] == 500 and e[0]['slot'] == 'lu' and not st(pg)['foods'], e)
    add(pg, 'sn', 'manual')
    pg.fill('#mn', 'Barre de céréales'); pg.wait_for_timeout(50)
    check('avec un nom : favori proposé', pg.is_visible('#mfavrow'))
    pg.fill('#mk', '120'); pg.check('#mfav'); pg.click('[data-act="f-manual"]'); pg.wait_for_timeout(250)
    check('nommé + favori : ajouté et gardé', today(pg)[-1]['name'] == 'Barre de céréales' and st(pg)['foods'][0]['name'] == 'Barre de céréales')
    check('aucune erreur JavaScript (rapides)', not errs, errs)
    ctx.close()

    # ---------- 2. copier ; 3. repas types ----------
    ctx, pg, errs = page()
    seed(pg, meals={D(1): [E('a1', 'bk', 'Porridge', 350), E('a2', 'bk', 'Café', 20), E('a3', 'lu', 'Salade composée', 520)],
                    D(40): [E('z1', 'bk', 'Vieux petit-déj', 400)]})
    food(pg)
    pg.click('[data-act="f-copy"][data-slot="bk"]'); pg.wait_for_timeout(250)
    days = pg.evaluate("[...document.querySelectorAll('[data-act=\"f-copy-ok\"]')].map(b=>b.dataset.d)")
    check('copier un petit-déj : seulement les 28 derniers jours qui en ont un', days == [D(1)], days)
    pg.click('[data-act="f-copy-ok"][data-d="%s"]' % D(1)); pg.wait_for_timeout(250)
    e = today(pg)
    check('copié : 2 aliments au petit-déj, nouveaux identifiants', [x['name'] for x in e] == ['Porridge', 'Café'] and all(x['slot'] == 'bk' and x['id'] not in ('a1', 'a2') for x in e), e)
    pg.click('[data-act="f-copy"][data-slot=""]'); pg.wait_for_timeout(250)
    pg.click('[data-act="f-copy-ok"][data-d="%s"]' % D(1)); pg.wait_for_timeout(250)
    e = today(pg)
    check('copier une journée : 3 aliments de plus, chacun à sa place', len(e) == 5 and [x['slot'] for x in e[2:]] == ['bk', 'bk', 'lu'] and len({x['id'] for x in e}) == 5, [(x['name'], x['slot']) for x in e])
    check('la journée source n\'a pas bougé', len(st(pg)['meals'][D(1)]) == 3)
    pg.click('[data-act="cb-save"][data-slot="lu"]'); pg.wait_for_timeout(250)
    pg.fill('#cbn', 'Mon déjeuner salade'); pg.click('[data-act="cb-save-ok"]'); pg.wait_for_timeout(250)
    cb = st(pg)['combos']
    check('repas type enregistré', len(cb) == 1 and cb[0]['name'] == 'Mon déjeuner salade' and [i['name'] for i in cb[0]['items']] == ['Salade composée'], cb)
    add(pg, 'di', 'mine')
    check('Favoris : « Mes repas types » en haut', pg.text_content('#favlist').startswith('Mes repas types'), pg.text_content('#favlist')[:80])
    pg.click('[data-act="cb-add"]'); pg.wait_for_timeout(250)
    check('repas type ajouté en un geste au dîner', [x['name'] for x in today(pg) if x['slot'] == 'di'] == ['Salade composée'])
    add(pg, 'di', 'mine')
    pg.click('[data-act="cb-del"]'); pg.wait_for_timeout(250)
    check('repas type supprimé', st(pg)['combos'] == [] and 'Mes repas types' not in pg.text_content('#favlist'))
    check('aucune erreur JavaScript (copier, repas types)', not errs, errs)
    ctx.close()

    # ---------- 4. souvent a ce repas ----------
    ctx, pg, errs = page()
    meals = {}
    for k, names in {2: ['Café au lait', 'Tartine', 'Kiwi', 'Yaourt', 'Jus d’orange', 'Muesli'], 5: ['Café au lait', 'Tartine', 'Kiwi', 'Yaourt', 'Jus d’orange'],
                     9: ['Café au lait', 'Pomme'], 70: ['Banane'], 71: ['Banane']}.items():
        meals[D(k)] = [E('m%d_%d' % (k, i), 'bk', n, 50 + i) for i, n in enumerate(names)]
    meals[D(3)] = [E('l1', 'lu', 'Muesli', 300), E('l2', 'lu', 'Muesli', 300)]   # au dejeuner : ne compte pas pour le petit-dej
    seed(pg, meals=meals)
    food(pg); add(pg, 'bk', 'basic')
    often = pg.locator('#boften [data-act="f-often"] .t').all_inner_texts()
    check('Chercher : « Souvent » en haut, 4 au plus, le plus fréquent d\'abord', len(often) == 4 and often[0] == 'Café au lait' and not {'Pomme', 'Banane', 'Muesli'} & set(often), often)
    pg.fill('#bqin', 'riz'); pg.wait_for_timeout(200)
    check('masqué pendant une recherche', pg.locator('#boften [data-act="f-often"]').count() == 0)
    pg.fill('#bqin', ''); pg.wait_for_timeout(200)
    check('revient quand la recherche est vide', pg.locator('#boften [data-act="f-often"]').count() == 4)
    pg.click('[data-act="add-tab"][data-t="mine"]'); pg.wait_for_timeout(200)
    check('Favoris : « Souvent au petit-déjeuner »', 'Souvent au petit-déjeuner' in pg.text_content('#favlist'))
    pg.click('#favlist [data-act="f-often"]'); pg.wait_for_timeout(250)
    check('ajout en un geste', [x['name'] for x in today(pg)] == ['Café au lait'])
    check('aucune erreur JavaScript (souvent)', not errs, errs)
    ctx.close()

    # ---------- 5. source, correction, cru / cuit ----------
    ctx, pg, errs = page(); seed(pg)
    food(pg); add(pg, 'bk', 'basic')
    def pick(q, fid):
        pg.fill('#bqin', q); pg.wait_for_timeout(250); pg.click('#bres [data-act="b-pick"][data-id="%s"]' % fid); pg.wait_for_timeout(250)
    pick('oeuf', 'oeuf-entier')
    sh = clean(pg.inner_text('.sheet'))
    check('fiche : source des aliments de base', 'Source : valeurs moyennes des tables nutritionnelles' in sh)
    pg.click('[data-act="b-fix"]'); pg.wait_for_timeout(200)
    pg.fill('#xk', '150'); pg.click('[data-act="b-fix-ok"]'); pg.wait_for_timeout(250)
    sh = clean(pg.inner_text('.sheet'))
    check('correction : fiche à 150 kcal, original affiché', 'Pour 100 g : 150 kcal' in sh and 'Valeurs corrigées par toi' in sh and 'Original : 143 kcal' in sh, sh[:300])
    check('correction enregistrée dans S.fixes', st(pg)['fixes'].get('oeuf-entier', {}).get('k') == 150)
    pg.click('[data-act="b-q"][data-v="2"]'); pg.click('[data-act="b-add"]'); pg.wait_for_timeout(250)
    check('ajout futur aux valeurs corrigées : 2 œufs = 165 kcal', today(pg)[-1]['kcal'] == 165, today(pg))
    pg.reload(); pg.wait_for_timeout(500); food(pg); add(pg, 'bk', 'basic'); pick('oeuf', 'oeuf-entier')
    check('après rechargement : toujours corrigé', 'Pour 100 g : 150 kcal' in clean(pg.inner_text('.sheet')))
    pg.click('[data-act="b-fix"]'); pg.wait_for_timeout(200); pg.click('[data-act="b-fix-reset"]'); pg.wait_for_timeout(250)
    check('« Rétablir l\'original » : 143 kcal', 'Pour 100 g : 143 kcal' in clean(pg.inner_text('.sheet')) and 'oeuf-entier' not in st(pg)['fixes'])
    check('le journal ne change pas', today(pg)[-1]['kcal'] == 165)
    pg.click('[data-act="b-back"]'); pg.wait_for_timeout(200)
    pg.fill('#bqin', 'lentille'); pg.wait_for_timeout(250)
    cq = pg.evaluate("(()=>{const b=[...document.querySelectorAll('#bres [data-act=\"b-pick\"]')].find(x=>x.dataset.id.startsWith('cq'));return b&&b.dataset.id})()")
    pg.click('#bres [data-act="b-pick"][data-id="%s"]' % cq); pg.wait_for_timeout(250)
    check('fiche Ciqual : « Source : Anses, Table Ciqual 2025 »', 'Source : Anses, Table Ciqual 2025' in pg.inner_text('.sheet'), cq)
    pg.click('[data-act="b-back"]'); pg.wait_for_timeout(200)
    pick('poulet cru', 'blanc-de-poulet-cru')
    check('cru : bouton « Version cuite »', pg.locator('[data-act="b-twin"]').inner_text() == 'Version cuite')
    pg.click('[data-act="b-twin"]'); pg.wait_for_timeout(250)
    check('bascule vers « Blanc de poulet cuit »', 'Blanc de poulet cuit' in pg.inner_text('.sheet') and pg.locator('[data-act="b-twin"]').inner_text() == 'Version crue')
    pg.click('[data-act="b-back"]'); pg.wait_for_timeout(200)
    pick('jambon cru', 'jambon-cru')
    check('jambon cru : pas de jumeau (produit différent)', pg.locator('[data-act="b-twin"]').count() == 0)
    check('aucune erreur JavaScript (fiche)', not errs, errs)
    ctx.close()

    # ---------- 6. recette perso : portions et calcul ----------
    ctx, pg, errs = page(); seed(pg)
    food(pg, 'recipes'); pg.click('[data-act="rc-new"]'); pg.wait_for_timeout(250)
    pg.fill('#rfn', 'Poulet du test')
    pg.fill('#rfi', '150 g de blanc de poulet cru\n2 œufs\n1 càs d’huile d’olive\n100 g de xyzw')
    pg.fill('#rfpor', '2'); pg.click('[data-act="rc-calc"]'); pg.wait_for_timeout(250)
    calc = clean(pg.inner_text('#rfcalc'))
    exp = (150 * 110 / 100 + 110 * 143 / 100 + 13 * 900 / 100) / 2
    check('calcul : 3 ingrédients reconnus sur 4, « xyzw » non compté', '3 ingrédients reconnus sur 4' in calc and 'xyzw' in calc, calc)
    check('calcul : %.0f kcal par portion' % exp, pg.input_value('#rfk') == '%d' % round(exp), pg.input_value('#rfk'))
    pg.click('[data-act="rc-save"]'); pg.wait_for_timeout(300)
    mine = st(pg)['recipes']['mine'][0]
    check('recette enregistrée avec 2 portions', mine['por'] == 2 and mine['k'] == round(exp), mine)
    check('aucune erreur JavaScript (recette)', not errs, errs)
    ctx.close()

    # ---------- 7. semaine et liste de courses ; 8. frigo ----------
    ctx, pg, errs = page(); seed(pg)
    food(pg, 'week')
    check('Semaine : 7 jours', pg.locator('.plday').count() == 7)
    def plan(d, slot, rid):
        pg.click('[data-act="pl-add"][data-d="%s"]' % d); pg.wait_for_timeout(200)
        pg.click('[data-act="pl-slot"][data-s="%s"]' % slot); pg.wait_for_timeout(150)
        pg.click('[data-act="pl-pick"][data-id="%s"]' % rid); pg.wait_for_timeout(250)
    tomorrow = (TODAY + datetime.timedelta(days=1)).isoformat()
    plan(D(0), 'lu', 'bowl_poulet'); plan(tomorrow, 'lu', 'bowl_poulet')
    days = st(pg)['plan']['days']
    check('recettes posées sur 2 jours', days[D(0)]['lu'] == [{'r': 'bowl_poulet', 'ok': 0}] and days[tomorrow]['lu'][0]['r'] == 'bowl_poulet', days)
    shop = clean(pg.inner_text('#shop'))
    check('courses : quantités additionnées (300 g de poulet, 140 g de riz)', re.search(r'Blanc de poulet cru\s*300 g', shop) and re.search(r'Riz basmati cru\s*140 g', shop), shop[:400])
    shopt = clean(pg.text_content('#shop'))
    check('courses : rangées par rayon', 'Viandes, poissons, œufs' in shopt and 'Féculents & céréales' in shopt and shopt.index('Viandes') < shopt.index('Féculents'), shopt[:300])
    pg.click('[data-act="pl-log"][data-d="%s"]' % tomorrow); pg.wait_for_timeout(200)
    check('✓ un jour à venir : refusé', not st(pg)['meals'].get(tomorrow))
    pg.click('[data-act="pl-log"][data-d="%s"]' % D(0)); pg.wait_for_timeout(250)
    check('✓ aujourd\'hui : noté au journal (déjeuner), recette faite', [x['name'] for x in today(pg)] == ['Bowl poulet, riz et brocoli'] and today(pg)[0]['slot'] == 'lu' and st(pg)['recipes']['done']['bowl_poulet']['n'] == 1)
    check('recette notée : retirée des courses (150 g)', re.search(r'Blanc de poulet cru\s*150 g', clean(pg.inner_text('#shop'))))
    pg.fill('#shnew', 'Papier cuisson'); pg.click('[data-act="sh-add"]'); pg.wait_for_timeout(200)
    pg.fill('#shnew', '2 citrons'); pg.click('[data-act="sh-add"]'); pg.wait_for_timeout(200)
    shop = clean(pg.inner_text('#shop'))
    check('ajouts à la main : texte libre et quantité lue', 'Papier cuisson' in shop and re.search(r'Citrons?\s*2', shop), shop[-400:])
    keys = pg.evaluate("[...document.querySelectorAll('#shop [data-act=\"sh-tog\"]')].map(b=>[b.dataset.k,b.textContent])")
    kp = next(k for k, t in keys if 'Blanc de poulet' in t); kx = next(k for k, t in keys if 'Papier cuisson' in t)
    pg.click('#shop [data-act="sh-tog"][data-k="%s"]' % kp); pg.click('#shop [data-act="sh-tog"][data-k="%s"]' % kx); pg.wait_for_timeout(200)
    check('cases cochées, enregistrées', st(pg)['plan']['shop']['done'] == {kp: 1, kx: 1})
    pg.click('[data-act="sh-fridge"]'); pg.wait_for_timeout(250)
    s2 = st(pg)
    check('« Ranger dans mon frigo » : poulet et papier dans le frigo, ajout à la main retiré de la liste',
          'blanc de poulet cru' in s2['fridge']['have'] and 'papier cuisson' in s2['fridge']['have'] and not any(e.get('t') == 'Papier cuisson' for e in s2['plan']['shop']['extra']), s2['fridge'])
    pg.click('[data-act="pl-del"][data-d="%s"]' % tomorrow); pg.wait_for_timeout(200)
    check('retirer une recette du planning', not st(pg)['plan']['days'].get(tomorrow))
    # fiche d'une recette -> liste de courses
    food(pg, 'recipes'); pg.click('[data-act="rc-open"][data-id="omelette"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="rc-shop"]'); pg.wait_for_timeout(200); pg.click('.sheet [data-act="close"]') if pg.locator('.sheet [data-act="close"]').count() else None
    pg.evaluate("document.querySelector('#layer').innerHTML=''")
    food(pg, 'week')
    check('« Ajouter à ma liste de courses » : 3 œufs, épinards', re.search(r'Œufs\s*3', clean(pg.inner_text('#shop'))) and 'Épinards frais' in pg.inner_text('#shop'), clean(pg.inner_text('#shop'))[:500])
    # 8. frigo
    food(pg, 'recipes')
    pg.click('[data-act="fr-open"]'); pg.wait_for_timeout(250)
    for k in ('oeuf', 'epinard frai', 'mozzarella allegee', 'jambon blanc', 'pain complet'):
        if pg.locator('[data-act="fr-tog"][data-k="%s"]' % k).count():
            if pg.get_attribute('[data-act="fr-tog"][data-k="%s"]' % k, 'aria-pressed') != 'true': pg.click('[data-act="fr-tog"][data-k="%s"]' % k)
    pg.click('[data-act="fr-done"]'); pg.wait_for_timeout(250)
    have = st(pg)['fridge']['have']
    check('Mon frigo : cases enregistrées', {'oeuf', 'mozzarella allegee', 'jambon blanc', 'pain complet'} <= set(have), have)
    pg.click('[data-act="fr-chip"]'); pg.wait_for_timeout(250)
    first = pg.locator('#view [data-act="rc-open"]').first
    check('« Avec mon frigo » : l\'omelette (rien ne manque) en premier', first.get_attribute('data-id') == 'omelette' and 'Tout est dans ton frigo' in first.inner_text(), first.inner_text())
    check('pastille « Il manque » sur les autres', pg.locator('#view .pill:has-text("Il manque")').count() > 0)
    check('aucune erreur JavaScript (semaine, frigo)', not errs, errs)
    ctx.close()
    # sel, poivre, huile, epices toujours presents
    ctx, pg, errs = page()
    seed(pg, recipes={'done': {}, 'notes': {}, 'mine': [{'id': 'u_t', 'n': 'Test frigo', 's': ['lu'], 't': 10, 'k': 300, 'p': 20, 'c': 10, 'f': 5, 'ingTxt': ['100 g de tofu', 'sel', 'poivre', '1 càs d’huile', '1 pincée de cumin'], 'st': [], 'mine': 1}]},
         fridge={'have': ['tofu']})
    food(pg, 'recipes')
    row = pg.locator('#view [data-act="rc-open"][data-id="u_t"]')
    check('sel, poivre, huile, épices : toujours présents', 'Tout est dans ton frigo' in row.inner_text(), row.inner_text())
    ctx.close()

    # ---------- 9. bilan ----------
    ctx, pg, errs = page()
    noted = [1, 2, 3, 4] + list(range(6, 16)) + [18, 19]          # -5 oublie (pardonne), -16 et -17 oublies (rupture)
    kc = {1: 1500, 2: 2400, 3: 2700, 4: 1000}
    seed(pg, meals={D(k): [E('b%d' % k, 'lu', 'Repas du jour %d' % k, kc.get(k, 1900), 100, 200, 60)] for k in noted})
    food(pg, 'bilan')
    s = clean(pg.inner_text('#blstreak'))
    check('série : 14 jours, 1 oubli pardonné (aujourd\'hui pas encore noté)', '🔥 14 jours notés de suite' in s and '1 jour sans rien de noté pardonné' in s, s)
    check('7 jours : 7 barres', pg.locator('.wkbar').count() == 7)
    avg = pg.locator('#blavg .stat b').first.inner_text()
    exp_avg = sum(kc.get(k, 1900) for k in range(1, 7) if k in noted) / len([k for k in range(1, 7) if k in noted])
    check('moyenne des jours notés : %d kcal' % round(exp_avg), clean(avg).replace(' ', '') == str(round(exp_avg)), avg)
    def cls(d):
        if not pg.locator('.calday[data-d="%s"]' % d).count():
            pg.click('[data-act="bl-mon"][data-n="-1"]'); pg.wait_for_timeout(200)
        return pg.get_attribute('.calday[data-d="%s"]' % d, 'class')
    bands = {k: cls(D(k)) for k in (1, 2, 3, 4)}
    check('calendrier : 75 % vert, 120 % orange, 135 % rouge, 50 % gris',
          'bok' in bands[1] and 'bwarn' in bands[2] and 'bbad' in bands[3] and 'blo' in bands[4], bands)
    pg.click('.calday[data-d="%s"]' % D(3)); pg.wait_for_timeout(250)
    check('toucher un jour : le journal de ce jour s\'ouvre', 'Repas du jour 3' in pg.inner_text('#view') and pg.get_attribute('[data-act="food-sub"][data-s="journal"]', 'aria-selected') == 'true')
    pg.click('[data-act="f-day"][data-n="1"]'); pg.click('[data-act="f-day"][data-n="1"]'); pg.click('[data-act="f-day"][data-n="1"]'); pg.wait_for_timeout(200)
    add(pg, 'bk', 'manual'); pg.fill('#mk', '300'); pg.click('[data-act="f-manual"]'); pg.wait_for_timeout(250)
    check('journal : la série s\'affiche dans la carte du cercle (15 avec aujourd\'hui)', '🔥 15 jours notés de suite' in pg.inner_text('#fstreak'), pg.locator('#fstreak').all_inner_texts())
    check('aucune erreur JavaScript (bilan)', not errs, errs)
    ctx.close()

    # ---------- 10. synchro des nouvelles tranches ----------
    FAKE = """(()=>{window.__sent=[];const R=%s;
      const coll={get:async()=>({docs:Object.entries(R).map(([id,v])=>({id,data:()=>({t:9e12,v})}))}),
                  doc:id=>({set:async x=>{window.__sent.push([id,JSON.parse(JSON.stringify(x))])}})};
      window.claude={use:async k=>k==='db'?{collection:()=>coll}:k==='user'?{id:async()=>'u-test'}:null};})()"""
    remote = {'fixes': {'oeuf-entier': {'k': 160, 'p': 13, 'c': 1, 'f': 11}}, 'combos': [{'id': 'c1', 'name': 'Reçu du compte', 'slot': 'bk', 'items': [{'name': 'Thé', 'kcal': 2, 'p': 0, 'c': 0, 'f': 0}]}]}
    ctx, pg, errs = page(FAKE % json.dumps(remote))
    pg.evaluate("s=>localStorage.setItem('forme.v1',JSON.stringify(s))", {'settings': {'v2': 1}, 'plan': {'days': {D(0): {'lu': [{'r': 'chili', 'ok': 0}]}}, 'shop': {'done': {}, 'extra': []}}, 'fridge': {'have': ['tofu']}})
    pg.reload(); pg.wait_for_timeout(1500)
    sent = {k for k, x in pg.evaluate('window.__sent')}
    check('synchro : planning et frigo envoyés au compte', {'plan', 'fridge'} <= sent, sent)
    check('synchro : repas types et corrections reçus', st(pg)['combos'][0]['name'] == 'Reçu du compte' and st(pg)['fixes']['oeuf-entier']['k'] == 160)
    food(pg); add(pg, 'bk', 'basic'); pg.fill('#bqin', 'oeuf'); pg.wait_for_timeout(250)
    pg.click('#bres [data-act="b-pick"][data-id="oeuf-entier"]'); pg.wait_for_timeout(250)
    check('synchro : correction reçue appliquée à l\'aliment (160 kcal)', 'Pour 100 g : 160 kcal' in clean(pg.inner_text('.sheet')))
    check('aucune erreur JavaScript (synchro)', not errs, errs)
    ctx.close()
    b.close()

print('\n%d echec(s) : %s' % (len(fails), fails) if fails else '\nTOUT EST OK')
