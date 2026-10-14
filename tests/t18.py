"""Test : lecture d'etiquette hors ligne (2026.10.14-4).

  1. parseLabel (src/js4c.js) sur des textes connus : kcal / kJ, deux colonnes (portion d'abord),
     « g » lu comme 9 ou 0, virgule perdue, sodium en mg, valeurs sur des lignes a part, portion seule, vide ;
  2. lecture reelle avec Tesseract.js (vendor/ocr) de fausses etiquettes fabriquees avec PIL :
     nette, deux colonnes, floue et penchee ; aucune requete hors du serveur local ; rien de charge
     avant la premiere photo ; sw.js ne precharge pas le moteur ;
  3. feuille de verification : enregistrement dans S.scans (src 'label'), conversion portion -> 100 g ;
  4. forme.html : aucun bouton Photo / Galerie de lecture d'etiquette.

    python3 -m http.server 8765
    python3 tests/t18.py
"""
import json, os, random, re, tempfile
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from playwright.sync_api import sync_playwright

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
rd = lambda *p: open(os.path.join(ROOT, *p), encoding='utf-8').read()
URL = 'http://localhost:8765/'
TMP = tempfile.mkdtemp(prefix='t18_')
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra != '' and not ok else ''))
    if not ok: fails.append(label)

# ---------- fausses etiquettes ----------
def font(sz, bold=False):
    for n in (('arialbd.ttf' if bold else 'arial.ttf'), ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'), '/usr/share/fonts/truetype/dejavu/' + ('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')):
        try: return ImageFont.truetype(n, sz)
        except OSError: pass
    return ImageFont.load_default()
NET = [('Énergie', '1580 kJ / 377 kcal'), ('Matières grasses', '12 g'), ('dont acides gras saturés', '4,1 g'), ('Glucides', '55 g'),
       ('dont sucres', '4,6 g'), ('Fibres alimentaires', '6,5 g'), ('Protéines', '10 g'), ('Sel', '0,85 g')]
NET_V = dict(kcal='377', fat='12', sat='4,1', carbs='55', sugar='4,6', fiber='6,5', prot='10', salt='0,85')
COL2 = [('Énergie', '1854 kJ / 443 kcal', '556 kJ / 133 kcal'), ('Matières grasses', '17 g', '5,1 g'), ('dont acides gras saturés', '4,1 g', '1,2 g'),
        ('Glucides', '62 g', '18,6 g'), ('dont sucres', '24 g', '7,2 g'), ('Fibres alimentaires', '5,2 g', '1,6 g'), ('Protéines', '8,3 g', '2,5 g'), ('Sel', '0,42 g', '0,13 g')]
COL2_V = dict(kcal='443', fat='17', sat='4,1', carbs='62', sugar='24', fiber='5,2', prot='8,3', salt='0,42')
def label_net(path):
    W, H = 900, 60 + len(NET) * 58 + 80
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    d.text((30, 20), 'Valeurs nutritionnelles moyennes', font=font(34, True), fill='black')
    d.text((560, 80), 'Pour 100 g', font=font(30, True), fill='black')
    y = 130
    for a, v in NET:
        d.line((25, y - 8, W - 25, y - 8), fill='black', width=2); d.text((30, y), a, font=font(30), fill='black'); d.text((560, y), v, font=font(30), fill='black'); y += 58
    im.save(path); return path
def label_2col(path):
    W, H = 1100, 60 + len(COL2) * 58 + 90
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    d.text((30, 20), 'Informations nutritionnelles', font=font(34, True), fill='black')
    d.text((520, 80), 'Pour 100 g', font=font(30, True), fill='black'); d.text((780, 80), 'Par portion (30 g)', font=font(30, True), fill='black')
    y = 140
    for a, v, w in COL2:
        d.line((25, y - 8, W - 25, y - 8), fill='black', width=2)
        for x, t in ((30, a), (520, v), (780, w)): d.text((x, y), t, font=font(30), fill='black')
        y += 58
    im.save(path); return path
def label_blur(path):
    im = Image.open(label_net(path + '.png')).convert('L')
    im = im.rotate(3, expand=True, fillcolor=255, resample=Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.3))
    random.seed(1); px = im.load()
    for _ in range(9000):
        x = random.randrange(im.width); y = random.randrange(im.height); px[x, y] = max(0, min(255, px[x, y] + random.randint(-60, 60)))
    im.save(path, quality=70); return path

