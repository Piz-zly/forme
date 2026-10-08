"""Assemble le décor de fond de Forme et l'écrit dans src/p1.html, entre
<!-- deco:debut --> et <!-- deco:fin -->.

    python3 tools/gen_decor.py        (puis ./src/build.sh)

  .sk  ambiance Sakura : branches de cerisier, mont Fuji     (tools/gen_sakura.py)
  .ln  ambiance Lune   : ciel étoilé, lune, nuages en volutes (tools/gen_lune.py)
  .pt  pétales qui tombent (Sakura) ou étoiles qui scintillent (Lune), animés en CSS
Le CSS montre le décor de l'ambiance active (data-theme sur <html>).
Tout est dessiné par ces scripts : aucune image tierce.
"""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
P1 = os.path.join(HERE, '..', 'src', 'p1.html')
run = lambda f: subprocess.run([sys.executable, os.path.join(HERE, f)], check=True, capture_output=True, text=True).stdout.strip()
deco = ('<!-- deco:debut (généré par tools/gen_decor.py) -->\n<div class="deco" aria-hidden="true">'
        + run('gen_sakura.py') + run('gen_lune.py') + '<i class="pt"></i>' * 9 + '</div>\n<!-- deco:fin -->')
s = open(P1, encoding='utf-8').read()
a = s.index('<!-- deco:debut')
b = s.index('<!-- deco:fin -->') + len('<!-- deco:fin -->')
s = s[:a] + deco + s[b:]
open(P1, 'w', encoding='utf-8').write(s)
print('décor écrit dans src/p1.html :', len(deco), 'caractères')
