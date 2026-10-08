"""Génère le décor « sakura » de Forme : branches de cerisier, fleurs, mont Fuji pâle.

Dessin original, tracé par ce script (aucune image tierce).
Imprime un fragment <div class="sk">…</div> ; tools/gen_decor.py l'insère dans src/p1.html.
"""
import math, random, sys

R = random.Random(7)
f1 = lambda v: f'{v:.1f}'.rstrip('0').rstrip('.')


def catmull(pts, n=10):
    """Courbe lisse passant par les points."""
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(pts[-1])
    return out


def limb(pts, w0, w1):
    """Branche effilée : polygone autour de la courbe, largeur w0 -> w1."""
    c = catmull(pts)
    L, R2 = [], []
    for i, (x, y) in enumerate(c):
        a = c[max(i - 1, 0)]
        b = c[min(i + 1, len(c) - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        t = i / (len(c) - 1)
        w = (w0 + (w1 - w0) * t) / 2
        # léger noueux de l'écorce
        w *= 1 + 0.08 * math.sin(i * 1.7)
        L.append((x + nx * w, y + ny * w))
        R2.append((x - nx * w, y - ny * w))
    poly = L + R2[::-1]
    d = 'M' + ' L'.join(f1(x) + ' ' + f1(y) for x, y in poly) + 'Z'
    return d, c


def flowers_along(c, count, spread, smin, smax, tmin=0.2):
    out = []
    for _ in range(count):
        t = R.uniform(tmin, 1)
        i = int(t * (len(c) - 1))
        x, y = c[i]
        ang = R.uniform(0, 2 * math.pi)
        r = R.uniform(0, spread)
        out.append((x + math.cos(ang) * r, y + math.sin(ang) * r, R.uniform(smin, smax), R.uniform(0, 72), R.random()))
    return out


def svg_branch(cls, vb, limbs, n_flowers, buds, defs=''):
    body = []
    allc = []
    for pts, w0, w1, nf, spread in limbs:
        d, c = limb(pts, w0, w1)
        body.append(f'<path d="{d}" fill="url(#skBark)"/>')
        allc.append((c, nf, spread))
    fl = []
    for c, nf, spread in allc:
        fl += flowers_along(c, nf, spread, 0.62, 1.35)
    # boutons au bout des rameaux
    bd = []
    for c, nf, spread in allc:
        for _ in range(buds):
            t = R.uniform(0.55, 1)
            x, y = c[int(t * (len(c) - 1))]
            x += R.uniform(-9, 9)
            y += R.uniform(-9, 9)
            bd.append(f'<ellipse cx="{f1(x)}" cy="{f1(y)}" rx="2.6" ry="3.6" fill="#EE86A5" transform="rotate({R.randint(0,180)} {f1(x)} {f1(y)})"/>')
    fl.sort(key=lambda f: f[2])  # les petites derrière
    uses = []
    for x, y, s, rot, v in fl:
        sym = '#skA' if v < 0.62 else '#skB'
        uses.append(f'<use href="{sym}" transform="translate({f1(x)} {f1(y)}) rotate({f1(rot)}) scale({s:.2f})"/>')
    return f'<svg class="{cls}" viewBox="{vb}" preserveAspectRatio="xMidYMid meet">{defs}{"".join(body[1:])}{body[0]}{"".join(bd)}{"".join(uses)}</svg>'


# un pétale échancré, la base au centre de la fleur
PETAL = 'M0 0C-6.2-1.8-7.8-7.6-4.4-10.8Q-2.1-11.9 0-9.7Q2.1-11.9 4.4-10.8C7.8-7.6 6.2-1.8 0 0Z'


def flower_symbol(sid, gid):
    petals = ''.join(f'<path d="{PETAL}" fill="url(#{gid})" transform="rotate({k*72})"/>' for k in range(5))
    stam = ''.join(
        f'<line x1="0" y1="0" x2="{f1(3.8*math.cos(a))}" y2="{f1(3.8*math.sin(a))}" stroke="#D9577D" stroke-width=".4" opacity=".8"/>'
        f'<circle cx="{f1(4*math.cos(a))}" cy="{f1(4*math.sin(a))}" r=".6" fill="#E9A23B"/>'
        for a in [i * 2 * math.pi / 7 + 0.3 for i in range(7)])
    return f'<symbol id="{sid}" overflow="visible">{petals}<circle r="2.2" fill="#E0688D"/>{stam}</symbol>'


DEFS = ('<defs>'
        '<radialGradient id="skGa" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="11.5"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".45" stop-color="#FFE3EA"/><stop offset="1" stop-color="#F6B3C6"/></radialGradient>'
        '<radialGradient id="skGb" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="11.5"><stop offset="0" stop-color="#FFF0F4"/><stop offset=".5" stop-color="#F9BFD0"/><stop offset="1" stop-color="#EE8FAC"/></radialGradient>'
        '<linearGradient id="skBark" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6B4A50"/><stop offset="1" stop-color="#3F2A30"/></linearGradient>'
        + flower_symbol('skA', 'skGa') + flower_symbol('skB', 'skGb') +
        '</defs>')

# branche du haut, à droite (viewBox 420 x 330, ancrée en haut à droite)
TOP = svg_branch('br br1', '0 0 420 330', [
    ([(440, -6), (372, 34), (300, 66), (226, 100), (158, 120), (92, 146), (34, 170)], 15, 2.2, 26, 16),
    ([(300, 66), (282, 34), (252, 12), (226, 2)], 5, 1.2, 9, 12),
    ([(226, 100), (208, 146), (186, 182), (170, 214)], 5, 1.2, 11, 13),
    ([(372, 34), (388, 92), (380, 140), (364, 176)], 6, 1.4, 11, 13),
    ([(158, 120), (128, 96), (100, 86)], 3.4, 1, 6, 11),
    ([(92, 146), (72, 186), (66, 214)], 3, 1, 6, 11),
], 0, 2, DEFS)

# branche du bas, à gauche (viewBox 380 x 280, ancrée en bas à gauche)
BOT = svg_branch('br br2', '0 0 380 280', [
    ([(-12, 268), (52, 222), (120, 196), (190, 150), (252, 122), (318, 92), (362, 70)], 13, 2, 22, 15),
    ([(120, 196), (128, 150), (150, 116), (162, 92)], 4.4, 1.1, 10, 12),
    ([(252, 122), (268, 160), (296, 182)], 3.6, 1, 7, 11),
    ([(52, 222), (40, 176), (54, 140)], 4, 1.1, 8, 12),
], 0, 2)

FUJI = ('<svg class="fuji" viewBox="0 0 400 130" preserveAspectRatio="xMidYMax slice">'
        '<defs><linearGradient id="fjG" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A9B9E0"/><stop offset="1" stop-color="#E9E6F4" stop-opacity="0"/></linearGradient></defs>'
        '<path d="M0 130V112C70 108 120 92 168 60L214 26Q230 17 246 26L292 58C336 88 372 100 400 104V130Z" fill="url(#fjG)"/>'
        '<path d="M188 46L214 26Q230 17 246 26L274 44L265 49L257 42L247 51L238 43L229 52L220 43L210 50L200 44L192 49Z" fill="#FFFFFF" opacity=".95"/>'
        '<path d="M0 130V120C60 116 110 112 160 116C220 121 300 112 400 116V130Z" fill="#F3D9E3" opacity=".7"/>'
        '</svg>')

if __name__ == '__main__':
    print(f'<div class="sk">{FUJI}{TOP}{BOT}</div>')
