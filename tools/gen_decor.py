"""Assemble le décor de fond de Forme et l'écrit dans src/p1.html, entre
<!-- deco:debut --> et <!-- deco:fin -->.

    python3 tools/gen_decor.py        (puis ./src/build.sh)

  .sk  ambiance Sakura : branches de cerisier, mont Fuji     (tools/gen_sakura.py)
  .ln  ambiance Lune   : ciel étoilé (tools/gen_lune.py), lune détaillée (tools/gen_lune_detail.py,
       image WebP en data URI), motif Kikkō .kk dessiné en CSS (Pattern Monster, MIT)
  .pt  pétales qui tombent (Sakura) ou étoiles qui scintillent (Lune), animés en CSS
Le CSS montre le décor de l'ambiance active (data-theme sur <html>).
Tout est dessiné par ces scripts : aucune image tierce.
"""
import base64, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
P1 = os.path.join(HERE, '..', 'src', 'p1.html')
run = lambda f, *a: subprocess.run([sys.executable, os.path.join(HERE, f), *a], check=True, capture_output=True, text=True).stdout.strip()


def lune():
    """Lune détaillée lavande (gen_lune_detail.py, numpy + scipy + Pillow, plusieurs minutes), en data URI WebP :
    pas de fichier d'image à part, elle marche hors ligne et dans forme.html."""
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, 'lune.webp')
        run('gen_lune_detail.py', 'lavande', '640', out)
        with open(out, 'rb') as f:
            return 'data:image/webp;base64,' + base64.b64encode(f.read()).decode('ascii')


print('calcul de la lune détaillée : plusieurs minutes…')
ln = run('gen_lune.py')
assert ln.count('src="LUNE"') == 1, 'emplacement de la lune introuvable dans gen_lune.py'
ln = ln.replace('src="LUNE"', 'src="' + lune() + '"')
deco = ('<!-- deco:debut (généré par tools/gen_decor.py) -->\n<div class="deco" aria-hidden="true">'
        + run('gen_sakura.py') + ln + '<i class="pt"></i>' * 9 + '</div>\n<!-- deco:fin -->')
s = open(P1, encoding='utf-8').read()
a = s.index('<!-- deco:debut')
b = s.index('<!-- deco:fin -->') + len('<!-- deco:fin -->')
s = s[:a] + deco + s[b:]
open(P1, 'w', encoding='utf-8', newline='\n').write(s)   # fins de ligne Unix, même sous Windows
print('décor écrit dans src/p1.html :', len(deco), 'caractères')
