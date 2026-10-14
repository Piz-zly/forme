"""Colore en rouge les muscles travailles sur les illustrations d'exercices.

Detecte la posture du personnage (YOLO11x-pose, 17 points), en deduit ou se
trouve chaque muscle, et applique la couleur uniquement sur les pixels clairs
du corps. Voir docs/04-images.md.

    pip install ultralytics pillow numpy
    curl -L -o yolo11x-pose.pt \
      https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-pose.pt
    python3 tools/paint.py                    # toutes les illustrations
    python3 tools/paint.py bench-press squat  # seulement ces identifiants

Chemins : un dossier d'atelier HORS du depot (variable FORME_ATELIER, 'oei' par
defaut) qui contient zones_todo.json et out/ (images recadrees par
tools/recadre.py) ; les images colorees sont ecrites dans <atelier>/red/.
Le modele est cherche dans FORME_YOLO ('yolo11x-pose.pt' par defaut) : ne
jamais l'ajouter au depot.
"""
import json,os,math,sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from ultralytics import YOLO
A=os.environ.get('FORME_ATELIER','oei')
D=A+'/out'
rows=json.load(open(A+'/zones_todo.json',encoding='utf-8'))
model=YOLO(os.environ.get('FORME_YOLO','yolo11x-pose.pt'))
L={'nose':0,'LS':5,'RS':6,'LE':7,'RE':8,'LW':9,'RW':10,'LH':11,'RH':12,'LK':13,'RK':14,'LA':15,'RA':16}
def mid(a,b):return ((a[0]+b[0])/2,(a[1]+b[1])/2)
def lerp(a,b,t):return (a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t)
def dist(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
def zones(P,C,muscle):
    """renvoie une liste de formes : ('c',cx,cy,r) cercle, ('s',ax,ay,bx,by,w) segment"""
    g=lambda k: P[L[k]] if C[L[k]]>0.3 else None
    LS,RS,LH,RH=g('LS'),g('RS'),g('LH'),g('RH')
    sh = mid(LS,RS) if LS and RS else (LS or RS)
    hp = mid(LH,RH) if LH and RH else (LH or RH)
    if not sh or not hp: return []
    T=max(dist(sh,hp),1e-6)
    out=[]
    def seg(a,b,t0,t1,k,lo=0.10,hi=0.30):
        A,B=g(a),g(b)
        if not(A and B):return
        d=dist(A,B)
        if d<1e-6:return
        out.append(('s',*lerp(A,B,t0),*lerp(A,B,t1),min(max(d*k,T*lo),T*hi)))
    m=muscle
    if m=='Pectoraux': out.append(('c',*lerp(sh,hp,0.30), T*0.40))
    elif m=='Abdominaux': out.append(('c',*lerp(sh,hp,0.66), T*0.34))
    elif m=='Grand dorsal': out.append(('c',*lerp(sh,hp,0.38), T*0.44))
    elif m=='Milieu du dos': out.append(('c',*lerp(sh,hp,0.30), T*0.40))
    elif m=='Trapèzes': out.append(('c',*lerp(sh,hp,-0.08), T*0.28))
    elif m=='Lombaires': out.append(('c',*lerp(sh,hp,0.84), T*0.32))
    elif m=='Épaules':
        for k in ('LS','RS'):
            p=g(k)
            if p: out.append(('c',*p, T*0.24))
    elif m in ('Biceps','Triceps'):
        seg('LS','LE',0.28,0.96,0.31,0.08,0.19); seg('RS','RE',0.28,0.96,0.31,0.08,0.19)
    elif m=='Avant-bras':
        seg('LE','LW',0.12,0.90,0.32,0.07,0.18); seg('RE','RW',0.12,0.90,0.32,0.07,0.18)
    elif m in ('Quadriceps','Ischio-jambiers'):
        seg('LH','LK',0.36,0.96,0.48,0.13,0.36); seg('RH','RK',0.36,0.96,0.48,0.13,0.36)
    elif m=='Fessiers':
        seg('LH','LK',0.02,0.32,0.50,0.13,0.34); seg('RH','RK',0.02,0.32,0.50,0.13,0.34)
    elif m=='Mollets':
        seg('LK','LA',0.08,0.78,0.44,0.10,0.28); seg('RK','RA',0.08,0.78,0.44,0.10,0.28)
    elif m in ('Adducteurs','Abducteurs'):
        # interieur (adducteurs) ou exterieur (abducteurs) de la cuisse : la capsule
        # hanche->genou est decalee vers l'axe du corps ou vers l'exterieur
        kn=[g(k) for k in ('LK','RK')]; km=mid(*kn) if all(kn) else None
        for h,k in (('LH','LK'),('RH','RK')):
            H,K=g(h),g(k)
            if not(H and K):continue
            if m=='Adducteurs':
                a=lerp(H,hp,0.35); b=lerp(lerp(H,K,0.70),km,0.25) if km else lerp(H,K,0.70)
            else:
                a=lerp(H,hp,-0.30); b=lerp(H,K,0.45)
            out.append(('s',*a,*b,min(max(dist(H,K)*0.34,T*0.10),T*0.26)))
    return out
def pose(im):
    """points (x,y) et confiances de la personne la plus grande, ou None"""
    r=model(im,verbose=False,conf=0.10)[0]
    kp=r.keypoints
    if kp is None or kp.xy is None or len(kp.xy)==0: return None
    bi=0
    if r.boxes is not None and len(r.boxes)>1:
        a=[(b[2]-b[0])*(b[3]-b[1]) for b in r.boxes.xyxy.tolist()]; bi=a.index(max(a))
    return kp.xy[bi].tolist(),(kp.conf[bi].tolist() if kp.conf is not None else [1]*17)
def tronc(C):return sorted(C[i] for i in (5,6,11,12))[2]  # confiance du tronc : 2e meilleure des epaules et hanches
def paint(path,prim,sec,out,tissu=False):
    im=Image.open(path).convert('RGB'); W,H=im.size
    best=pose(im)
    # personnage tete en bas (ex. back-extensions) : on retente sur l'image tournee
    if best is None or tronc(best[1])<0.3:
        back={90:lambda u,v:(W-v,u),180:lambda u,v:(W-u,H-v),270:lambda u,v:(v,H-u)}
        for ang,f in back.items():
            q=pose(im.rotate(ang,expand=True))
            if q and (best is None or tronc(q[1])>tronc(best[1])):
                best=([list(f(*pt)) for pt in q[0]],q[1]); print('  tourne',ang,os.path.basename(path))
    if best is None: return False
    P,C=best
    arr=np.asarray(im).astype(np.float32)
    body=(arr.mean(2)>88)
    def layer(muscles):
        m=Image.new('L',(W,H),0); d=ImageDraw.Draw(m); any_=False
        for mu in muscles:
            for z in zones(P,C,mu):
                if z[0]=='c':
                    _,cx,cy,rad=z; d.ellipse([cx-rad,cy-rad,cx+rad,cy+rad],fill=255)
                else:
                    _,ax,ay,bx,by,w=z; r=w/2
                    d.line([ax,ay,bx,by],fill=255,width=int(max(2,w)))
                    for (px,py) in ((ax,ay),(bx,by)): d.ellipse([px-r,py-r,px+r,py+r],fill=255)
                any_=True
        if not any_: return None
        return np.asarray(m.filter(ImageFilter.GaussianBlur(max(W,H)*0.010))).astype(np.float32)/255.0
    res=arr.copy()
    for muscles,col,stren in ((sec,(226,140,130),0.55),(prim,(214,46,38),0.88)):
        lay=layer(muscles)
        if lay is None: continue
        mask=body
        # muscle principal cache par le short (ex. fessiers du cable-kickback) : on colore aussi le tissu
        if muscles is prim and (tissu or (lay*body).sum()<W*H*0.002):
            mask=np.maximum(body,np.clip((arr.mean(2)-22)/22,0,1)); paint.tissu=True
        k=(lay*stren*mask)[...,None]
        c=np.zeros_like(arr); c[...,0],c[...,1],c[...,2]=col
        res=res*(1-k)+c*k
    Image.fromarray(np.clip(res,0,255).astype('uint8')).save(out,'WEBP',quality=76,method=5)
    return True
if __name__=='__main__':
    only=set(sys.argv[1:]) if len(sys.argv)>1 else None
    ok=fail=0
    R=A+'/red'
    os.makedirs(R,exist_ok=True)
    for row in rows:
        if only and row['id'] not in only: continue
        paint.tissu=False
        for passe in (0,1):
            # si une position a demande de colorer le tissu, l'autre aussi, sinon l'animation clignote
            if passe and not paint.tissu: break
            if passe: print('  tissu',row['id'])
            for f in range(row['frames']):
                src='%s/%s-%d.webp'%(D,row['id'],f)
                if paint(src,row['m'],row['s'],'%s/%s-%d.webp'%(R,row['id'],f),tissu=passe==1): ok+=passe==0
                else:
                    fail+=passe==0; print('ECHEC',row['id'],f)
                    Image.open(src).save('%s/%s-%d.webp'%(R,row['id'],f),'WEBP',quality=76,method=5)
    print('peints',ok,'echecs',fail)
