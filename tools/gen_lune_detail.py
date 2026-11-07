"""Génère une lune détaillée pour le décor « Lune » de Forme (image WebP avec transparence).

Dessin original, calculé par ce script : aucune photo, aucune image tierce.
- Les mers lunaires sont placées aux positions réelles de la face visible (un fait de la nature),
  avec des bords irréguliers et une texture tirées au hasard (graine fixe).
- Cratères en relief (cuvette, rebord, éjectas), éclairage en relief (bump mapping),
  traînées claires autour de Tycho, Copernic, Kepler et Aristarque.
- Teinte au choix : lavande (ambiance Lune), rose (lune rousse), argent.

    python3 tools/gen_lune_detail.py [teinte] [taille] [sortie.webp]
"""
import sys, math
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, map_coordinates, zoom

rng = np.random.default_rng(7)


def fbm(h, w, octaves=6, base=4, persistence=.55, seed=0):
    """Bruit fractal dans [0,1] (somme de bruits lissés)."""
    g = np.random.default_rng(seed)
    out = np.zeros((h, w)); amp = 1; tot = 0
    for o in range(octaves):
        k = base * 2 ** o
        a = g.random((k // 2 + 2, k + 2))
        z = zoom(a, (h / (k // 2 + 2) * 1.0001, w / (k + 2) * 1.0001), order=3)[:h, :w]
        out += amp * z; tot += amp; amp *= persistence
    out /= tot
    return (out - out.min()) / (out.max() - out.min())


def render(N=640, tint='lavande'):
    R = N / 2 - 1.5
    y, x = np.mgrid[0:N, 0:N]
    X = (x - N / 2 + .5) / R
    Y = -(y - N / 2 + .5) / R            # nord en haut
    r2 = X ** 2 + Y ** 2
    inside = r2 <= 1
    Z = np.sqrt(np.clip(1 - r2, 0, 1))
    P = np.stack([X, Y, Z], -1)          # point sur la sphère (Z vers nous)
    lon = np.degrees(np.arctan2(X, Z))
    lat = np.degrees(np.arcsin(np.clip(Y, -1, 1)))

    # --- carte en longitude / latitude : bruit pour texture et bords des mers ---
    MW, MH = 1024, 512
    tex = fbm(MH, MW, 7, 4, .55, seed=1)
    warp1 = fbm(MH, MW, 5, 3, .6, seed=2) - .5
    warp2 = fbm(MH, MW, 5, 3, .6, seed=3) - .5
    mott = fbm(MH, MW, 6, 8, .6, seed=4)
    warp3 = fbm(MH, MW, 5, 12, .6, seed=5) - .5
    speck = fbm(MH, MW, 3, 96, .6, seed=6)
    warp4 = fbm(MH, MW, 4, 24, .6, seed=8) - .5
    def sample(m):
        u = (lon + 180) / 360 * (MW - 1)
        v = (90 - lat) / 180 * (MH - 1)
        return map_coordinates(m, [v, u], order=1, mode='wrap')
    T, W1, W2, MO, W3, SP, W4 = sample(tex), sample(warp1), sample(warp2), sample(mott), sample(warp3), sample(speck), sample(warp4)

    def unit(lo, la):
        lo, la = math.radians(lo), math.radians(la)
        return np.array([math.sin(lo) * math.cos(la), math.sin(la), math.cos(lo) * math.cos(la)])

    def angdist(c):
        return np.degrees(np.arccos(np.clip(P @ c, -1, 1)))

    # --- mers (positions réelles approchées) : (longitude, latitude, rayon°, étirement nord-sud) ---
    MARIA = [
        (-57, 18, 24, 1.5), (-62, 0, 16, 1.2), (-48, 32, 14, 1), (-45, 8, 12, 1), (-66, 30, 10, 1), (-52, -8, 10, 1),       # Océan des Tempêtes
        (-16, 34, 17, 1), (-22, 42, 10, 1),                             # mer des Pluies
        (17, 28, 10, 1), (31, 8, 11, 1), (24, 2, 8, 1),                 # Sérénité, Tranquillité
        (59, 17, 7, .8), (51, -8, 8, 1.3), (34, -15, 5, 1),             # Crises, Fécondité, Nectar
        (-17, -20, 9, 1), (-39, -24, 6, 1), (-23, -10, 6, 1),           # Nuées, Humeurs, Connue
        (-31, 7, 8, 1), (4, 13, 5, 1), (0, 2, 4, 1),                    # Îles, Vapeurs, golfe Central
        (-35, 57, 7, .45), (-20, 56, 7, .45), (-5, 57, 7, .45), (10, 56, 7, .45), (25, 57, 7, .45), (40, 58, 6, .45),  # mer du Froid
        (86, 2, 6, 1.3), (-80, -18, 4, 1),                              # Smyth, Orientale (bord)
    ]
    mare = np.zeros_like(X)
    tone = np.full_like(X, .44)
    for lo, la, rad, st in MARIA:
        dark = rng.uniform(.38, .50)
        c = unit(lo, la)
        d = angdist(c)
        # étirement nord-sud : on réduit l'écart de latitude
        dl = (lat - la) / st
        dd = np.sqrt(np.maximum(d ** 2 - (lat - la) ** 2, 0) + dl ** 2)
        t = dd / rad + W1 * 1.1 + W2 * .7 + W3 * 1.4 + W4 * .7
        m = np.clip((1.1 - t) / .35, 0, 1)
        tone = np.where(m > mare, dark, tone)
        mare = np.maximum(mare, m)
    mare = gaussian_filter(mare, N / 300); tone = gaussian_filter(tone, N / 60)

    # --- albédo de base ---
    high = .72 + (T - .5) * .26 + (MO - .5) * .1 + (SP - .5) * .16
    sea = tone + (MO - .5) * .26 + (W3 + .5 - .5) * .12 + (SP - .5) * .07
    alb = high * (1 - mare) + sea * mare

    # --- cratères : hauteur + éjectas clairs ---
    H = np.zeros_like(X)
    bright = np.zeros_like(X)
    def crater(lo, la, rad_deg, depth=1.0, ejecta=.12):
        c = unit(lo, la)
        cx = N / 2 + c[0] * R; cy = N / 2 - c[1] * R
        rpx = math.radians(rad_deg) * R * 2.2 + 3
        x0, x1 = int(max(cx - rpx, 0)), int(min(cx + rpx + 1, N))
        y0, y1 = int(max(cy - rpx, 0)), int(min(cy + rpx + 1, N))
        if x1 <= x0 or y1 <= y0 or c[2] < .05:
            return
        sl = (slice(y0, y1), slice(x0, x1))
        d = np.degrees(np.arccos(np.clip(P[sl] @ c, -1, 1))) / rad_deg
        bowl = np.where(d < 1, (d ** 2 - 1) * .9, 0)
        rim = np.exp(-((d - 1) / .25) ** 2) * .15
        H[sl] += depth * rad_deg * (bowl + rim)
        bright[sl] += ejecta * np.exp(-np.maximum(d - .9, 0) / .5) * (d < 2.6)

    # grands cratères réels (approchés)
    BIG = [(-11, -43, 4.2, 1, .35), (-20, 10, 4.5, 1, .3), (-38, 8, 1.6, 1, .35), (-47, 24, 1.8, 1, .55),
           (-9, -50, 5, .8, .05), (-1, -58, 3.5, .8, .05), (-21, -54, 3.4, .8, .05), (60, -6, 2.5, .8, .1),
           (-3, 51, 3, .8, .06), (26, 39, 2.6, .7, .05), (-31, -15, 3.8, .6, .04), (50, -33, 3.7, .8, .06),
           (8, -13, 4.5, .5, .04), (20, -26, 3, .7, .06), (-60, -5, 4.2, .6, .05), (39, 47, 4, .6, .05),
           (77, 20, 2.5, .8, .08), (-7, -15, 2.3, .7, .06), (68, -40, 4, .6, .05), (-73, -32, 3.5, .6, .05)]
    for c in BIG:
        crater(*c)
    # petits cratères au hasard (loi de puissance), plus nombreux sur les hautes terres
    for _ in range(1500):
        lo = rng.uniform(-88, 88); la = math.degrees(math.asin(rng.uniform(-.98, .98)))
        rad = .18 * (1 - rng.random()) ** -0.8
        rad = min(rad, 3.2)
        crater(lo, la, rad, depth=rng.uniform(.3, .8), ejecta=rng.uniform(0, .03))

    for _ in range(5000):
        lo = rng.uniform(-88, 88); la = math.degrees(math.asin(rng.uniform(-.98, .98)))
        crater(lo, la, rng.uniform(.12, .45), depth=rng.uniform(.5, 1.2), ejecta=rng.uniform(0, .02))
    # petits points clairs (cratères jeunes vus à la pleine lune)
    spots = np.zeros((N, N))
    for _ in range(420):
        lo = rng.uniform(-85, 85); la = math.degrees(math.asin(rng.uniform(-.97, .97)))
        c = unit(lo, la)
        px, py = int(N / 2 + c[0] * R), int(N / 2 - c[1] * R)
        if 0 <= px < N and 0 <= py < N and c[2] > .1:
            spots[py, px] += rng.uniform(.15, 1) ** 3
    spots = gaussian_filter(spots, N / 600) * (N / 120) ** 2 * .22
    # --- traînées claires (rayons) ---
    rays = np.zeros_like(X)
    for lo, la, n, reach, strength in [(-11, -43, 16, 85, .9), (-20, 10, 18, 30, .4),
                                        (-38, 8, 18, 18, .3), (-47, 24, 14, 14, .3), (60, -6, 10, 14, .15)]:
        c = unit(lo, la)
        d = angdist(c)
        # azimut autour du cratère
        north = np.array([0, 1, 0]) - c * c[1]; north /= np.linalg.norm(north)
        east = np.cross(north, c)
        v = P - (P @ c)[..., None] * c
        az = np.arctan2(v @ east, v @ north)
        acc = np.zeros_like(X)
        for k in range(n):
            a0 = rng.uniform(-math.pi, math.pi)
            w = rng.uniform(.02, .07)
            ln = reach * rng.uniform(.25, 1)
            st = rng.uniform(.35, 1)
            da = np.angle(np.exp(1j * (az - a0)))
            width = w * (1 + d / 18) * (.7 + .6 * W4 + .3)
            acc = np.maximum(acc, st * np.exp(-(da / width) ** 2) * np.clip(1 - d / ln, 0, 1) ** 1.2 * np.clip((d - 2) / 6, 0, 1))
        rays += strength * gaussian_filter(acc, N / 500) * (.3 + 1.2 * MO)
    alb = alb + rays * .5 + bright * .6 + np.clip(spots, 0, .45) * (1 - .5 * mare)
    alb = alb * (.9 + .2 * MO * (1 - mare))
    alb = alb * (1 + gaussian_filter(rng.normal(0, 1, alb.shape), .7) * .06)

    # --- éclairage en relief ---
    Hs = gaussian_filter(H, .7)
    gy, gx = np.gradient(Hs)
    k = N / 900
    nx, ny = X - gx * k, Y + gy * k
    nz = Z
    nl = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2) + 1e-9
    L = np.array([-.32, .18, 1]); L /= np.linalg.norm(L)
    lam = np.clip((nx * L[0] + ny * L[1] + nz * L[2]) / nl, 0, 1)
    limb = .55 + .45 * Z ** .35
    I = alb * (.35 + .75 * lam) * limb
    I = np.clip(I / np.percentile(I[inside], 99.6), 0, 1)
    I = I ** .9

    # --- teinte ---
    PAL = {
        'lavande': [(0, (34, 26, 72)), (.45, (120, 100, 200)), (.75, (200, 186, 250)), (1, (250, 246, 255))],
        'rose':    [(0, (70, 16, 34)), (.45, (196, 74, 84)), (.75, (246, 160, 148)), (1, (255, 238, 228))],
        'argent':  [(0, (40, 40, 56)), (.5, (140, 140, 160)), (1, (248, 248, 255))],
    }[tint]
    rgb = np.zeros((N, N, 3))
    for c in range(3):
        rgb[..., c] = np.interp(I, [p for p, _ in PAL], [col[c] for _, col in PAL])
    # bord adouci
    edge = np.clip((1 - np.sqrt(r2)) * R / 1.2, 0, 1)
    a = (edge * 255).astype(np.uint8)
    img = np.dstack([rgb.astype(np.uint8), a])
    return Image.fromarray(img, 'RGBA')


if __name__ == '__main__':
    tint = sys.argv[1] if len(sys.argv) > 1 else 'lavande'
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 640
    out = sys.argv[3] if len(sys.argv) > 3 else f'lune-{tint}.webp'
    im = render(int(N * 1.5), tint).resize((N, N), Image.LANCZOS)
    im.save(out, 'WEBP', quality=82, method=6)
    print(out)