# parseLabel isole : js4c.js avec ses deux dependances (nf, normTxt), sans l'application
NF = re.search(r'^const nf=.*$', rd('src', 'js1.js'), re.M).group(0)
NORM = re.search(r'^const normTxt=.*$', rd('src', 'js2f.js'), re.M).group(0)
CODE = "const A={},I={},ICON={cam:''},$=s=>document.querySelector(s);" + NF + NORM + rd('src', 'js4c.js') + ';return parseLabel;'
CASES = [
    ('une colonne, kcal', 'Valeurs nutritionnelles pour 100 g\nÉnergie 1580 kJ / 377 kcal\nMatières grasses 12 g\ndont acides gras saturés 4,1 g\nGlucides 55 g\ndont sucres 4,6 g\nFibres alimentaires 6,5 g\nProtéines 10 g\nSel 0,85 g',
     dict(kcal=377, fat=12, sat=4.1, carbs=55, sugar=4.6, fiber=6.5, prot=10, salt=0.85, n=8)),
    ('kJ seul, converti', 'Pour 100 g\nÉnergie 1000 kJ\nMatières grasses 2 g\nGlucides 40 g\nProtéines 15 g', dict(kcal=239, fat=2, carbs=40, prot=15)),
    ('deux colonnes, portion d\'abord', 'Par portion (30 g) Pour 100 g\nÉnergie 556 kJ / 133 kcal 1854 kJ / 443 kcal\nMatières grasses 5,1 g 17 g\nGlucides 18,6 g 62 g\nProtéines 2,5 g 8,3 g',
     dict(kcal=443, fat=17, carbs=62, prot=8.3, portion=30, col=1)),
    ('« g » lu comme 9, corrigé par les calories', 'Pour 100 g\nÉnergie 377 kcal\nMatières grasses 129\nGlucides 55 g\nProtéines 10 g\nFibres 6,5 g', dict(fat=12, carbs=55)),
    ('sodium en mg -> sel', 'Pour 100 g\nÉnergie 200 kcal\nSodium 400 mg', dict(salt=1.0)),
    ('valeurs sur des lignes à part (photo penchée)', 'Pour 100 g\n377 kcal\nMatières grasses 12 g\nGlucides 55 g\n659\nFibres alimentaires\n109\nProtéines\n0859\nSel',
     dict(fiber=6.5, prot=10, salt=0.85)),
    ('« 4,19 » -> 4,1 ; sel « 0,59 » gardé', 'Pour 100 g\nMatières grasses 12 g\ndont saturés 4,19\nSel 0,59', dict(sat=4.1, salt=0.59)),
    ('« < 0,5 g »', 'Pour 100 g\nGlucides 3 g\ndont sucres < 0,5 g', dict(sugar=0.5)),
    ('portion seule', 'Pour une portion de 30 g\nÉnergie 133 kcal', dict(kcal=133, portion=30, basis='portion')),
    ('texte vide', '', dict(n=0)),
]

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- 1. parseLabel ----------
    pg = b.new_page()
    pg.goto(URL + 'manifest.webmanifest')   # une page du serveur local, sans l'application
    pg.evaluate("c=>{window.PL=new Function(c)()}", CODE)
    for label, text, want in CASES:
        r = pg.evaluate("t=>window.PL(t)", text)
        bad = {k: (r.get(k), v) for k, v in want.items() if not (r.get(k) == v or (isinstance(v, float) and r.get(k) is not None and abs(r[k] - v) < 1e-6))}
        check('parseLabel : ' + label, not bad, bad)
    r = pg.evaluate("t=>window.PL(t)", CASES[3][1])
    check('parseLabel : alerte sur la valeur corrigée', any('lu « 129 »' in w for w in r['warn']), r['warn'])
    r = pg.evaluate("t=>window.PL(t)", '')
    check('parseLabel : valeurs manquantes signalées', any(w.startswith('Non trouvé') for w in r['warn']), r['warn'])
    pg.close()

    # ---------- 2 et 3. lecture reelle, telephone ----------
    ctx = b.new_context(viewport={'width': 412, 'height': 900})
    ext = []
    ctx.route(re.compile(r'https?://(?!localhost)'), lambda r: (ext.append(r.request.url), r.abort()))
    pg = ctx.new_page(); errs = []; reqs = []
    pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('request', lambda r: reqs.append(r.url))
    pg.goto(URL + 'index.html'); pg.wait_for_timeout(800)
    check('rien du moteur de lecture au démarrage', not any('vendor/ocr' in u for u in reqs), [u for u in reqs if 'ocr' in u])
    check('sw.js ne précharge pas le moteur', 'ocr' not in re.search(r'const SHELL=\[.*?\]', rd('sw.js')).group(0))
    pg.click('.tab[data-t="food"]'); pg.wait_for_timeout(200)
    def read(path):
        pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(250)
        pg.click('[data-act="add-tab"][data-t="manual"]'); pg.wait_for_timeout(250)
        pg.set_input_files('input[data-ch="ocr-file"]:not([capture])', path)
        pg.wait_for_selector('#lb-kcal', timeout=180000)
        return {k: pg.input_value('#lb-' + k) for k in NET_V}
    got = read(label_net(os.path.join(TMP, 'nette.png')))
    check('étiquette nette : les 8 valeurs justes', got == NET_V, got)
    check('feuille de vérification : photo, nom, avertissement, texte lu', pg.locator('.ocrimg').count() == 1 and pg.locator('#lbn').count() == 1
          and 'Vérifie chaque chiffre' in pg.inner_text('.sheet') and 'Valeurs nutritionnelles' in pg.evaluate("document.querySelector('details pre').textContent"))
    pg.fill('#lbn', 'Céréales du test'); pg.click('[data-act="lb-save"]'); pg.wait_for_timeout(300)
    sc = json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))['scans'][0]
    check('enregistré dans la bibliothèque (src label, pour 100 g)', sc['name'] == 'Céréales du test' and sc['src'] == 'label' and sc['per']['kcal'] == 377 and sc['per']['salt'] == 0.85, sc)
    check('retour au Scanner de la feuille, produit prêt à ajouter', 'Céréales du test' in pg.inner_text('.sheet') and pg.locator('[data-act="bc-add"]').count() == 1)
    pg.evaluate("document.querySelector('#layer').innerHTML=''")
    got = read(label_2col(os.path.join(TMP, 'deux-colonnes.png')))
    ok = sum(got[k] == v for k, v in COL2_V.items())
    check('deux colonnes : colonne 100 g, au moins 7 valeurs sur 8 (%d)' % ok, ok >= 7 and all(got[k] == COL2_V[k] for k in ('kcal', 'fat', 'carbs', 'prot')), got)
    # conversion portion -> 100 g
    pg.click('[data-act="lb-basis"][data-b="portion"]'); pg.fill('#lbpor', '30'); pg.fill('#lb-kcal', '133'); pg.fill('#lb-fat', '5,1')
    pg.fill('#lbn', 'Biscuits du test'); pg.click('[data-act="lb-save"]'); pg.wait_for_timeout(300)
    sc = json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))['scans'][0]
    check('portion de 30 g convertie en 100 g (133 -> 443 kcal, 5,1 -> 17 g)', sc['per']['kcal'] == 443 and sc['per']['fat'] == 17, sc['per'])
    pg.evaluate("document.querySelector('#layer').innerHTML=''")
    got = read(label_blur(os.path.join(TMP, 'floue.jpg')))
    key = sum(got[k] == NET_V[k] for k in ('kcal', 'fat', 'carbs', 'sugar', 'prot'))
    check('floue et penchée : au moins 4 valeurs clés sur 5 (%d)' % key, key >= 4, got)
    check('lecture : aucune requête hors du serveur local (hors polices, bloquées)', not [u for u in ext if 'fonts.g' not in u], ext)
    check('lecture : le moteur vient de vendor/ocr', any(u.endswith('vendor/ocr/tesseract-core-simd-lstm.wasm.js') for u in reqs) and any(u.endswith('fra.traineddata.gz') for u in reqs))
    pg.evaluate("document.querySelector('#layer').innerHTML=''")
    pg.click('.tab[data-t="scan"]'); pg.wait_for_timeout(300)
    check('onglet Scan sans vision : boutons Photo et Galerie', pg.locator('#view input[data-ch="ocr-file"]').count() == 2)
    check('aucune erreur JavaScript (téléphone)', not errs, errs)
    ctx.close()

    # ---------- 4. forme.html ----------
    ctx = b.new_context(viewport={'width': 412, 'height': 900})
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + 'forme.html'); pg.wait_for_timeout(600)
    pg.click('.tab[data-t="food"]'); pg.click('[data-act="f-add"][data-slot="lu"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="add-tab"][data-t="manual"]'); pg.wait_for_timeout(250)
    n1 = pg.locator('input[data-ch="ocr-file"]').count()
    pg.evaluate("document.querySelector('#layer').innerHTML=''"); pg.click('.tab[data-t="scan"]'); pg.wait_for_timeout(300)
    check('forme.html : aucun bouton de lecture d\'étiquette', n1 == 0 and pg.locator('input[data-ch="ocr-file"]').count() == 0)
    check('aucune erreur JavaScript (forme.html)', not errs, errs)
    ctx.close()
    b.close()

print('\n%d echec(s) : %s' % (len(fails), fails) if fails else '\nTOUT EST OK')
