"""Test de bout en bout : bibliotheque des produits scannes (onglet Scan > Bibliotheque).

Produits FICTIFS ecrits par le test (aucune donnee reelle).

    python3 -m http.server 8765
    python3 tests/t10.py
"""
import sys, json, datetime
from playwright.sync_api import sync_playwright

PAGE = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra and not ok else ''))
    if not ok: fails.append(label)

# nom -> (section, sous-section) attendues
CASES = [
 ('Saumon fumé', 'Viandes, poissons, œufs', 'Poissons & fruits de mer'),
 ('Thon au naturel', 'Viandes, poissons, œufs', 'Poissons & fruits de mer'),
 ('Jambon blanc découenné', 'Viandes, poissons, œufs', 'Charcuteries'),
 ('Saucisson sec', 'Viandes, poissons, œufs', 'Charcuteries'),
 ('Œufs plein air x6', 'Viandes, poissons, œufs', 'Œufs'),
 ('Blanc de poulet', 'Viandes, poissons, œufs', 'Viandes'),
 ('Steak haché 5 %', 'Viandes, poissons, œufs', 'Viandes'),
 ('Yaourt grec nature', 'Produits laitiers', 'Yaourts & fromages blancs'),
 ('Skyr nature', 'Produits laitiers', 'Yaourts & fromages blancs'),
 ('Emmental râpé', 'Produits laitiers', 'Fromages'),
 ('Beurre doux', 'Produits laitiers', 'Crèmes & beurres'),
 ('Lait demi-écrémé', 'Produits laitiers', 'Laits'),
 ('Boisson à l’avoine', 'Boissons', 'Boissons végétales'),
 ('Coca-Cola zéro', 'Boissons', 'Jus & sodas'),
 ('Eau minérale Evian', 'Boissons', 'Eaux'),
 ('Café moulu', 'Boissons', 'Café, thé & boissons chaudes'),
 ('Vin rouge', 'Boissons', 'Alcools'),
 ('Pizza 4 fromages', 'Plats préparés', 'Pizzas, quiches & tartes salées'),
 ('Soupe de légumes', 'Plats préparés', 'Soupes'),
 ('Lasagnes bolognaise', 'Plats préparés', 'Plats cuisinés'),
 ('Sandwich jambon-beurre', 'Plats préparés', 'Sandwichs & burgers'),
 ('Pâtes torsades', 'Féculents & céréales', 'Pâtes, riz, semoule & farine'),
 ('Muesli croustillant', 'Féculents & céréales', 'Céréales du petit-déjeuner'),
 ('Pain complet tranché', 'Féculents & céréales', 'Pains & viennoiseries'),
 ('Lentilles corail', 'Féculents & céréales', 'Légumineuses & protéines végétales'),
 ('Pâte à tartiner chocolat-noisette', 'Produits sucrés', 'Pâtes à tartiner, confitures & miel'),
 ('Chocolat noir 70 %', 'Produits sucrés', 'Chocolat & confiseries'),
 ('Petit beurre', 'Produits sucrés', 'Biscuits & gâteaux'),
 ('Glace vanille', 'Produits sucrés', 'Desserts & glaces'),
 ('Chips nature', 'Apéritif & en-cas', 'Chips & biscuits apéritif'),
 ('Barre de céréales', 'Apéritif & en-cas', 'Barres & en-cas'),
 ('Whey isolate vanille', 'Sport & compléments', 'Protéines en poudre'),
 ('Barre protéinée caramel', 'Sport & compléments', 'Barres protéinées'),
 ('Huile d’olive vierge extra', 'Huiles, sauces & condiments', 'Huiles & vinaigres'),
 ('Ketchup', 'Huiles, sauces & condiments', 'Sauces & condiments'),
 ('Haricots verts extra-fins', 'Fruits & légumes', 'Légumes & pommes de terre'),
 ('Compote pomme sans sucre', 'Fruits & légumes', 'Fruits & compotes'),
 ('Amandes entières', 'Fruits & légumes', 'Fruits secs & oléagineux'),
 ('Produit mystère', 'Autres', 'Non classé'),
]
TAGGED = {'name': 'Produit sans indice', 'tags': ['dairies', 'cheeses', 'soft-cheeses'], 'sec': 'Produits laitiers', 'sub': 'Fromages'}

def prod(i, name, **kw):
    d = dict(id='t%02d' % i, date=datetime.date.today().isoformat(), name=name, brand='', code='', src='manual',
             per=dict(kcal=120, fat=5, sat=1, carbs=12, sugar=3, salt=.2, fiber=1, prot=6, fv=0), additives=[])
    d.update(kw); return d

