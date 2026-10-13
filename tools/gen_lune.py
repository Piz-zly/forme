"""Génère le décor « Lune » de Forme : ciel étoilé, grande lune lavande au trait d'encre,
nuages japonais en volutes.

Dessin original, tracé par ce script (aucune image tierce).
Imprime un fragment <div class="ln">…</div> ; tools/gen_decor.py l'insère dans src/p1.html.
"""
import math, random

R = random.Random(11)
PREC = [1]  # décimales : 0 pour la lune (petits détails, fichier plus léger), 1 ailleurs
f1 = lambda v: (f'{v:.{PREC[0]}f}'.rstrip('0').rstrip('.') if PREC[0] else str(round(v)))


def blob(cx, cy, r, n=22, jit=0.22):
    """Contour irrégulier fermé (mer lunaire)."""
    pts = []
    ph = [R.uniform(0, 6.3) for _ in range(3)]
    sq = R.uniform(.62, .95)
    for k in range(n):
        a = k / n * 2 * math.pi
        rr = r * (1 + jit * (math.sin(2 * a + ph[0]) + .6 * math.sin(3 * a + ph[1]) + .35 * math.sin(5 * a + ph[2])) / 1.95)
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * sq))
    # courbe lisse : milieux + quadratiques
    d = ''
    m = [((pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2) for i in range(n)]
    d = f'M{f1(m[-1][0])} {f1(m[-1][1])}'
    for i in range(n):
        d += f'Q{f1(pts[i][0])} {f1(pts[i][1])} {f1(m[i][0])} {f1(m[i][1])}'
    return d + 'Z'


def sketch(cx, cy, r, n=12):
    """Trait d'encre ouvert, légèrement tremblé, autour d'une forme."""
    a0 = R.uniform(0, 2 * math.pi)
    span = R.uniform(1.6, 4.4)
    pts = []
    for k in range(n):
        a = a0 + span * k / (n - 1)
        rr = r * (1 + R.uniform(-.12, .12))
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * .85))
    return 'M' + ' L'.join(f1(x) + ' ' + f1(y) for x, y in pts)


def ell_arc(cx, cy, rx, ry, rot, a0, a1, n=10):
    """Arc d'ellipse (angles en radians), pour les ombres et reflets des cratères."""
    c, s_ = math.cos(rot), math.sin(rot)
    pts = []
    for k in range(n):
        a = a0 + (a1 - a0) * k / (n - 1)
        x, y = rx * math.cos(a), ry * math.sin(a)
        pts.append((cx + x * c - y * s_, cy + x * s_ + y * c))
    return 'M' + ' L'.join(f1(x) + ' ' + f1(y) for x, y in pts)


