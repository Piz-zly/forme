"""Recadre les illustrations d'exercices (Open Exercise Illustrations, CC0) au format de ill/.

Atelier HORS du depot (variable FORME_ATELIER, 'oei' par defaut) :
  <atelier>/zones_todo.json   liste [{"id":..., "src":["start","end"] ou ["hold"], "frames":2 ou 1, "m":[...], "s":[...]}]
  <atelier>/src/<id>-<start|end|hold>.webp   images telechargees de la collection
Ecrit dans <atelier>/out/ :
  <id>-0.webp, <id>-1.webp   720 x 480, MEME recadrage pour les deux positions
  <id>-t.webp                vignette carree 176 px

Ensuite : tools/paint.py colore <atelier>/out/<id>-<n>.webp dans <atelier>/red/,
puis on copie dans ill/ : out/<id>-0 -> <id>-0, red/<id>-0 -> <id>-0r, etc.
Voir docs/04-images.md.

    python3 tools/recadre.py                    # tout
    python3 tools/recadre.py bench-press squat  # seulement ces identifiants
"""
import json,os,sys
import numpy as np
from PIL import Image

A=os.environ.get('FORME_ATELIER','oei')
SEUIL=60      # luminosite au-dessus de laquelle un pixel appartient au personnage ou au materiel
MARGE=0.05    # marge autour de la zone utile, en part de sa plus grande dimension
W,H,T=720,480,176
Q=dict(quality=76,method=6)

# defauts des images sources, effaces (en noir) avant recadrage : (x0,y0,x1,y1) en pixels source
NETTOIE={('leg-raises','start'):(0,440,1536,512)}  # bout de pied coupe en bas de l'image

def zone(im):
    """boite (x0,y0,x1,y1) des pixels clairs, en ignorant les points isoles"""
    a=np.asarray(im.convert('L'))>SEUIL
    cols=np.where(a.sum(0)>=3)[0]; rows=np.where(a.sum(1)>=3)[0]
    return cols[0],rows[0],cols[-1]+1,rows[-1]+1

def cadre(box,ratio):
    """agrandit box au rapport largeur/hauteur voulu, centre sur la zone utile"""
    x0,y0,x1,y1=box; m=max(x1-x0,y1-y0)*MARGE
    x0,y0,x1,y1=x0-m,y0-m,x1+m,y1+m
    w,h=x1-x0,y1-y0
    if w/h<ratio: w=h*ratio
    else: h=w/ratio
    cx,cy=(x0+x1)/2,(y0+y1)/2
    return tuple(int(round(v)) for v in (cx-w/2,cy-h/2,cx+w/2,cy+h/2))

def coupe(im,c,size):
    """recadre (le debordement hors de l'image est comble en noir) puis redimensionne"""
    out=Image.new('RGB',(c[2]-c[0],c[3]-c[1]),(0,0,0))
    out.paste(im,(-c[0],-c[1]))
    return out.resize(size,Image.LANCZOS)

def flat(p):
    im=Image.open(p)
    if im.mode in ('RGBA','LA','P'):
        im=im.convert('RGBA'); bg=Image.new('RGBA',im.size,(0,0,0,255)); bg.alpha_composite(im); im=bg
    return im.convert('RGB')

if __name__=='__main__':
    only=set(sys.argv[1:]) or None
    rows=json.load(open(A+'/zones_todo.json',encoding='utf-8'))
    os.makedirs(A+'/out',exist_ok=True); n=0
    for r in rows:
        if only and r['id'] not in only: continue
        ims=[flat('%s/src/%s-%s.webp'%(A,r['id'],f)) for f in r['src']]
        for f,im in zip(r['src'],ims):
            if (r['id'],f) in NETTOIE: im.paste((0,0,0),NETTOIE[(r['id'],f)])
        assert len({im.size for im in ims})==1, r['id']+' : tailles differentes'
        bs=[zone(im) for im in ims]
        u=(min(b[0] for b in bs),min(b[1] for b in bs),max(b[2] for b in bs),max(b[3] for b in bs))
        c=cadre(u,W/H)
        for i,im in enumerate(ims):
            coupe(im,c,(W,H)).save('%s/out/%s-%d.webp'%(A,r['id'],i),'WEBP',**Q)
        coupe(ims[0],cadre(u,1),(T,T)).save('%s/out/%s-t.webp'%(A,r['id']),'WEBP',**Q)
        n+=1
    print('recadres',n)
