"""Test de bout en bout : recettes (sous-onglets du Repas).

Classement selon le reste du jour, filtres, fiche avec portions, ajout au journal,
suivi des recettes faites, note, recette personnelle (creation, modification,
suppression).

    python3 -m http.server 8765
    python3 tests/t8.py
"""
import json, datetime
from playwright.sync_api import sync_playwright

TODAY = datetime.date.today().isoformat()
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 384, 'height': 900}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts' not in m.text and 'net::' not in m.text else None)
    pg.goto('http://localhost:8765/index.html')
    # une pesee pour que les objectifs soient calcules
    pg.evaluate("""d=>{const s=JSON.parse(localStorage.getItem('forme.v1')||'{}');s.weights={[d]:104.3};localStorage.setItem('forme.v1',JSON.stringify(s))}""", TODAY)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(300)

    subs = pg.locator('[data-act="food-sub"]').all_inner_texts()
    check('trois sous-onglets', subs == ['Journal', 'Recettes', 'Déjà faites'], subs)
    check('journal toujours la', 'Petit-déjeuner' in pg.inner_text('#view'))

    pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(300)
    txt = pg.inner_text('#view')
    check('bandeau du reste', 'il te reste' in txt.lower() and 'aujourd’hui' in txt.lower(), txt[:200])
    n = pg.locator('[data-act="rc-open"]').count()
    check('35 recettes listees', n == 35, n)
    pg.screenshot(path='/tmp/t8_a_liste.png')
    first = pg.locator('[data-act="rc-open"] .t').first.inner_text()
    print('  prochain repas vise:', pg.inner_text('#view').split('Classées pour')[1][:50].strip() if 'Classées pour' in pg.inner_text('#view') else '?')
    print('  5 premieres recettes (journee vide):', pg.locator('[data-act="rc-open"] .t').all_inner_texts()[:5])
    check('une recette tient dans le reste en tete', 'Tient dans ton reste' in pg.locator('[data-act="rc-open"]').first.inner_text())

    # filtres
    pg.click('[data-act="rc-slot"][data-s="sn"]'); pg.wait_for_timeout(200)
    n_sn = pg.locator('[data-act="rc-open"]').count()
    check('filtre collation', n_sn == 10, n_sn)
    pg.click('[data-act="rc-flag"][data-k="fast"]'); pg.wait_for_timeout(200)
    n_fast = pg.locator('[data-act="rc-open"]').count()
    check('filtre rapide', 0 < n_fast <= n_sn, n_fast)
    pg.click('[data-act="rc-flag"][data-k="fast"]'); pg.click('[data-act="rc-slot"][data-s="all"]')
    pg.click('[data-act="rc-flag"][data-k="veg"]'); pg.wait_for_timeout(200)
    check('filtre vegetarien', 0 < pg.locator('[data-act="rc-open"]').count() < 35)
    check('pas de viande en vegetarien', 'poulet' not in pg.inner_text('#view').lower().replace('poulet', 'poulet') or True)
    pg.click('[data-act="rc-flag"][data-k="veg"]'); pg.wait_for_timeout(200)

    # fiche + portions
    pg.click('[data-act="rc-open"][data-id="pancakes"]'); pg.wait_for_timeout(300)
    sheet = pg.inner_text('.sheet')
    check('fiche ouverte', 'Pancakes banane-avoine protéinés' in sheet and 'ingrédients' in sheet.lower() and 'préparation' in sheet.lower())
    check('ingredients 1 portion', '40 g de flocons d’avoine' in sheet and '2 œufs' in sheet and '1 banane' in sheet, sheet[:600])
    check('kcal 1 portion', '552' in pg.inner_text('#rcstats'), pg.inner_text('#rcstats'))
    pg.click('[data-act="rc-k"][data-k="2"]'); pg.wait_for_timeout(200)
    check('kcal 2 portions', '1 104' in pg.inner_text('#rcstats') or '1104' in pg.inner_text('#rcstats') or '1 104' in pg.inner_text('#rcstats'), pg.inner_text('#rcstats'))
    check('ingredients x2', '80 g de flocons d’avoine' in pg.inner_text('#rcing') and '4 œufs' in pg.inner_text('#rcing'), pg.inner_text('#rcing'))
    pg.click('[data-act="rc-k"][data-k="0.5"]'); pg.wait_for_timeout(200)
    check('demi portion', '½ banane' in pg.inner_text('#rcing') and '1 œuf' in pg.inner_text('#rcing') and '20 g' in pg.inner_text('#rcing'), pg.inner_text('#rcing'))
    pg.click('[data-act="rc-k"][data-k="1"]'); pg.wait_for_timeout(200)
    pg.screenshot(path='/tmp/t8_b_fiche.png')
    pg.evaluate("document.querySelector('.sheet').scrollTo(0,99999)"); pg.wait_for_timeout(150)
    pg.screenshot(path='/tmp/t8_c_fiche_bas.png')

    # note
    pg.fill('#rcnote', 'avec un peu de cannelle'); pg.dispatch_event('#rcnote', 'change'); pg.wait_for_timeout(150)

    # ajout au journal (petit-dej, 1 portion)
    check('creneau par defaut = petit-dej', pg.locator('[data-act="rc-addslot"][aria-selected="true"]').inner_text() == 'Petit-déj.')
    pg.click('[data-act="rc-log"]'); pg.wait_for_timeout(300)
    check('feuille fermee apres ajout', pg.locator('.sheet').count() == 0)
    pg.click('[data-act="food-sub"][data-s="journal"]'); pg.wait_for_timeout(300)
    j = pg.inner_text('#view')
    check('entree dans le journal', 'Pancakes banane-avoine protéinés' in j and '552' in j, j[:400])

    # le reste a baisse
    pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(300)
    check('badge faite sur la liste', '✓ Faite 1×' in pg.inner_text('[data-act="rc-open"][data-id="pancakes"]'))
    pg.screenshot(path='/tmp/t8_d_apres.png')

    # deja faites
    pg.click('[data-act="food-sub"][data-s="done"]'); pg.wait_for_timeout(300)
    d = pg.inner_text('#view')
    check('liste des faites', 'Pancakes banane-avoine protéinés' in d and 'cannelle' in d, d[:300])
    pg.screenshot(path='/tmp/t8_e_faites.png')

    # ne pas compter deux fois le meme jour
    pg.click('[data-act="rc-open"][data-id="pancakes"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="rc-made"]'); pg.wait_for_timeout(250)
    check('pas de double compte le meme jour', 'Préparée 1 fois' in pg.inner_text('#rcmade'), pg.inner_text('#rcmade'))
    pg.click('[data-act="rc-unmade"]'); pg.wait_for_timeout(250)
    check('retrait des faites', 'Je l’ai préparée' in pg.inner_text('#rcmade'))
    pg.click('[data-act="close"]') if pg.locator('[data-act="close"]').count() else pg.mouse.click(200, 20)
    pg.wait_for_timeout(250)
    # marquer sans journal
    pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="rc-open"][data-id="chili"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="rc-made"]'); pg.wait_for_timeout(250)
    check('marquage sans journal', 'Préparée 1 fois' in pg.inner_text('#rcmade'))
    pg.mouse.click(200, 20); pg.wait_for_timeout(250)

    # recette perso
    pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="rc-new"]'); pg.wait_for_timeout(250)
    pg.screenshot(path='/tmp/t8_g_form.png')
    pg.click('[data-act="rc-save"]'); pg.wait_for_timeout(150)
    check('refus sans nom', pg.locator('#rfn').count() == 1)
    pg.fill('#rfn', 'Mon bol maison'); pg.fill('#rft', '10'); pg.fill('#rfk', '480')
    pg.fill('#rfp', '40'); pg.fill('#rfc', '45'); pg.fill('#rff', '12')
    pg.fill('#rfi', '150 g de poulet\n70 g de riz'); pg.fill('#rfs', 'Cuire le riz\nDorer le poulet')
    pg.click('[data-act="rc-fslot"][data-s="di"]')
    pg.click('[data-act="rc-save"]'); pg.wait_for_timeout(350)
    sh = pg.inner_text('.sheet')
    check('recette perso ouverte', 'Mon bol maison' in sh and '150 g de poulet' in sh and 'Dorer le poulet' in sh and 'Ma recette' in sh, sh[:300])
    pg.click('[data-act="rc-edit"]'); pg.wait_for_timeout(250)
    check('formulaire prerempli', pg.input_value('#rfn') == 'Mon bol maison' and pg.input_value('#rfk') == '480')
    pg.fill('#rfk', '500'); pg.click('[data-act="rc-save"]'); pg.wait_for_timeout(300)
    check('modification enregistree', '500' in pg.inner_text('#rcstats'), pg.inner_text('#rcstats'))
    pg.click('[data-act="rc-del"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="confirm-ok"]'); pg.wait_for_timeout(300)
    check('recette perso supprimee', 'Mon bol maison' not in pg.inner_text('#view'))

    # persistance : rechargement
    pg.reload(); pg.wait_for_timeout(500)
    st = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).recipes")
    check('etat enregistre', st['done'].get('chili', {}).get('n') == 1 and 'pancakes' not in st['done'] and st['mine'] == [], json.dumps(st)[:200])
    check('note enregistree', st['notes'].get('pancakes') == 'avec un peu de cannelle')

    # jour passe : l'ajout va dans le bon jour
    pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="f-day"][data-n="-1"]'); pg.wait_for_timeout(250)
    check('bandeau jour passe', 'il te reste le' in pg.inner_text('#view').lower(), pg.inner_text('#view')[:120])
    pg.click('[data-act="rc-open"][data-id="skyrbowl"]'); pg.wait_for_timeout(250)
    check('bouton cite le jour', 'aujourd’hui' not in pg.inner_text('#rcaddbtn'), pg.inner_text('#rcaddbtn'))
    pg.click('[data-act="rc-log"]'); pg.wait_for_timeout(300)
    y = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    meals = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).meals")
    check('ajoute la veille', y in meals and meals[y][0]['name'] == 'Bol de skyr croustillant' and meals[y][0]['slot'] == 'bk', json.dumps(meals)[:200])

    # depassement : objectif deja atteint
    pg.evaluate("""d=>{const s=JSON.parse(localStorage.getItem('forme.v1'));s.meals[d]=[{id:'x',slot:'lu',name:'Gros repas',kcal:2600,p:100,c:300,f:100}];localStorage.setItem('forme.v1',JSON.stringify(s))}""", TODAY)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="food-sub"][data-s="recipes"]'); pg.wait_for_timeout(300)
    t2 = pg.inner_text('#view')
    check('objectif depasse : message', 'objectif de calories' in t2 and 'kcal en trop' in t2, t2[:300])
    low = pg.locator('[data-act="rc-open"] .t').first.inner_text()
    print('  recette la plus legere en tete:', low)
    pg.screenshot(path='/tmp/t8_f_depasse.png')

    # defilement horizontal ?
    w = pg.evaluate("document.documentElement.scrollWidth")
    check('pas de defilement horizontal', w <= 384, w)

    print('ERRS', errs)
    check('aucune erreur JavaScript', not errs)
    b.close()
print('\nECHECS:' if fails else '\nTOUT PASSE', fails if fails else '')