def moon():
    C, Rm = 200, 170
    parts = []
    # mers lavande, plus marquées en bas à droite (côté ombre), pointillées
    seas = [(140, 118, 40), (238, 96, 26), (112, 232, 34), (230, 205, 52), (306, 268, 32),
            (176, 300, 28), (282, 150, 18), (88, 168, 16), (336, 196, 22), (210, 352, 24), (160, 190, 12), (262, 330, 14)]
    for cx, cy, r in seas:
        parts.append(f'<path d="{blob(cx, cy, r)}" fill="#B3A2EA" opacity=".42"/>')
        parts.append(f'<path d="{blob(cx + 4, cy + 3, r * .62)}" fill="#9D89DF" opacity=".28"/>')
        parts.append(f'<path d="{blob(cx - r*.25, cy - r*.2, r * .3)}" fill="#C2B4F2" opacity=".35"/>')
        parts.append(f'<path d="{sketch(cx, cy, r * 1.05)}" fill="none" stroke="#4E3E9E" stroke-width="1.3" stroke-linecap="round" opacity=".38"/>')
        if r > 20:
            parts.append(f'<path d="{sketch(cx, cy, r * .9)}" fill="none" stroke="#4E3E9E" stroke-width=".7" stroke-linecap="round" opacity=".3"/>')
        dots = ''.join(f'<circle cx="{f1(cx + R.uniform(-.7, .7) * r)}" cy="{f1(cy + R.uniform(-.55, .55) * r)}" r="{R.choice([.6, .8, 1, 1.2])}"/>' for _ in range(int(r / 3)))
        parts.append(f'<g fill="#6E5AC6" opacity=".35">{dots}</g>')
    # rayons clairs autour d'un cratère jeune
    rx0, ry0 = 268, 296
    rays = []
    for k in range(16):
        a = k / 16 * 2 * math.pi + R.uniform(-.15, .15)
        L = R.uniform(30, 120)
        w = R.uniform(1.2, 3)
        p1 = (rx0 + w * math.cos(a + math.pi / 2), ry0 + w * math.sin(a + math.pi / 2))
        p2 = (rx0 - w * math.cos(a + math.pi / 2), ry0 - w * math.sin(a + math.pi / 2))
        p3 = (rx0 + L * math.cos(a), ry0 + L * math.sin(a))
        rays.append(f'<path d="M{f1(p1[0])} {f1(p1[1])}L{f1(p3[0])} {f1(p3[1])}L{f1(p2[0])} {f1(p2[1])}Z"/>')
    parts.append(f'<g fill="#FFFFFF" opacity=".28">{"".join(rays)}</g>')
    # cratères : fond, ombre intérieure (côté lumière), rebord éclairé (côté opposé), trait d'encre
    craters = [(rx0, ry0, 9)] + [(R.uniform(50, 350), R.uniform(50, 350), R.choice([3, 4, 5, 6, 7, 8, 10, 12, 15])) for _ in range(40)]
    shade, rims, inks = [], [], []
    for cx, cy, r in craters:
        d = math.hypot(cx - C, cy - C)
        if d > Rm - r - 4:
            continue
        rot = math.atan2(cy - C, cx - C)
        squash = max(.38, math.sqrt(max(0, 1 - (d / Rm) ** 2)))  # raccourci près du bord
        rx, ry = r * squash, r
        parts.append(f'<ellipse cx="{f1(cx)}" cy="{f1(cy)}" rx="{f1(rx)}" ry="{f1(ry)}" transform="rotate({f1(math.degrees(rot))} {f1(cx)} {f1(cy)})" fill="#C4B6F1" opacity=".75"/>')
        # ombre : arc côté haut-gauche (la lumière vient d'en haut à gauche)
        la = math.atan2(-1, -1) - rot  # direction de la lumière dans le repère de l'ellipse
        shade.append(f'<path d="{ell_arc(cx, cy, rx * .82, ry * .82, rot, la - 1.3, la + 1.3, 7)}" stroke-width="{max(1, round(r * .28, 1))}"/>')
        rims.append(f'<path d="{ell_arc(cx, cy, rx * 1.04, ry * 1.04, rot, la + math.pi - 1.2, la + math.pi + 1.2, 7)}" stroke-width="{max(.8, round(r * .16, 1))}"/>')
        if r >= 6:
            inks.append(ell_arc(cx, cy, rx * 1.12, ry * 1.12, rot, la - 1.9 + R.uniform(-.3, .3), la + 1.1, 8))
        if r >= 12:  # piton central
            parts.append(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r * .14)}" fill="#F4F0FF" opacity=".8"/>')
    parts.append(f'<g fill="none" stroke="#7A64CF" stroke-linecap="round" opacity=".45">{"".join(shade)}</g>')
    parts.append(f'<g fill="none" stroke="#FFFFFF" stroke-linecap="round" opacity=".62">{"".join(rims)}</g>')
    parts.append(f'<path d="{"".join(inks)}" fill="none" stroke="#4E3E9E" stroke-width=".9" stroke-linecap="round" opacity=".45"/>')
    # petites cupules
    pits = ''.join(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{R.choice([.6, .8, 1, 1.3, 1.6])}"/>'
                   for x, y in ((R.uniform(40, 360), R.uniform(40, 360)) for _ in range(140)) if math.hypot(x - C, y - C) < Rm - 6)
    parts.append(f'<g fill="#8E79DA" opacity=".42">{pits}</g>')
    # hachures croisées dans l'ombre, façon dessin à l'encre
    hatch = []
    for _ in range(34):
        a = R.uniform(-.25, 1.6)  # quart bas-droit
        rr = R.uniform(Rm * .6, Rm * .96)
        x, y = C + rr * math.cos(a), C + rr * math.sin(a)
        L = R.uniform(10, 26)
        for t in (a + math.pi / 2 + R.uniform(-.25, .25), a + math.pi / 2 + .9):
            for k in range(R.randint(2, 4)):
                ox, oy = x + k * 3.6 * math.cos(a), y + k * 3.6 * math.sin(a)
                hatch.append(f'M{f1(ox - L/2*math.cos(t))} {f1(oy - L/2*math.sin(t))}L{f1(ox + L/2*math.cos(t))} {f1(oy + L/2*math.sin(t))}')
            if R.random() < .5:
                break
    parts.append(f'<path d="{"".join(hatch)}" stroke="#5A46B8" stroke-width=".8" stroke-linecap="round" opacity=".26"/>')
    inner = ''.join(parts)
    return ('<svg class="moon" viewBox="-90 -90 580 580">'
            '<defs>'
            '<radialGradient id="lnGlow" cx="200" cy="200" r="290" gradientUnits="userSpaceOnUse"><stop offset=".55" stop-color="#C9B8FF" stop-opacity=".45"/><stop offset=".75" stop-color="#9D84F5" stop-opacity=".16"/><stop offset="1" stop-color="#7C63E8" stop-opacity="0"/></radialGradient>'
            '<radialGradient id="lnMoon" cx="150" cy="135" r="260" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#FDFBFF"/><stop offset=".4" stop-color="#ECE5FF"/><stop offset=".75" stop-color="#CBBDF5"/><stop offset="1" stop-color="#A08BE2"/></radialGradient>'
            '<radialGradient id="lnShade" cx="140" cy="128" r="300" gradientUnits="userSpaceOnUse"><stop offset=".45" stop-color="#4B3A9E" stop-opacity="0"/><stop offset=".8" stop-color="#4B3A9E" stop-opacity=".22"/><stop offset="1" stop-color="#36277F" stop-opacity=".45"/></radialGradient>'
            '<clipPath id="lnClip"><circle cx="200" cy="200" r="170"/></clipPath>'
            '</defs>'
            '<circle cx="200" cy="200" r="290" fill="url(#lnGlow)"/>'
            '<circle cx="200" cy="200" r="170" fill="url(#lnMoon)"/>'
            f'<g clip-path="url(#lnClip)">{inner}<circle cx="200" cy="200" r="170" fill="url(#lnShade)"/></g>'
            '<circle cx="200" cy="200" r="169" fill="none" stroke="#8A74D8" stroke-width="2.5" opacity=".55"/>'
            f'<path d="{ell_arc(200, 200, 167, 167, 0, math.radians(150), math.radians(300), 24)}" fill="none" stroke="#FFFFFF" stroke-width="2.2" stroke-linecap="round" opacity=".75"/>'
            '</svg>')


