"""Colore en rouge les muscles travailles sur les illustrations d'exercices.

Detecte la posture du personnage (YOLO11x-pose, 17 points), en deduit ou se
trouve chaque muscle, et applique la couleur uniquement sur les pixels clairs
du corps. Voir docs/04-images.md.

    pip install ultralytics pillow numpy
    curl -L -o yolo11x-pose.pt \
      https://github.com/ultralytics/assets/releases/download/v8.3.0/yolo11x-pose.pt
    python3 tools/paint.py                    # toutes les illustrations
    python3 tools/paint.py bench-press squat  # seulement ces identifiants

ATTENTION : les chemins ci-dessous (oei/out, oei/red, oei/zones_todo.json) sont
ceux de l'atelier d'origine. Les adapter avant toute reexecution.
"""
import json,os,math,sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from ultralytics import YOLO
D='oei/out'
rows=json.load(open('oei/zones_todo.json'))
model=YOLO('yolo11x-pose.pt')
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
    return out
def paint(path,prim,sec,out):
    im=Image.open(path).convert('RGB'); W,H=im.size
    r=model(path,verbose=False,conf=0.10)[0]
    kp=r.keypoints
    if kp is None or kp.xy is None or len(kp.xy)==0: return False
    # personne la plus grande
    bi=0
    if r.boxes is not None and len(r.boxes)>1:
        a=[(b[2]-b[0])*(b[3]-b[1]) for b in r.boxes.xyxy.tolist()]; bi=a.index(max(a))
    P=kp.xy[bi].tolist(); C=(kp.conf[bi].tolist() if kp.conf is not None else [1]*17)
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
        k=(lay*stren*body)[...,None]
        c=np.zeros_like(arr); c[...,0],c[...,1],c[...,2]=col
        res=res*(1-k)+c*k
    Image.fromarray(np.clip(res,0,255).astype('uint8')).save(out,'WEBP',quality=76,method=5)
    return True
if __name__=='__main__':
    only=set(sys.argv[1:]) if len(sys.argv)>1 else None
    ok=fail=0
    os.makedirs('oei/red',exist_ok=True)
    for row in rows:
        if only and row['id'] not in only: continue
        for f in range(row['frames']):
            src='%s/%s-%d.webp'%(D,row['id'],f)
            if paint(src,row['m'],row['s'],'oei/red/%s-%d.webp'%(row['id'],f)): ok+=1
            else:
                fail+=1; print('ECHEC',row['id'],f)
                Image.open(src).save('oei/red/%s-%d.webp'%(row['id'],f),'WEBP',quality=76,method=5)
    print('peints',ok,'echecs',fail)
