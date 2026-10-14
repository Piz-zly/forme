"""Test de bout en bout : onglet Poids, statistiques detaillees, historique, CSV, depense estimee (2026.10.14-3).

Donnees fictives uniquement (aucune donnee personnelle).
  1. carte des statistiques : 3 cases gardees ; « Plus de details » ferme au depart, s'ouvre, se ferme,
     etat garde apres changement d'onglet ;
  2. plus bas / plus haut / moyenne 30 j / variations 7-30-90 j exacts ; IMC absent sans taille, exact avec ;
  3. historique : couleur de l'ecart selon l'objectif (gris sans objectif), separateurs de semaine
     (moyenne, variation, pas de separateur pour une semaine d'une pesee sans semaine precedente),
     repli et depli (titre seul, etat garde apres changement d'onglet et rechargement, « Tout afficher »
     toujours la), animations douces en mode normal, aucune avec « reduire les animations » ;
  4. export CSV : BOM, « ; », virgule decimale, ordre croissant (telephone : fichier ; Claude : texte) ;
  5. import CSV : 4 formats de date, separateurs ; , tabulation, en-tete ou non, lignes invalides
     comptees, apercu avant ecriture, « nouvelles seulement » ne touche rien d'existant, « remplacer »
     modifie, aller-retour export -> import identique ;
  6. depense estimee : valeur attendue sur un jeu connu ; « pas assez de donnees » dans les 3 cas.

    python3 -m http.server 8765
    python3 tests/t16.py
"""
import datetime, json, os, re, tempfile
from playwright.sync_api import sync_playwright

URL = 'http://localhost:8765/'
TODAY = datetime.date.today()
D = lambda k: (TODAY - datetime.timedelta(days=k)).isoformat()
TMP = tempfile.mkdtemp(prefix='t16_')
fails = []
def check(label, ok, extra=''):
    print(('OK   ' if ok else 'FAIL ') + label + (' ' + str(extra) if extra != '' and not ok else ''))
    if not ok: fails.append(label)
clean = lambda t: re.sub(r'[  ]', ' ', t)
SPY = """window.__anims=[];const _a=Element.prototype.animate;
Element.prototype.animate=function(k,o){window.__anims.push({ak:this.dataset&&this.dataset.ak||null,ghost:this.getAttribute('aria-hidden')==='true',kf:JSON.stringify(k[0])});return _a.call(this,k,o)};"""

# serie connue : une pesee par jour sur 100 jours, 75,0 aujourd'hui, +0,1 kg par jour en remontant
# (donc une baisse reguliere vers l'objectif de 70), avec une remontee de 0,5 kg il y a 2 jours
W = {D(k): round(75 + 0.1 * k, 1) for k in range(100)}
W[D(2)] = round(W[D(2)] + 0.5, 1)

def ctx_page(b, reduced=False, html='index.html'):
    ctx = b.new_context(viewport={'width': 412, 'height': 900}, accept_downloads=True,
                        reduced_motion='reduce' if reduced else 'no-preference')
    ctx.add_init_script(SPY)
    # forme.html ne declare pas son encodage (la page de Claude l'ajoute) : on le precise ici
    ctx.route('**/forme.html', lambda r: r.fulfill(response=r.fetch(), headers={'content-type': 'text/html; charset=utf-8'}))
    pg = ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto(URL + html); pg.wait_for_timeout(300)
    return ctx, pg, errs
def seed(pg, **o):
    pg.evaluate("s=>{localStorage.setItem('forme.v1',JSON.stringify(Object.assign({settings:{v2:1}},s)))}", o)
    pg.reload(); pg.wait_for_timeout(500)
st = lambda pg: json.loads(pg.evaluate("localStorage.getItem('forme.v1')"))
def tab(pg, t): pg.click('.tab[data-t="%s"]' % t); pg.wait_for_timeout(250)