def spiral(cx, cy, r0, turns, direction, a0=math.pi / 2, n=56):
    pts = []
    T = turns * 2 * math.pi
    for k in range(n):
        t = T * k / (n - 1)
        r = r0 * (1 - .86 * t / T)
        a = a0 + direction * t
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * .9))
    return 'M' + ' L'.join(f1(x) + ' ' + f1(y) for x, y in pts)


def taper(p0, c, p1, w0, n=16):
    """Traînée effilée : courbe quadratique p0 -> p1, largeur w0 -> 0."""
    pts = []
    for k in range(n):
        t = k / (n - 1)
        x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * c[0] + t * t * p1[0]
        y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * c[1] + t * t * p1[1]
        pts.append((x, y))
    L, Rr = [], []
    for i, (x, y) in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        d = math.hypot(dx, dy) or 1
        w = w0 * (1 - i / (n - 1)) ** .8 / 2
        L.append((x - dy / d * w, y + dx / d * w))
        Rr.append((x + dy / d * w, y - dx / d * w))
    poly = L + Rr[::-1]
    return 'M' + ' L'.join(f1(x) + ' ' + f1(y) for x, y in poly) + 'Z'


def star4(x, y, k):
    return (f'M{f1(x)} {f1(y-k)}Q{f1(x+k*.15)} {f1(y-k*.15)} {f1(x+k)} {f1(y)}Q{f1(x+k*.15)} {f1(y+k*.15)} {f1(x)} {f1(y+k)}'
            f'Q{f1(x-k*.15)} {f1(y+k*.15)} {f1(x-k)} {f1(y)}Q{f1(x-k*.15)} {f1(y-k*.15)} {f1(x)} {f1(y-k)}Z')


