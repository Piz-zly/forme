#!/usr/bin/env python3
"""Fabrique src/js1c.js : les seules icônes SVG utilisées par Forme, recopiées depuis les paquets
Iconify (jamais la bibliothèque entière).

    python tools/gen_icones.py <dossier-des-paquets-npm-téléchargés>
    (puis ./src/build.sh)

Le dossier peut venir de `npm pack` (paquets décompressés) ou de `npm install --prefix <dossier>`,
toujours HORS du projet. Le script y cherche les fichiers icons.json des paquets :
  ph           @iconify-json/ph                 Phosphor Icons, MIT
  fluent       @iconify-json/fluent-emoji       Fluent Emoji (Microsoft), style Color, MIT
  fluent-flat  @iconify-json/fluent-emoji-flat  Fluent Emoji (Microsoft), style Flat, MIT
  game         @iconify-json/game-icons         Game-icons.net, CC BY 3.0 (citer les auteurs)

Pour ajouter une icône : une ligne dans ICONES ci-dessous, relancer le script, puis le build.
Phosphor et Game-icons dessinent en currentColor (couleur du texte) ; Fluent garde ses couleurs.
Dans l'appli : icon('nom', 'classe', taille) renvoie la balise <svg aria-hidden="true">.
"""
import json, os, sys

# nom dans l'application -> (jeu, nom de l'icône dans le jeu)
ICONES = {
    # barre d'onglets : duotone au repos, pleine sur l'onglet actif
    'onglet-poids':        ('ph', 'scales-duotone'),
    'onglet-poids-actif':  ('ph', 'scales-fill'),
    'onglet-repas':        ('ph', 'fork-knife-duotone'),
    'onglet-repas-actif':  ('ph', 'fork-knife-fill'),
    'onglet-muscu':        ('ph', 'barbell-duotone'),
    'onglet-muscu-actif':  ('ph', 'barbell-fill'),
    'onglet-scan':         ('ph', 'barcode-duotone'),
    'onglet-scan-actif':   ('ph', 'barcode-fill'),
    # boutons
    'reglages':            ('ph', 'gear-six'),
    'plus':                ('ph', 'plus-bold'),
    'droite':              ('ph', 'caret-right-bold'),
    'gauche':              ('ph', 'caret-left-bold'),
    'ouvrir':              ('ph', 'caret-down-bold'),
    'coche':               ('ph', 'check-bold'),
    'photo':               ('ph', 'camera-bold'),
    'fermer':              ('ph', 'x-bold'),
    'menu':                ('ph', 'dots-three-bold'),
    'minuteur':            ('ph', 'timer-bold'),
    # repas (Fluent, style Flat : le style Color pèse 51 ko pour ces 4 icônes)
    'repas-bk':            ('fluent-flat', 'hot-beverage'),
    'repas-lu':            ('fluent-flat', 'green-salad'),
    'repas-di':            ('fluent-flat', 'shallow-pan-of-food'),
    'repas-sn':            ('fluent-flat', 'red-apple'),
}

PAQUETS = {'ph': '@iconify-json/ph', 'fluent': '@iconify-json/fluent-emoji',
           'fluent-flat': '@iconify-json/fluent-emoji-flat', 'game': '@iconify-json/game-icons'}
LICENCES = {'ph': 'Phosphor Icons (github.com/phosphor-icons/core), MIT',
            'fluent': 'Fluent Emoji, Microsoft (github.com/microsoft/fluentui-emoji), MIT',
            'fluent-flat': 'Fluent Emoji, Microsoft (github.com/microsoft/fluentui-emoji), MIT',
            'game': 'Game-icons.net (github.com/game-icons/icons), CC BY 3.0, auteurs dans THIRD_PARTY.txt'}


def trouve_paquets(racine, voulus):
    """jeu -> (version, données icons.json) pour chaque jeu utilisé"""
    noms = {PAQUETS[j]: j for j in voulus}
    out = {}
    for d, _, fichiers in os.walk(racine):
        if 'icons.json' in fichiers and 'package.json' in fichiers:
            with open(os.path.join(d, 'package.json'), encoding='utf-8') as f:
                p = json.load(f)
            if p.get('name') in noms:
                with open(os.path.join(d, 'icons.json'), encoding='utf-8') as f:
                    out[noms[p['name']]] = (p.get('version', '?'), json.load(f))
    manque = [PAQUETS[j] for j in voulus if j not in out]
    if manque:
        sys.exit('Paquet introuvable dans %s : %s' % (racine, ', '.join(manque)))
    return out


def icone(data, nom):
    """(viewBox, contenu SVG) ; suit les alias simples (sans rotation ni retournement)"""
    icons, alias = data['icons'], data.get('aliases', {})
    vu = nom
    while vu not in icons:
        a = alias.get(vu)
        if not a:
            return None
        if any(k in a for k in ('rotate', 'hFlip', 'vFlip')):
            sys.exit('Alias transformé non géré : %s' % nom)
        vu = a['parent']
    i = icons[vu]
    w, h = i.get('width', data.get('width', 16)), i.get('height', data.get('height', 16))
    return '%s %s %s %s' % (i.get('left', 0), i.get('top', 0), w, h), i['body']


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    jeux = sorted({j for j, _ in ICONES.values()})
    paquets = trouve_paquets(sys.argv[1], jeux)
    sortie, erreurs = {}, []
    for nom, (jeu, ico) in ICONES.items():
        r = icone(paquets[jeu][1], ico)
        if r is None:
            erreurs.append('%s : « %s » absent du jeu %s' % (nom, ico, PAQUETS[jeu]))
        else:
            sortie[nom] = r
    if erreurs:
        sys.exit('Icônes introuvables :\n  ' + '\n  '.join(erreurs))
    tete = ['/* ===== ICÔNES : GÉNÉRÉ par tools/gen_icones.py, ne pas éditer =====',
            '   Seules les icônes utilisées sont recopiées. Sources et licences :']
    tete += ['   - %s, paquet %s %s' % (LICENCES[j], PAQUETS[j], paquets[j][0]) for j in jeux]
    tete += ['   Textes complets des licences : THIRD_PARTY.txt et vendor/. */']
    corps = ',\n'.join('  %s:%s' % (json.dumps(n), json.dumps(list(v), ensure_ascii=False, separators=(',', ':'))) for n, v in sortie.items())
    js = '\n'.join(tete) + '\nconst ICONS={\n' + corps + '\n};\n' + \
        "/* balise <svg> d'une icône ; taille facultative en px (attribut : le CSS d'un composant reste prioritaire) */\n" + \
        "function icon(n,c,s){const i=ICONS[n];if(!i)return '';return '<svg class=\"ico'+(c?' '+c:'')+'\" viewBox=\"'+i[0]+'\"'+(s?' width=\"'+s+'\" height=\"'+s+'\"':'')+' aria-hidden=\"true\">'+i[1]+'</svg>'}\n"
    dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'js1c.js')
    with open(dest, 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('%d icônes, %d octets -> src/js1c.js' % (len(sortie), len(js.encode('utf-8'))))


if __name__ == '__main__':
    main()