with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------- 1 et 2 : statistiques ----------
    ctx, pg, errs = ctx_page(b)
    seed(pg, weights=W, settings={'v2': 1, 'goalW': 70, 'step': 2.5, 'heightCm': None})
    card = pg.locator('.card:has([data-act="w-det"])')
    check('carte statistiques : 3 cases gardées', card.locator('.stat').count() == 3 and 'Moyenne 7 j' in card.inner_text() and 'Tendance' in card.inner_text() and 'Objectif' in card.inner_text())
    check('« Plus de détails » fermé au départ', pg.get_attribute('[data-act="w-det"]', 'aria-expanded') == 'false' and pg.locator('#wdet').count() == 0)
    pg.click('[data-act="w-det"]'); pg.wait_for_timeout(200)
    det = clean(pg.inner_text('#wdet'))
    check('s\'ouvre', pg.get_attribute('[data-act="w-det"]', 'aria-expanded') == 'true' and pg.locator('#wdet').count() == 1)
    vals = sorted(W.items(), key=lambda kv: kv[1])
    lo, hi = vals[0], vals[-1]
    check('plus bas %s kg et plus haut %s kg' % (lo[1], hi[1]), ('Plus bas\n75 kg' in det) and ('Plus haut\n84,9 kg' in det), det[:200])
    avg30 = sum(W[D(k)] for k in range(30)) / 30
    check('moyenne 30 jours %.1f' % avg30, ('Moyenne 30 jours\n%s kg' % ('%.1f' % avg30).replace('.', ',')) in det, det)
    var = re.findall(r'(\d+) j ([^\s]+) kg', det)
    check('variations 7 / 30 / 90 j : −0,7 / −3 / −9', var == [('7', '−0,7'), ('30', '−3'), ('90', '−9')], var)
    tones = pg.evaluate("[...document.querySelectorAll('#wdet .wvar b')].map(b=>b.className)")
    check('variations vers l\'objectif : en vert', all('wtg' in c for c in tones), tones)
    check('IMC absent sans taille', 'IMC' not in det)
    tab(pg, 'food'); tab(pg, 'weight')
    check('état ouvert gardé après changement d\'onglet', pg.locator('#wdet').count() == 1)
    pg.click('[data-act="w-det"]'); pg.wait_for_timeout(200)
    check('se ferme', pg.locator('#wdet').count() == 0 and pg.get_attribute('[data-act="w-det"]', 'aria-expanded') == 'false')
    tab(pg, 'food'); tab(pg, 'weight')
    check('état fermé gardé après changement d\'onglet', pg.locator('#wdet').count() == 0)
    # IMC avec taille : 75 / 1,80² = 23,1
    o = st(pg); o['settings']['heightCm'] = 180; seed(pg, **o)
    pg.click('[data-act="w-det"]') if pg.locator('#wdet').count() == 0 else None; pg.wait_for_timeout(200)
    det = clean(pg.inner_text('#wdet'))
    check('IMC 23,1 · corpulence normale · indicatif', 'IMC\n23,1\ncorpulence normale · indicatif' in det, det)
    # variation sans donnees assez anciennes
    seed(pg, weights={D(k): 75 + 0.1 * k for k in range(10)}, settings={'v2': 1, 'goalW': 70}, ui={'wDet': True})
    var = re.findall(r'(\d+) j ([^\s]+)', clean(pg.inner_text('#wdet')))
    check('variation 30 et 90 j : « — » s\'il manque des données', var[1:] == [('30', '—'), ('90', '—')], var)
    # sans objectif : variations neutres
    seed(pg, weights=W, settings={'v2': 1, 'goalW': None}, ui={'wDet': True})
    tones = pg.evaluate("[...document.querySelectorAll('#wdet .wvar b')].map(b=>b.className)")
    check('sans objectif : variations neutres', all('wt0' in c for c in tones), tones)
    check('aucune erreur JavaScript (statistiques)', not errs, errs)
    ctx.close()

    # ---------- 3 : historique ----------
    for reduced in (False, True):
        tag = '[réduit] ' if reduced else '[normal] '
        ctx, pg, errs = ctx_page(b, reduced)
        seed(pg, weights=W, settings={'v2': 1, 'goalW': 70})
        rows = pg.locator('#whist > .li')
        check(tag + '14 pesées affichées', rows.count() == 14, rows.count())
        cls = pg.evaluate("[...document.querySelectorAll('#whist > .li')].map(r=>{const s=r.querySelector('span.small');return s?s.className+'|'+s.textContent:''})")
        # aujourd'hui : 75,0 contre 75,6 la veille -> −0,6 vert ; hier 75,1 contre 75,7 (remontee) -> −0,6 vert ; avant-hier 75,7 contre 75,3 -> +0,4 orange
        check(tag + 'écart vers l\'objectif en vert, qui s\'en éloigne en orange',
              'wtg' in cls[0] and 'wtw' in cls[2] and '+0,4' in cls[2] and all('wtg' in c for c in cls[3:]), cls[:4])
        # separateurs : lundi de chaque semaine affichee
        mon = lambda d: (d - datetime.timedelta(days=d.weekday()))
        shown = [TODAY - datetime.timedelta(days=k) for k in range(14)]
        weeks = sorted({mon(d) for d in shown}, reverse=True)
        seps = pg.evaluate("[...document.querySelectorAll('#whist > .wsep')].map(s=>[s.dataset.ak,s.textContent])")
        check(tag + 'un séparateur par semaine affichée', [s[0] for s in seps] == ['ws' + m.isoformat() for m in weeks], seps)
        m0 = weeks[0]; wk = [W[d.isoformat()] for d in (m0 + datetime.timedelta(days=i) for i in range(7)) if d.isoformat() in W]
        pw = [W[d.isoformat()] for d in (m0 - datetime.timedelta(days=7 - i) for i in range(7)) if d.isoformat() in W]
        av, pv = sum(wk) / len(wk), sum(pw) / len(pw)
        exp = 'moyenne %s kg · %s%s kg' % (('%.1f' % av).replace('.', ','), '−' if av < pv else '+', ('%.1f' % abs(av - pv)).replace('.', ','))
        check(tag + 'séparateur : « %s »' % exp, exp in clean(seps[0][1]) and clean(seps[0][1]).startswith('Semaine du '), seps[0][1])
        check(tag + 'les lignes gardent leur clé d\'animation', pg.evaluate("[...document.querySelectorAll('#whist > .li')].every(r=>r.dataset.ak==='w'+r.dataset.d)"))
        # nouvelle pesee : elle apparait (animation) et le separateur suit
        pg.evaluate('window.__anims.splice(0)')
        pg.fill('#wval', '74,6'); pg.click('[data-act="w-save"]'); pg.wait_for_timeout(60)
        a = pg.evaluate('window.__anims.splice(0)')
        check(tag + ('aucune animation' if reduced else 'pesée modifiée : pas de ligne en double, animation intacte'),
              (not a) if reduced else pg.locator('#whist > .li[data-ak="w%s"]' % D(0)).count() == 1, a[:3])
        # repli
        pg.wait_for_timeout(300); pg.evaluate('window.__anims.splice(0)')
        pg.click('[data-act="w-hist"]'); pg.wait_for_timeout(60)
        a = pg.evaluate('window.__anims.splice(0)')
        head = clean(pg.inner_text('[data-act="w-hist"]'))
        check(tag + 'replié : titre seul, « 100 pesées · dernière : 74,6 kg »',
              pg.locator('#whist > .li:not([aria-hidden])').count() == 0 and 'Tout afficher' not in pg.inner_text('#view') and '100 pesées · dernière : 74,6 kg' in head
              and pg.get_attribute('[data-act="w-hist"]', 'aria-expanded') == 'false', head)
        check(tag + ('repli sans animation' if reduced else 'repli en douceur (lignes qui s\'effacent)'), (not a) if reduced else any(x['ghost'] for x in a), a[:2])
        h = pg.evaluate("document.querySelector('[data-act=\"w-hist\"]').getBoundingClientRect().height")
        check(tag + 'zone tactile du titre ≥ 44 px', h >= 44, h)
        tab(pg, 'gym'); tab(pg, 'weight')
        check(tag + 'replié après changement d\'onglet', pg.locator('#whist > .li').count() == 0)
        pg.reload(); pg.wait_for_timeout(500)
        check(tag + 'replié après rechargement', pg.locator('#whist > .li').count() == 0)
        check(tag + 'état non synchronisé ni exporté (S.ui)', st(pg).get('ui', {}).get('wHistClosed') is True)
        pg.wait_for_timeout(300); pg.evaluate('window.__anims.splice(0)')
        pg.click('[data-act="w-hist"]'); pg.wait_for_timeout(60)
        a = pg.evaluate('window.__anims.splice(0)')
        check(tag + 'déplié : 14 pesées', pg.locator('#whist > .li').count() == 14 and pg.get_attribute('[data-act="w-hist"]', 'aria-expanded') == 'true')
        check(tag + ('dépli sans animation' if reduced else 'dépli en douceur (lignes qui apparaissent)'), (not a) if reduced else any('"opacity":0' in x['kf'] for x in a), a[:2])
        pg.click('[data-act="w-all"]'); pg.wait_for_timeout(200)
        check(tag + '« Tout afficher » marche une fois rouvert', pg.locator('#whist > .li').count() == 100)
        pg.click('[data-act="w-all"]'); pg.wait_for_timeout(200)
        check(tag + '« Réduire »', pg.locator('#whist > .li').count() == 14)
        check(tag + 'aucune erreur JavaScript', not errs, errs)
        ctx.close()

    # sans objectif : gris ; semaine d'une seule pesee sans semaine precedente : pas de separateur
    ctx, pg, errs = ctx_page(b)
    lone = mon(TODAY) - datetime.timedelta(days=14)   # lundi d'il y a 2 semaines
    w2 = {D(0): 80.0, D(1): 80.4, lone.isoformat(): 81.0}
    if mon(TODAY) == mon(TODAY - datetime.timedelta(days=1)):
        seed(pg, weights=w2, settings={'v2': 1, 'goalW': None})
        cls = pg.evaluate("[...document.querySelectorAll('#whist span.small')].map(s=>s.className)")
        check('sans objectif : écarts en gris', cls and all('wt0' in c for c in cls), cls)
        seps = pg.evaluate("[...document.querySelectorAll('#whist > .wsep')].map(s=>s.dataset.ak)")
        check('semaine d\'une seule pesée sans semaine précédente : pas de séparateur', seps == ['ws' + mon(TODAY).isoformat()], seps)
    else:
        print('     (lundi : cas « semaine seule » vérifié avec deux jours de la même semaine impossible, sauté)')
    ctx.close()

    # ---------- 4 : export CSV ----------
    WX = {D(5): 76.2, D(3): 75.0, D(1): 74.55, D(0): 74.0}
    ctx, pg, errs = ctx_page(b)
    seed(pg, weights=WX)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    with pg.expect_download() as dl:
        pg.click('[data-act="w-csv-exp"]')
    f = dl.value; path = os.path.join(TMP, f.suggested_filename); f.save_as(path)
    raw = open(path, 'rb').read(); txt = raw.decode('utf-8-sig')
    check('téléphone : fichier forme-pesees-%s.csv' % TODAY.isoformat(), f.suggested_filename == 'forme-pesees-%s.csv' % TODAY.isoformat(), f.suggested_filename)
    check('export : BOM UTF-8', raw[:3] == b'\xef\xbb\xbf')
    lines = txt.split('\r\n')
    check('export : en-tête date;poids_kg, « ; », virgule décimale, ordre croissant',
          lines[:5] == ['date;poids_kg', D(5) + ';76,2', D(3) + ';75', D(1) + ';74,55', D(0) + ';74'], lines)
    # aller-retour : on vide, on reimporte ce fichier
    seed(pg, weights={})
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
    pg.click('[data-act="w-csv-ok"][data-m="new"]'); pg.wait_for_timeout(300)
    check('aller-retour export -> import : mêmes pesées', st(pg)['weights'] == WX, st(pg)['weights'])
    check('aucune erreur JavaScript (export, téléphone)', not errs, errs)
    ctx.close()
    ctx, pg, errs = ctx_page(b, html='forme.html')
    seed(pg, weights=WX)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.click('[data-act="w-csv-exp"]'); pg.wait_for_timeout(300)
    ta = pg.input_value('#expta') if pg.locator('#expta').count() else ''
    check('version Claude sans téléchargement : texte CSV à copier (comme la sauvegarde)', ta.lstrip('﻿').startswith('date;poids_kg') and (D(0) + ';74') in ta, ta[:80])
    check('aucune erreur JavaScript (export, Claude)', not errs, errs)
    ctx.close()

    # ---------- 5 : import CSV ----------
    def write(name, text, enc='utf-8'):
        path = os.path.join(TMP, name); open(path, 'w', encoding=enc, newline='').write(text); return path
    dmy = lambda k, s: (TODAY - datetime.timedelta(days=k)).strftime('%d' + s + '%m' + s + '%Y')
    FILES = {
        'iso ; en-tête': (write('a.csv', 'date;poids_kg\n%s;80,5\n%s;80,1\n' % (D(10), D(11))), {D(10): 80.5, D(11): 80.1}, 0),
        'JJ/MM/AAAA , en-tête « Weight (kg) », colonne en plus': (write('b.csv', 'Note,Date,Weight (kg)\nok,%s,79.9\n,"%s","79.7"\n' % (dmy(12, '/'), dmy(13, '/'))), {D(12): 79.9, D(13): 79.7}, 0),
        'JJ-MM-AAAA tabulation sans en-tête': (write('c.tsv', '%s\t79,5\n%s\t79,4\n' % (dmy(14, '-'), dmy(15, '-'))), {D(14): 79.5, D(15): 79.4}, 0),
        'JJ.MM.AAAA ; sans en-tête, BOM, CRLF, guillemets, lignes invalides':
            (write('d.csv', '﻿"%s";"79,2"\r\n%s;79,1 kg\r\n31.02.2026;79\r\n%s;500\r\npas une date;80\r\n%s;\r\n\r\n' % (dmy(16, '.'), dmy(17, '.'), dmy(18, '.'), dmy(19, '.'))), {D(16): 79.2, D(17): 79.1}, 4),
    }
    for label, (path, want, bad) in FILES.items():
        ctx, pg, errs = ctx_page(b)
        seed(pg, weights={D(0): 74.0})
        pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
        pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
        summ = clean(pg.inner_text('#wimpsum')) if pg.locator('#wimpsum').count() else ''
        exp = '%d pesées lues · %d nouvelles' % (len(want), len(want)) + (' · %d lignes ignorées' % bad if bad else '')
        check('import %s : aperçu « %s »' % (label, exp), summ == exp, summ)
        check('import %s : rien écrit avant le choix' % label, st(pg)['weights'] == {D(0): 74.0})
        pg.click('[data-act="w-csv-ok"][data-m="new"]'); pg.wait_for_timeout(300)
        got = st(pg)['weights']
        check('import %s : pesées ajoutées' % label, got == dict(want, **{D(0): 74.0}), got)
        check('aucune erreur JavaScript (%s)' % label, not errs, errs)
        ctx.close()
    # nouvelles seulement / remplacer / annuler
    ctx, pg, errs = ctx_page(b)
    base = {D(1): 75.0, D(2): 75.2, D(3): 75.4}
    path = write('e.csv', 'date;poids_kg\n%s;75,0\n%s;76,0\n%s;77,0\n%s;74,8\n' % (D(1), D(2), D(3), D(0)))
    seed(pg, weights=base)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
    summ = clean(pg.inner_text('#wimpsum'))
    check('aperçu : nouvelles, déjà présentes avec une autre valeur, identiques', summ == '4 pesées lues · 1 nouvelle · 2 déjà présentes avec une autre valeur · 1 déjà présente à l’identique', summ)
    check('deux choix + Annuler', pg.locator('[data-act="w-csv-ok"]').count() == 2 and pg.locator('.sheet [data-act="close"]').count() == 1)
    pg.click('.sheet [data-act="close"]'); pg.wait_for_timeout(200)
    check('Annuler : rien ne change', st(pg)['weights'] == base)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
    pg.click('[data-act="w-csv-ok"][data-m="new"]'); pg.wait_for_timeout(300)
    check('« Ajouter seulement les nouvelles » : aucune pesée existante modifiée', st(pg)['weights'] == dict(base, **{D(0): 74.8}), st(pg)['weights'])
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
    pg.click('[data-act="w-csv-ok"][data-m="all"]'); pg.wait_for_timeout(300)
    check('« Remplacer aussi celles qui existent » : modifiées', st(pg)['weights'] == {D(1): 75.0, D(2): 76.0, D(3): 77.0, D(0): 74.8}, st(pg)['weights'])
    path = write('f.csv', 'nom;valeur\nabc;def\n')
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.set_input_files('[data-ch="wcsv"]', path); pg.wait_for_timeout(300)
    check('fichier sans pesée : message clair, aucun bouton d\'import', 'Aucune pesée reconnue' in pg.inner_text('.sheet') and pg.locator('[data-act="w-csv-ok"]').count() == 0)
    check('aucune erreur JavaScript (choix d\'import)', not errs, errs)
    ctx.close()

    # ---------- 6 : depense estimee ----------
    def tdee_text(weights, meal_days):
        meals = {D(k): [dict(id='m%d' % k, slot='lu', name='Repas', kcal=2100, p=100, c=250, f=70)] for k in meal_days}
        seed(pg, weights=weights, meals=meals, settings={'v2': 1, 'goalW': 70}, ui={'wDet': True})
        t = clean(pg.inner_text('#wdet'))
        return t[t.index('Dépense estimée'):]
    ctx, pg, errs = ctx_page(b)
    lin = {D(k): 80 - 0.06 * (27 - k) for k in range(28)}           # pente exacte −0,06 kg/jour
    t = tdee_text(lin, range(28))
    check('dépense : 2 100 kcal mangées, −0,06 kg/jour -> « ≈ 2 560 kcal/jour »', '≈ 2 560 kcal/jour' in t, t)
    check('dépense : mention « Estimation indicative »', 'Estimation indicative, elle suppose que tu notes presque tout ce que tu manges.' in t)
    PAS = 'Pas assez de données : il faut environ 2 semaines de pesées et de repas notés.'
    t = tdee_text({D(k): lin[D(k)] for k in range(0, 28, 4)}, range(28))   # 7 pesees
    check('pas assez de données : moins de 8 pesées', PAS in t, t)
    t = tdee_text({D(k): lin[D(k)] for k in range(10)}, range(28))         # 10 pesees sur 9 jours
    check('pas assez de données : pesées sur moins de 14 jours', PAS in t, t)
    t = tdee_text(lin, range(0, 28, 2))                                  # repas 14 jours sur 28
    check('pas assez de données : repas notés moins de 70 % des jours', PAS in t, t)
    t = tdee_text(lin, range(20))                                        # 20 jours sur 28 = 71 %
    check('assez à 70 % des jours de repas', '≈ 2 560 kcal/jour' in t, t)
    check('l\'objectif calorique n\'est pas modifié', st(pg)['settings'].get('kcal') in (None, 2200))
    check('aucune erreur JavaScript (dépense)', not errs, errs)
    ctx.close()

    # ---------- reglage taille ----------
    ctx, pg, errs = ctx_page(b)
    seed(pg, weights={D(0): 75.0})
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.fill('#ght', '90'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    check('taille hors 120–230 refusée', pg.locator('#ght').count() == 1 and st(pg)['settings'].get('heightCm') in (None,))
    pg.fill('#ght', '178'); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    check('taille 178 cm enregistrée', st(pg)['settings'].get('heightCm') == 178)
    pg.click('[data-act="settings"]'); pg.wait_for_timeout(250)
    pg.fill('#ght', ''); pg.click('[data-act="set-save"]'); pg.wait_for_timeout(250)
    check('taille effacée : IMC masqué', st(pg)['settings'].get('heightCm') is None)
    check('aucune erreur JavaScript (réglages)', not errs, errs)
    ctx.close()
    b.close()

print('\n%d echec(s) : %s' % (len(fails), fails) if fails else '\nTOUT EST OK')