def cloud(cls, lobes, spiral_left=True):
    """Nuage japonais en deux plans : lobes ornés d'arcs concentriques et de reflets,
    bande à fond plat rayée, grande volute d'un côté, petite volute de l'autre, traînées effilées."""
    base = 62
    OUT = '#2A2063'
    x = 40
    front, back = [], []
    for r in lobes:
        front.append((x + r, base - r * .55, r))
        x += r * 1.45
    end = x + 30
    for i, (cx, cy, r) in enumerate(front[:-1]):  # second plan, décalé vers le haut
        nx = (cx + front[i + 1][0]) / 2
        back.append((nx + 4, cy - r * .55, r * .72))
    g = []
    # halo doux sous le nuage
    g.append(f'<ellipse cx="{f1(end / 2 + 10)}" cy="{base + 4}" rx="{f1(end * .62)}" ry="46" fill="url(#lnHalo)"/>')
    # traînées effilées côté volute
    if spiral_left:
        tails = [taper((36, base + 17), (-10, base + 32), (-80, base + 24), 15), taper((40, base + 5), (0, base + 1), (-52, base + 9), 10)]
        sp1 = spiral(26, base - 4, 19, 1.35, +1)
        sp2 = spiral(front[-1][0] + front[-1][2] * .6, front[-1][1] - front[-1][2] * .55, 9, 1.2, -1, a0=math.pi)
    else:
        tails = [taper((end - 6, base + 17), (end + 40, base + 32), (end + 110, base + 24), 15), taper((end - 10, base + 5), (end + 30, base + 1), (end + 82, base + 9), 10)]
        sp1 = spiral(end + 4, base - 4, 19, 1.35, -1)
        sp2 = spiral(front[0][0] - front[0][2] * .6, front[0][1] - front[0][2] * .55, 9, 1.2, +1, a0=0)
    for tl in tails:
        g.append(f'<path d="{tl}" fill="url(#lnBand)" stroke="{OUT}" stroke-width="1.8" stroke-linejoin="round"/>')
    band = f'M30 {base}H{f1(end)}a14 14 0 0 1 0 22H30a11 11 0 0 1 0-22Z'

    def lobe_set(items, grad):
        o = ''.join(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r + 3)}"/>' for cx, cy, r in items)
        f = ''.join(f'<circle cx="{f1(cx)}" cy="{f1(cy)}" r="{f1(r)}"/>' for cx, cy, r in items)
        return f'<g fill="{OUT}">{o}</g><g fill="url(#{grad})">{f}</g>'

    def ornaments(items, op):
        o = []
        for cx, cy, r in items:
            for k, w in ((.8, 2.2), (.58, 1.8), (.36, 1.4)):
                rr = r * k
                o.append(f'<path d="M{f1(cx - rr)} {f1(cy + rr*.2)}A{f1(rr)} {f1(rr)} 0 0 1 {f1(cx + rr*.92)} {f1(cy - rr*.05)}" fill="none" stroke="#F3EEFF" stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>')
            # reflet en croissant en haut à gauche du lobe
            o.append(f'<path d="{ell_arc(cx, cy, r * .9, r * .9, 0, math.radians(195), math.radians(265), 8)}" fill="none" stroke="#FFFFFF" stroke-width="{f1(r * .14)}" stroke-linecap="round" opacity=".45"/>')
        return ''.join(o)

    g.append(lobe_set(back, 'lnClB'))
    g.append(ornaments(back, .35))
    g.append(f'<path d="{band}" fill="{OUT}" stroke="{OUT}" stroke-width="6"/>')
    g.append(f'<path d="{sp1}" fill="none" stroke="{OUT}" stroke-width="12" stroke-linecap="round"/>')
    g.append(f'<path d="{sp2}" fill="none" stroke="{OUT}" stroke-width="9" stroke-linecap="round"/>')
    g.append(lobe_set(front, 'lnCl'))
    g.append(f'<path d="{band}" fill="url(#lnBand)"/>')
    for sp, w in ((sp1, 7), (sp2, 5)):
        g.append(f'<path d="{sp}" fill="none" stroke="url(#lnCl)" stroke-width="{w}" stroke-linecap="round"/>')
        g.append(f'<path d="{sp}" fill="none" stroke="#F3EEFF" stroke-width="1.5" stroke-linecap="round" opacity=".65"/>')
    g.append(ornaments(front, .6))
    # rayures de la bande et petit pointillé
    g.append(f'<path d="M44 {base + 7}H{f1(end - 6)}M50 {base + 15}H{f1(end - 14)}" stroke="#F3EEFF" stroke-width="1.6" stroke-linecap="round" opacity=".4"/>')
    g.append('<g fill="#F3EEFF" opacity=".5">' + ''.join(f'<circle cx="{f1(xx)}" cy="{base + 11}" r=".9"/>' for xx in range(56, int(end - 16), 9)) + '</g>')
    # quelques éclats autour
    sx = [(-30, base - 40, 4), (end * .55, -14, 3.2), (end + 30, base - 34, 3.6)]
    g.append('<g fill="#F3EEFF" opacity=".85">' + ''.join(f'<path d="{star4(a, b, k)}"/>' for a, b, k in sx) + '</g>')
    return f'<svg class="{cls}" viewBox="-90 -40 {f1(end + 210)} 150">{"".join(g)}</svg>'


