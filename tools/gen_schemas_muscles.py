"""Genere les schemas anatomiques de img2/ : silhouettes face et dos, muscles
principaux en rouge et secondaires en rose, une paire par exercice.

Trace vectoriel repris de react-body-highlighter (MIT, (c) 2020 GV79).
Voir docs/04-images.md.

ATTENTION : chemins absolus de l'atelier d'origine (bodydata.json, exmap.json,
src/exercises.json, src/map.json). Les adapter avant toute reexecution.
"""
import json,sys
from PIL import Image,ImageDraw
B=json.load(open('/tmp/claude-0/-home-claude/9c32212f-2212-5398-b296-2f368ca4e5ff/scratchpad/t/bodydata.json'))
EXI=json.load(open('exmap.json'))
D={x['id']:x for x in json.load(open('src/exercises.json'))}
M=dict(json.load(open('src/map.json')))
# DB muscle -> polygons (view, muscle)
MAP={'chest':[('a','chest')],'shoulders':[('a','front-deltoids'),('p','back-deltoids')],'biceps':[('a','biceps')],'triceps':[('a','triceps'),('p','triceps')],
'forearms':[('a','forearm'),('p','forearm')],'lats':[('p','upper-back')],'middle back':[('p','upper-back')],'lower back':[('p','lower-back')],'traps':[('p','trapezius')],
'glutes':[('p','gluteal')],'hamstrings':[('p','hamstring')],'quadriceps':[('a','quadriceps')],'calves':[('a','calves'),('p','calves'),('p','left-soleus'),('p','right-soleus')],
'abdominals':[('a','abs')],'adductors':[('p','adductor')],'abductors':[('a','abductors')],'neck':[('a','neck')]}
BASE=(203,208,216,255);LINE=(143,151,165,255);PRI=(216,72,58,255);SEC=(240,170,162,255)
def polys(view,muscle):
    out=[]
    for e in B[view]:
        if e['muscle']==muscle:
            for s in e['svgPoints']:
                n=[float(x) for x in s.split()];out.append([(n[i],n[i+1]) for i in range(0,len(n)-1,2)])
    return out
def draw_view(d,view,ox,oy,sc,pri,sec):
    allp=[(e['muscle'],p) for e in B[view] for p in polys(view,e['muscle']) ] if False else None
    items=[]
    for e in B[view]:
        for s in e['svgPoints']:
            n=[float(x) for x in s.split()];items.append((e['muscle'],[(n[i],n[i+1]) for i in range(0,len(n)-1,2)]))
    T=lambda p:[(ox+x*sc,oy+y*sc) for x,y in p]
    for m,p in items: d.polygon(T(p),fill=BASE)
    for m,p in items:
        if (view,m) in sec: d.polygon(T(p),fill=SEC)
    for m,p in items:
        if (view,m) in pri: d.polygon(T(p),fill=PRI)
    w=max(1,int(sc*0.3))
    for m,p in items:
        q=T(p)+[T(p)[0]];d.line(q,fill=LINE,width=w,joint='curve')
def sets(dbm):
    return {x for m in dbm for x in MAP.get(m,[])}
SS=4
tot=0
for fr,i in M.items():
    slug=EXI[fr]['i'];d0=D[i]
    pri=sets(d0['primaryMuscles']);sec=sets(d0['secondaryMuscles'])-pri
    # full map: front | back, 100x200 units each
    W,H=400,400;sc=W/200*SS/ (SS) # 2 px/unit final
    big=Image.new('RGBA',(W*SS,H*SS),(0,0,0,0));d=ImageDraw.Draw(big)
    draw_view(d,'a',0,0,2*SS,pri,sec);draw_view(d,'p',200*SS,0,2*SS,pri,sec)
    big=big.resize((W,H),Image.LANCZOS)
    # trim: units 200x200 -> keep 400x400 (aspect 1:1)
    big=big.convert('RGBA').quantize(colors=24,method=Image.FASTOCTREE) if False else big
    p=f'img2/{slug}-m.png';big.save(p,optimize=True);tot+=len(open(p,'rb').read())
    # plus de vignette -t.png : l'appli ne les affichait pas (retirées au nettoyage de 2026.11)
print('done',tot//1024,'KB')