with sync_playwright() as p:
    b = p.chromium.launch()
    ctx = b.new_context(viewport={'width': 384, 'height': 900}, device_scale_factor=2)
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append(m.text) if m.type == 'error' and 'fonts' not in m.text and 'net::' not in m.text else None)
    pg.goto('http://localhost:8765/' + PAGE)
    pg.reload(); pg.wait_for_timeout(300)
    # bibliotheque vide
    pg.click('.tab[data-t="scan"]'); pg.wait_for_timeout(200)
    subs = pg.locator('[data-act="scan-sub"]').all_inner_texts()
    check('deux sous-onglets', len(subs) == 2 and subs[0].startswith('Scanner') and subs[1].startswith('Biblioth'), subs)
    pg.click('[data-act="scan-sub"][data-s="lib"]'); pg.wait_for_timeout(200)
    check('bibliotheque vide : message', 'bibliothèque est vide' in pg.inner_text('#view'), pg.inner_text('#view')[:120])

    items = [prod(i, c[0]) for i, c in enumerate(CASES)]
    items.append(prod(99, TAGGED['name'], src='off', tags=TAGGED['tags']))
    # doublons : meme produit, marques differentes, memes apports -> une seule ligne
    ham = dict(kcal=105, fat=2.5, sat=1, carbs=0.5, sugar=0.4, salt=1.9, fiber=0, prot=20, fv=0)
    items.append(prod(100, 'Jambon de porc supérieur', brand='Marque A', code='111', per=ham))
    items.append(prod(101, 'Jambon de porc', brand='Marque B', code='222', per=ham))
    items.append(prod(102, 'Jambon de porc -25 % de sel', brand='Marque C', code='333', per=dict(ham, kcal=110)))   # apports differents : a part
    water0 = dict(kcal=0, fat=0, sat=0, carbs=0, sugar=0, salt=0, fiber=0, prot=0, fv=0)
    items.append(prod(103, 'Eau minérale Volvic', brand='Volvic', code='444', per=water0))
    items.append(prod(104, 'Eau minérale Vittel', brand='Vittel', code='555', per=water0))                          # valeurs vides : jamais fusionnees
    n_hams = 2   # fiches fusionnees en une ligne
    pg.evaluate("a=>{const s=JSON.parse(localStorage.getItem('forme.v1')||'{}');s.scans=a;localStorage.setItem('forme.v1',JSON.stringify(s))}", items)
    pg.reload(); pg.wait_for_timeout(500)
    pg.click('.tab[data-t="scan"]'); pg.wait_for_timeout(200)

    # onglet Scanner : 5 derniers + bouton
    txt = pg.inner_text('#view')
    check('Scanner : 5 derniers seulement', pg.locator('[data-act="s-open"]').count() == 5, pg.locator('[data-act="s-open"]').count())
    check('Scanner : bouton vers la bibliotheque', pg.locator('[data-act="lib-go"]').count() == 1)
    pg.click('[data-act="lib-go"]'); pg.wait_for_timeout(250)
    check('ouvre la bibliotheque', pg.locator('#libq').count() == 1)
    n_all = len(items) - 1   # Jambon A + B comptent pour un seul produit
    check('compte total sans doublon', ('%d produits' % n_all) in pg.inner_text('#libcount'), pg.inner_text('#libcount'))
    pg.screenshot(path='/tmp/t10_a_ferme.png')

    # tout ouvrir et verifier le classement
    pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(250)
    where = pg.evaluate("""()=>{const out={};document.querySelectorAll('#libres .libsec').forEach(sec=>{
      const s=sec.querySelector('.libh .grow').textContent.trim();let sub='';
      sec.querySelectorAll('.libbody > *').forEach(el=>{
        if(el.classList.contains('libsub'))sub=el.textContent.split('·')[0].trim();
        else el.querySelectorAll('.li .t').forEach(t=>{out[t.textContent.trim()]=[s,sub]});
      })});return out}""")
    bad = []
    for name, sec, sub in CASES + [(TAGGED['name'], TAGGED['sec'], TAGGED['sub'])]:
        got = where.get(name)
        if got != [sec, sub]: bad.append((name, got, (sec, sub)))
    check('classement automatique de %d produits' % n_all, not bad, bad)
    for x in bad: print('     ', x)
    pg.screenshot(path='/tmp/t10_b_ouvert.png', full_page=False)

    # doublons
    hams = pg.locator('#libres .li', has_text='Jambon de porc')
    names = hams.all_inner_texts()
    check('jambons : 2 lignes (A+B fusionnes, C a part)', len(names) == 2, names)
    check('ligne fusionnee marquee ×2 avec les 2 marques', any('×2' in t and 'Marque A' in t and 'Marque B' in t for t in names), names)
    check('eaux a 0 kcal jamais fusionnees', pg.locator('#libres .li', has_text='Eau minérale').count() == 3)

    # tout fermer
    pg.click('[data-act="lib-all"]'); pg.wait_for_timeout(200)
    check('tout fermer', pg.locator('#libres .libbody').count() == 0)
    # une section
    pg.click('[data-act="lib-sec"][data-s="vpo"]'); pg.wait_for_timeout(200)
    check('section VPO : 4 sous-sections', pg.locator('#libres .libsub').count() == 4, pg.locator('#libres .libsub').all_inner_texts())
    pg.screenshot(path='/tmp/t10_c_vpo.png')

    # recherche
    pg.fill('#libq', 'oeuf'); pg.wait_for_timeout(200)
    check('recherche « oeuf »', pg.locator('#libres .li').count() == 1 and 'Œufs' in pg.inner_text('#libres'), pg.inner_text('#libres')[:100])
    pg.fill('#libq', 'zzzz'); pg.wait_for_timeout(200)
    check('recherche vide', 'Aucun produit' in pg.inner_text('#libres'))
    pg.fill('#libq', ''); pg.wait_for_timeout(200)

    # fiche + rangement manuel
    pg.click('[data-act="lib-sec"][data-s="autre"]'); pg.wait_for_timeout(200)
    pg.click('[data-act="lib-open"] >> text=Produit mystère'); pg.wait_for_timeout(300)
    check('fiche en feuille', pg.locator('#layer #libset').count() == 1)
    pg.screenshot(path='/tmp/t10_d_fiche.png')
    pg.select_option('#libset', 'vpo.oeuf'); pg.wait_for_timeout(300)
    stored = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).scans.find(s=>s.name==='Produit mystère').cat")
    check('rangement choisi enregistre', stored == 'vpo.oeuf', stored)
    pg.mouse.click(190, 40); pg.wait_for_timeout(300)   # ferme la feuille (voile)
    pg.click('[data-act="lib-sec"][data-s="vpo"]') if pg.locator('[data-act="lib-sec"][data-s="vpo"][aria-expanded="false"]').count() else None
    pg.wait_for_timeout(200)
    check('produit deplace dans Œufs', 'Produit mystère' in pg.inner_text('#libres') and pg.locator('[data-act="lib-sec"][data-s="autre"]').is_disabled())

    # suppression
    pg.click('[data-act="lib-open"] >> text=Produit mystère'); pg.wait_for_timeout(300)
    pg.click('[data-act="lib-del"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="confirm-ok"]'); pg.wait_for_timeout(300)
    left = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).scans.length")
    check('suppression', left == len(items) - 1, left)

    # rangement et suppression d'un groupe de doublons
    pg.click('[data-act="lib-sec"][data-s="vpo"]') if pg.locator('[data-act="lib-sec"][data-s="vpo"][aria-expanded="false"]').count() else None
    pg.wait_for_timeout(200)
    pg.locator('#libres .li', has_text='×2').click(); pg.wait_for_timeout(300)
    check('fiche du groupe : liste des 2 fiches', 'même produit, 2 fiches' in pg.inner_text('#layer').lower(), pg.inner_text('#layer')[:100])
    pg.select_option('#libset', 'vpo.viande'); pg.wait_for_timeout(300)
    cats = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).scans.filter(s=>s.code==='111'||s.code==='222').map(s=>s.cat)")
    check('rangement applique aux 2 fiches', cats == ['vpo.viande', 'vpo.viande'], cats)
    pg.locator('#layer .scrim').click(position={'x': 190, 'y': 30}); pg.wait_for_timeout(300)
    pg.locator('#libres .li', has_text='×2').click(); pg.wait_for_timeout(300)
    pg.click('[data-act="lib-del"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="confirm-ok"]'); pg.wait_for_timeout(300)
    left2 = pg.evaluate("JSON.parse(localStorage.getItem('forme.v1')).scans.length")
    check('suppression du groupe : 2 fiches retirees', left2 == left - 2, (left, left2))

    ov = pg.evaluate("document.documentElement.scrollWidth<=document.documentElement.clientWidth")
    check('pas de defilement horizontal', ov)
    # retour a l'onglet Scanner
    pg.click('[data-act="scan-sub"][data-s="scan"]'); pg.wait_for_timeout(200)
    check('retour sur Scanner', pg.locator('[data-act="s-manual"]').count() >= 1)
    print('ERRS', errs)
    check('aucune erreur JS', not errs, errs)
    b.close()
print('\nECHECS:', fails if fails else 'aucun')
sys.exit(1 if fails else 0)