def stars():
    s = []
    for _ in range(120):
        x, y = R.uniform(0, 400), R.uniform(0, 860)
        r = R.choice([.5, .6, .7, .8, 1, 1.2])
        s.append(f'<circle cx="{f1(x)}" cy="{f1(y)}" r="{r}" fill="#F3EFFF" opacity="{R.uniform(.35, .95):.2f}"/>')
    # quelques étoiles à quatre branches
    for _ in range(7):
        x, y, k = R.uniform(20, 380), R.uniform(30, 820), R.uniform(3, 6)
        s.append(f'<path d="M{f1(x)} {f1(y-k)}Q{f1(x+.8)} {f1(y-.8)} {f1(x+k)} {f1(y)}Q{f1(x+.8)} {f1(y+.8)} {f1(x)} {f1(y+k)}Q{f1(x-.8)} {f1(y+.8)} {f1(x-k)} {f1(y)}Q{f1(x-.8)} {f1(y-.8)} {f1(x)} {f1(y-k)}Z" fill="#E6DEFF" opacity=".9"/>')
    return f'<svg class="stars" viewBox="0 0 400 860" preserveAspectRatio="xMidYMid slice">{"".join(s)}</svg>'


DEFS = ('<svg width="0" height="0" style="position:absolute"><defs>'
        '<linearGradient id="lnCl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E7D8FF"/><stop offset=".3" stop-color="#BCA9F7"/><stop offset=".7" stop-color="#8B78E0"/><stop offset="1" stop-color="#6553C2"/></linearGradient>'
        '<linearGradient id="lnClB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#A996EE"/><stop offset=".6" stop-color="#7461CC"/><stop offset="1" stop-color="#4F3FA8"/></linearGradient>'
        '<linearGradient id="lnBand" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#B7A6F6"/><stop offset=".55" stop-color="#8670DC"/><stop offset="1" stop-color="#5A48B6"/></linearGradient>'
        '<radialGradient id="lnHalo"><stop offset="0" stop-color="#E9A6E0" stop-opacity=".22"/><stop offset=".6" stop-color="#9D84F5" stop-opacity=".1"/><stop offset="1" stop-color="#9D84F5" stop-opacity="0"/></radialGradient>'
        '</defs></svg>')

if __name__ == '__main__':
    PREC[0] = 0
    m = moon()
    PREC[0] = 1
    print('<div class="ln">' + DEFS + stars() + m
          + cloud('cl cl1', [26, 34, 22, 18], spiral_left=True)
          + cloud('cl cl2', [22, 30, 24], spiral_left=False)
          + '</div>')
