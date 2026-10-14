/* ===== GYM ===== */
const LIB=[['Pectoraux',['Développé couché','Développé incliné barre','Développé incliné haltères','Développé couché haltères','Développé décliné','Développé couché machine','Écarté haltères','Écarté poulie','Pec deck','Pompes','Dips']],['Dos',['Tractions','Tractions supination','Tirage vertical','Tirage vertical prise serrée','Rowing barre','Rowing haltère','Tirage horizontal','Rowing T-bar','Soulevé de terre','Pull-over poulie','Shrugs haltères']],['Épaules',['Développé militaire','Développé haltères assis','Arnold press','Élévations latérales','Élévations frontales','Oiseau','Face pull']],['Biceps',['Curl barre','Curl haltères','Curl marteau','Curl pupitre','Curl incliné','Curl poulie']],['Triceps',['Extension poulie','Extension poulie corde','Barre au front','Dips banc','Extension nuque haltère','Extension verticale poulie','Développé serré']],['Jambes',['Squat','Squat avant','Goblet squat','Hack squat','Presse à cuisses','Fentes','Fentes marchées','Leg extension','Leg curl','Leg curl assis','Soulevé de terre roumain','Hip thrust','Mollets debout','Mollets assis']],['Abdos',['Crunch','Crunch poulie','Relevé de jambes','Gainage']]];
/* muscles sollicités par exercice */
const EXI={"Développé couché":{"i":"barbell-bench-press-medium-grip","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé incliné barre":{"i":"barbell-incline-bench-press-medium-grip","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé incliné haltères":{"i":"incline-dumbbell-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé couché haltères":{"i":"dumbbell-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé décliné":{"i":"decline-barbell-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé couché machine":{"i":"machine-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Écarté haltères":{"i":"dumbbell-flyes","m":["Pectoraux"],"s":[]},"Écarté poulie":{"i":"cable-crossover","m":["Pectoraux"],"s":["Épaules"]},"Pec deck":{"i":"butterfly","m":["Pectoraux"],"s":[]},"Pompes":{"i":"pushups","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Dips":{"i":"parallel-bar-dip","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Tractions":{"i":"pullups","m":["Grand dorsal"],"s":["Biceps","Milieu du dos"]},"Tractions supination":{"i":"chin-up","m":["Grand dorsal"],"s":["Biceps","Avant-bras","Milieu du dos"]},"Tirage vertical":{"i":"wide-grip-lat-pulldown","m":["Grand dorsal"],"s":["Biceps","Milieu du dos","Épaules"]},"Tirage vertical prise serrée":{"i":"close-grip-front-lat-pulldown","m":["Grand dorsal"],"s":["Biceps","Milieu du dos","Épaules"]},"Rowing barre":{"i":"bent-over-barbell-row","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Rowing haltère":{"i":"one-arm-dumbbell-row","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Tirage horizontal":{"i":"seated-cable-rows","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Rowing T-bar":{"i":"t-bar-row-with-handle","m":["Milieu du dos"],"s":["Biceps","Grand dorsal"]},"Soulevé de terre":{"i":"barbell-deadlift","m":["Lombaires"],"s":["Mollets","Avant-bras","Fessiers"]},"Pull-over poulie":{"i":"straight-arm-pulldown","m":["Grand dorsal"],"s":[]},"Shrugs haltères":{"i":"dumbbell-shrug","m":["Trapèzes"],"s":[]},"Développé militaire":{"i":"standing-military-press","m":["Épaules"],"s":["Triceps"]},"Développé haltères assis":{"i":"dumbbell-shoulder-press","m":["Épaules"],"s":["Triceps"]},"Élévations latérales":{"i":"side-lateral-raise","m":["Épaules"],"s":[]},"Élévations frontales":{"i":"front-dumbbell-raise","m":["Épaules"],"s":[]},"Oiseau":{"i":"reverse-flyes","m":["Épaules"],"s":[]},"Face pull":{"i":"face-pull","m":["Épaules"],"s":["Milieu du dos"]},"Arnold press":{"i":"arnold-dumbbell-press","m":["Épaules"],"s":["Triceps"]},"Curl barre":{"i":"barbell-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl haltères":{"i":"dumbbell-bicep-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl marteau":{"i":"hammer-curls","m":["Biceps"],"s":[]},"Curl pupitre":{"i":"preacher-curl","m":["Biceps"],"s":[]},"Curl incliné":{"i":"alternate-incline-dumbbell-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl poulie":{"i":"standing-biceps-cable-curl","m":["Biceps"],"s":[]},"Extension poulie":{"i":"triceps-pushdown","m":["Triceps"],"s":[]},"Extension poulie corde":{"i":"triceps-pushdown-rope-attachment","m":["Triceps"],"s":[]},"Barre au front":{"i":"ez-bar-skullcrusher","m":["Triceps"],"s":["Avant-bras"]},"Dips banc":{"i":"bench-dips","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Extension nuque haltère":{"i":"standing-dumbbell-triceps-extension","m":["Triceps"],"s":[]},"Extension verticale poulie":{"i":"cable-rope-overhead-triceps-extension","m":["Triceps"],"s":[]},"Développé serré":{"i":"close-grip-barbell-bench-press","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Squat":{"i":"barbell-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Squat avant":{"i":"front-barbell-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Goblet squat":{"i":"goblet-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Hack squat":{"i":"barbell-hack-squat","m":["Quadriceps"],"s":["Mollets","Avant-bras","Ischio-jambiers"]},"Presse à cuisses":{"i":"leg-press","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Fentes":{"i":"dumbbell-lunges","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Fentes marchées":{"i":"barbell-walking-lunge","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Leg extension":{"i":"leg-extensions","m":["Quadriceps"],"s":[]},"Leg curl":{"i":"lying-leg-curls","m":["Ischio-jambiers"],"s":[]},"Leg curl assis":{"i":"seated-leg-curl","m":["Ischio-jambiers"],"s":[]},"Soulevé de terre roumain":{"i":"romanian-deadlift","m":["Ischio-jambiers"],"s":["Mollets","Fessiers","Lombaires"]},"Hip thrust":{"i":"barbell-hip-thrust","m":["Fessiers"],"s":["Mollets","Ischio-jambiers"]},"Mollets debout":{"i":"standing-calf-raises","m":["Mollets"],"s":[]},"Mollets assis":{"i":"seated-calf-raise","m":["Mollets"],"s":[]},"Crunch":{"i":"crunches","m":["Abdominaux"],"s":[]},"Relevé de jambes":{"i":"hanging-leg-raise","m":["Abdominaux"],"s":[]},"Crunch poulie":{"i":"cable-crunch","m":["Abdominaux"],"s":[]},"Gainage":{"i":"plank","m":["Abdominaux"],"s":[]}};
/* Consignes, équipement, muscles corrigés et exercices en plus : EXD (js3c.js, généré par tools/gen_exercices.py).
   Un exercice en plus a un groupe g : il rejoint LIB. Sans e.i, il n'a pas de schéma img2/. */
Object.keys(EXD).forEach(n=>{
  const d=EXD[n];EXI[n]=Object.assign(EXI[n]||{},d);
  if(d.g){let g=LIB.find(x=>x[0]===d.g);if(!g)LIB.push(g=[d.g,[]]);if(!g[1].includes(n))g[1].push(n)}
});
/* Familles de prises (EXV, js3c.js) : la liste ne montre que le premier exercice de la famille ;
   la prise se choisit sur la carte de la séance ou de la routine (gripRow), ce qui change le nom de
   l'exercice : chaque prise garde donc son historique. */
const GRIP={};Object.keys(EXV).forEach(b=>EXV[b][1].forEach(([,n])=>{GRIP[n]=b}));
const gripHidden=n=>!!GRIP[n]&&GRIP[n]!==n;
function gripRow(name,act,i){
  const b=GRIP[name];if(!b)return '';
  const [lab,opts]=EXV[b];
  return `<div class="row gripr" style="flex-wrap:wrap;gap:6px;margin:10px 0 2px;align-items:center"><span class="small muted" style="margin-right:2px">${lab} :</span>${opts.map(([t,n])=>`<button class="chip" style="min-height:40px;padding:0 12px" data-act="${act}" data-i="${i}" data-n="${esc(n)}" aria-pressed="${n===name}">${esc(t)}</button>`).join('')}</div>`;
}
const EX_MUS=['Pectoraux','Grand dorsal','Milieu du dos','Lombaires','Trapèzes','Épaules','Biceps','Triceps','Avant-bras','Quadriceps','Ischio-jambiers','Fessiers','Mollets','Adducteurs','Abducteurs','Abdominaux'].filter(m=>Object.values(EXI).some(e=>e.m.includes(m)));
const EX_EQ=[...new Set(Object.values(EXI).map(e=>e.eq).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'fr'));

function thumb(name,size){
  const id=ILL[name],st=size?'style="width:'+size+'px;height:'+size+'px"':'';
  return id?'<img class="thumb" '+st+' src="ill/'+id+'-t.webp" alt="" loading="lazy" decoding="async">':'<div class="thumb ph" '+st+' aria-hidden="true">'+esc((name||'?').trim().charAt(0).toUpperCase())+'</div>';
}

let gymTab='sessions',gymOpen=false,progEx=null,progMetric='top',exQuery='',exMus='',exEq='',restEnd=0;
const fmtKg=v=>nf(v,2);
const e1rm=(kg,reps)=>reps<=1?kg:kg*(1+reps/30);
const setVol=s=>num(s.kg)*num(s.reps);
/* type de série (2026.10.14-5) : t absent = normale, 'w' échauffement, 'f' échec, 'd' drop set.
   L'échauffement ne compte nulle part (records, volume, suggestion, séries par muscle) ; échec et drop set
   comptent comme des séries normales. */
const STYPES={w:['É','Échauffement'],f:['E','Échec'],d:['D','Drop set']};
const isWork=s=>!s||s.t!=='w';
const workSets=sets=>(sets||[]).filter(isWork);
const withT=(o,s)=>s&&STYPES[s.t]?Object.assign(o,{t:s.t}):o;
const topSet=sets=>sets.reduce((b,s)=>!b||num(s.kg)>num(b.kg)||(num(s.kg)===num(b.kg)&&num(s.reps)>num(b.reps))?s:b,null);
const sessVol=ses=>ses.exercises.reduce((t,e)=>t+workSets(e.sets).reduce((u,s)=>u+setVol(s),0),0);
/* libellé de la case « # » : lettre du type, sinon numéro parmi les séries normales */
function setLab(sets,si){const s=sets[si];if(STYPES[s.t])return STYPES[s.t][0];let n=0;for(let i=0;i<=si;i++)if(!STYPES[sets[i].t])n++;return String(n)}
/* records (2026.10.14-5) : la série validée est comparée à toutes les séries de travail déjà faites sur cet
   exercice (séances enregistrées + séries déjà validées de la séance en cours). Rien à comparer = pas de record.
   Un seul record retenu : charge max > 1RM estimé > répétitions à cette charge > volume de la série. */
function prCheck(name,set,others){
  const kg=num(set.kg),reps=num(set.reps);
  let n=0,bk=null,be=0,bv=0,br=null;
  const see=s=>{const k=num(s.kg),r=num(s.reps);if(r<=0)return;n++;
    if(!bk||k>num(bk.kg)||(k===num(bk.kg)&&r>num(bk.reps)))bk=s;
    be=Math.max(be,e1rm(k,r));bv=Math.max(bv,k*r);if(k===kg&&(br===null||r>br))br=r};
  for(const ses of S.sessions)for(const e of ses.exercises)if(e.name===name)workSets(e.sets).forEach(see);
  others.forEach(see);
  if(!n||reps<=0)return null;
  const e1=e1rm(kg,reps),v=kg*reps,f=x=>nf(x,2);
  if(kg>num(bk.kg))return {k:'kg',txt:`Record ! ${name} ${f(kg)} kg × ${nf(reps,0)} (avant : ${f(num(bk.kg))} × ${nf(num(bk.reps),0)})`};
  if(kg>0&&e1>be+.05)return {k:'e1',txt:`Record de 1RM estimé ! ${name} ${nf(e1,1)} kg (avant : ${nf(be,1)})`};
  if(br!==null&&reps>br)return {k:'reps',txt:`Record ! ${name} ${f(kg)} kg × ${nf(reps,0)} (avant : ${f(kg)} × ${nf(br,0)})`};
  if(kg>0&&v>bv)return {k:'vol',txt:`Record de volume ! ${name} ${f(kg)} × ${nf(reps,0)} = ${nf(v,0)} kg (avant : ${nf(bv,0)})`};
  return null;
}
let prBan=null;   /* bannière du dernier record : {s, until} ; jamais enregistrée */
const PR_MS=5000;
/* suggestion de charge, double progression (2026.10.14-5) : seulement une indication, jamais appliquée d'office.
   Séries de travail chargées (kg > 0) : toutes à la même charge et toutes >= max -> + palier ;
   toutes >= min -> rester ; une seule sous min, ou rien de chargé (poids du corps, durée) -> rien. */
function sugCalc(sets){
  const g=S.settings;if(g.sugCharge===false)return null;
  const lo=num(g.sugMin)||10,hi=num(g.sugMax)||12,st=num(g.pasCharge)||2.5;
  const w=workSets(sets).filter(s=>num(s.kg)>0&&num(s.reps)>0);if(!w.length)return null;
  const top=Math.max(...w.map(s=>num(s.kg))),minR=Math.min(...w.map(s=>num(s.reps)));
  if(minR<lo)return null;
  if(minR>=hi&&w.every(s=>num(s.kg)===top))return {up:true,kg:Math.round((top+st)*100)/100,st,lo,hi};
  return {up:false,kg:top,st,lo,hi};
}
/* phrase complète (lecteur d'écran, info-bulle) ; à l'écran une version courte qui tient sur une ligne */
const sugTxt=(g,when)=>'Suggestion. '+(g.up?when+' : +'+fmtKg(g.st)+' kg ('+fmtKg(g.kg)+' kg) et repars à '+g.lo+' répétitions.':'Reste à '+fmtKg(g.kg)+' kg, vise '+g.hi+' répétitions sur chaque série.');
function lastPerf(name){
  for(const ses of S.sessions){const e=ses.exercises.find(x=>x.name===name);if(e)return e.sets}
  return null;
}
function history(name){
  const out=[];
  for(const ses of S.sessions.slice().reverse()){
    const e=ses.exercises.find(x=>x.name===name),w=e?workSets(e.sets):[];if(!w.length)continue;
    const top=topSet(w),best=w.reduce((m,s)=>Math.max(m,e1rm(num(s.kg),num(s.reps))),0);
    out.push({date:ses.date,x:dn(ses.date),top,e1:best,vol:w.reduce((t,s)=>t+setVol(s),0)});
  }
  return out;
}
function allExNames(){
  const set=new Set();LIB.forEach(g=>g[1].forEach(n=>set.add(n)));S.exercises.forEach(n=>set.add(n));
  S.sessions.forEach(s=>s.exercises.forEach(e=>set.add(e.name)));
  return [...set];
}
const mkSets=n=>Array.from({length:n},()=>({kg:'',reps:'',done:false}));
function startSession(name,exs){
  if(S.active){gymOpen=true;toast('Séance en cours reprise');render();return}
  /* exs : [{name, sets:[{kg,reps},…]}] (routine) ; chaque série reprend SON poids et SES répétitions prévus */
  const str=v=>v==null?'':String(v);
  S.active={id:uid(),name:name||'Séance',start:Date.now(),exercises:exs.map(e=>({name:e.name,sets:(Array.isArray(e.sets)&&e.sets.length?e.sets:mkSets(3)).map(x=>withT({kg:str(x.kg),reps:str(x.reps),done:false},x))}))};
  persist('active');gymOpen=true;restEnd=0;render();window.scrollTo(0,0);
}
VIEWS.gym=()=>S.active&&gymOpen?sessionView():routEdit?routineView():gymHome();
function gymHome(){
  const seg=`<div class="seg" role="tablist"><button role="tab" data-act="g-tab" data-t="sessions" aria-selected="${gymTab==='sessions'}">Séances</button><button role="tab" data-act="g-tab" data-t="progress" aria-selected="${gymTab==='progress'}">Progression</button></div>`;
  return seg+(gymTab==='sessions'?sessionsHome():progressView());
}
A['g-tab']=b=>{gymTab=b.dataset.t;render()};
function sessionsHome(){
  const wk=S.sessions.filter(s=>dn(s.date)>dn(today())-7);
  const active=S.active?`<div class="card" style="background:var(--accent);color:var(--on-accent)"><div class="row sb"><div><div class="small" style="opacity:.85;font-weight:700">SÉANCE EN COURS</div><div class="num" style="font-size:22px;font-weight:800">${esc(S.active.name)}</div></div><button class="btn" style="background:var(--on-accent);color:var(--accent)" data-act="g-resume">Reprendre</button></div></div>`:'';
  const routines=`<div class="card"><div class="row sb" style="margin-bottom:${S.routines.length?'10px':'2px'}"><h2 style="margin:0">Mes routines</h2><button class="chip" data-act="g-rnew">${ICON.plus} Créer</button></div>
  ${S.routines.length?'<div class="list">'+S.routines.map(r=>`<div class="row"><button class="li" data-act="g-rstart" data-id="${r.id}"><div class="grow"><div class="t">${esc(r.name)}</div><div class="small muted">${r.exercises.length} exercice${r.exercises.length>1?'s':''}${(n=>n?' · '+n+' série'+(n>1?'s':''):'')(r.exercises.reduce((t,e)=>t+(Array.isArray(e.sets)?e.sets.length:0),0))}${r.exercises.length?' · '+esc(r.exercises.slice(0,3).map(e=>e.name).join(', '))+(r.exercises.length>3?'…':''):''}</div></div><span class="pill neutral">Démarrer</span></button><button class="iconbtn" style="box-shadow:none;background:var(--surface2)" data-act="g-redit" data-id="${r.id}" aria-label="Modifier la routine ${esc(r.name)}"><span style="font-size:19px;line-height:1">⋯</span></button></div>`).join('')+'</div>'
  :'<div class="small muted" style="margin:0 0 2px">Prépare tes séances à l’avance : les exercices, le nombre de séries, et si tu veux les charges prévues.</div>'}</div>`;

  const hist=S.sessions.slice(0,30).map(s=>{
    const sets=s.exercises.reduce((t,e)=>t+e.sets.length,0);
    return `<button class="li" data-act="g-view" data-id="${s.id}"><div class="grow"><div class="t">${esc(s.name)}</div><div class="small muted">${esc(fmtDay(s.date))} · ${s.exercises.length} exo · ${sets} séries · ${nf(sessVol(s),0)} kg</div></div>${ICON.chev}</button>`;
  }).join('');
  return `${active}
  <div class="card"><div class="stats" style="grid-template-columns:1fr 1fr"><div class="stat"><span>7 derniers jours</span><b>${wk.length}</b><span>séance${wk.length>1?'s':''}</span></div><div class="stat"><span>Volume 7 jours</span><b>${nf(wk.reduce((t,s)=>t+sessVol(s),0)/1000,1)}</b><span>tonnes</span></div></div>
  ${S.active?'':'<button class="btn block" style="margin-top:14px" data-act="g-start">'+ICON.plus+' Nouvelle séance</button>'}</div>
  ${routines}
  <div class="card"><h2>Historique</h2>${hist?'<div class="list">'+hist+'</div>':'<div class="empty">Ta première séance apparaîtra ici.</div>'}</div>`;
}
A['g-start']=()=>startSession('Séance',[]);
A['g-resume']=()=>{gymOpen=true;render();window.scrollTo(0,0)};
A['g-back']=()=>{gymOpen=false;render()};
A['g-start-r']=b=>{const r=S.routines.find(x=>x.id===b.dataset.id);if(r)startSession(r.name,r.exercises)};
A['g-rdel']=b=>confirmSheet('Supprimer cette routine ?','Les séances déjà faites ne sont pas touchées.','Supprimer',()=>{routEdit=null;S.routines=S.routines.filter(r=>r.id!==b.dataset.id);persist('routines');render()});

/* active session */
function sessionView(){
  const a=S.active;
  const exs=a.exercises.map((e,ei)=>{
    const prev=lastPerf(e.name)||[],sg=sugCalc(prev),live=sugCalc(e.sets.filter(s=>s.done));
    const rows=e.sets.map((s,si)=>{
      const p=prev[si],ty=STYPES[s.t];
      const ban=prBan&&prBan.s===s&&s.pr&&Date.now()<prBan.until?`<div class="prban" id="prban" role="status">🏆 ${esc(s.pr.txt)}</div>`:'';
      return `<div class="r ${s.done?'done':''}" style="display:contents"><button class="n${ty?' t'+s.t:''}" data-act="g-stype" data-c="a" data-e="${ei}" data-s="${si}" aria-label="Série ${si+1}, ${ty?ty[1].toLowerCase():'normale'} : changer le type">${setLab(e.sets,si)}</button><div class="prev">${p?nf(num(p.kg),2)+' × '+nf(num(p.reps),0):'—'}</div>
      <input inputmode="decimal" data-in="set" data-e="${ei}" data-s="${si}" data-f="kg" value="${esc(s.kg)}" placeholder="${p?nf(num(p.kg),2):'kg'}" aria-label="Charge série ${si+1}">
      <input inputmode="numeric" data-in="set" data-e="${ei}" data-s="${si}" data-f="reps" value="${esc(s.reps)}" placeholder="${p?nf(num(p.reps),0):'reps'}" aria-label="Répétitions série ${si+1}">
      <button class="ck" data-act="g-check" data-e="${ei}" data-s="${si}" aria-pressed="${s.done}" aria-label="Série ${si+1} faite">${ICON.check}</button></div>${ban}`;
    }).join('');
    return `<div class="card ex"><div class="hd"><button class="thumbbtn" data-act="g-exinfo" data-name="${esc(e.name)}" aria-label="Voir l’exercice ${esc(e.name)}">${thumb(e.name,48)}</button><b style="flex:1;min-width:0;overflow-wrap:anywhere">${esc(e.name)}</b><button class="iconbtn" style="width:40px;height:40px;box-shadow:none;background:var(--surface2)" data-act="g-exmenu" data-e="${ei}" aria-label="Options de l’exercice"><span style="font-size:20px;line-height:1">⋯</span></button></div>${gripRow(e.name,'g-grip',ei)}
    ${sg?(t=>`<button class="sug" data-act="g-sug" data-e="${ei}" data-kg="${sg.kg}" title="${t}" aria-label="${t}">💡 <b>Suggestion</b> · ${sg.up?`${fmtKg(sg.kg)} kg (+${fmtKg(sg.st)}), repars à ${sg.lo} reps`:`reste à ${fmtKg(sg.kg)} kg, vise ${sg.hi} reps`}</button>`)(sugTxt(sg,'Aujourd’hui')+' Touche pour pré-remplir la charge.'):''}
    <div class="sets"><div class="h">#</div><div class="h">Avant</div><div class="h">kg</div><div class="h">Reps</div><div class="h">OK</div>${rows}</div>
    ${live?`<div class="sug" title="${sugTxt(live,'Prochaine fois')}"><span aria-hidden="true">💡 <b>Suggestion</b> · ${live.up?`prochaine fois ${fmtKg(live.kg)} kg, ${live.lo} reps`:`reste à ${fmtKg(live.kg)} kg, vise ${live.hi} reps`}</span><span class="sr">${sugTxt(live,'Prochaine fois')}</span></div>`:''}
    <button class="btn soft block" style="margin-top:12px;min-height:44px" data-act="g-addset" data-e="${ei}">${ICON.plus} Série</button></div>`;
  }).join('');
  return `<div class="row sb" style="margin-bottom:10px"><button class="chip" data-act="g-back">${ICON.chevL} Séances</button><span class="num" id="elapsed" style="font-weight:800;font-size:20px"></span><button class="btn" style="min-height:44px" data-act="g-finish">Terminer</button></div>
  <div class="field"><input class="inp" data-in="sname" value="${esc(a.name)}" aria-label="Nom de la séance" style="font-weight:700"></div>
  ${exs||'<div class="card empty">Ajoute ton premier exercice.</div>'}
  <button class="btn block" data-act="g-addex">${ICON.plus} Ajouter un exercice</button>
  <button class="btn danger block" style="margin-top:10px" data-act="g-cancel">Abandonner la séance</button>`;
}
function tick(){
  const a=S.active,el=$('#elapsed');
  if(a&&el){const s=Math.floor((Date.now()-a.start)/1000),h=Math.floor(s/3600),m=Math.floor(s%3600/60);el.textContent=(h?h+':'+pad(m):m)+':'+pad(s%60)}
  if(typeof syncRestBar==='function')syncRestBar();
  if(typeof wakeSync==='function')wakeSync();   /* écran allumé pendant la séance (js5.js, téléphone seulement) */
}
VIEWS.gym_after=tick;
I.sname=t=>{if(S.active){S.active.name=t.value;persist('active')}};
I.set=t=>{const a=S.active;if(!a)return;const s=a.exercises[+t.dataset.e].sets[+t.dataset.s];s[t.dataset.f]=t.value;persist('active')};
A['g-check']=b=>{
  const a=S.active,e=a.exercises[+b.dataset.e],s=e.sets[+b.dataset.s];
  if(!s.done){
    const p=(lastPerf(e.name)||[])[+b.dataset.s];
    if(s.kg===''&&p)s.kg=String(num(p.kg));
    if(s.reps===''&&p)s.reps=String(num(p.reps));
    if(s.reps===''||num(s.reps)<=0){toast('Indique les répétitions');return}
    if(s.kg==='')s.kg='0';
    s.done=true;
    delete s.pr;prBan=null;   /* une nouvelle série validée remplace la bannière précédente */
    if(isWork(s)){
      const o=a.exercises.filter(x=>x.name===e.name).flatMap(x=>x.sets.filter(y=>y!==s&&y.done&&isWork(y)));
      const pr=prCheck(e.name,s,o);if(pr){s.pr=pr;prBan={s,until:Date.now()+PR_MS}}
    }
    startRest(S.settings.rest);
  }else{s.done=false;delete s.pr}
  persist('active');render();
  /* la bannière s'efface d'elle-même, sans redessiner l'écran */
  if(s.done&&s.pr){const u=prBan.until;setTimeout(()=>{const x=$('#prban');if(x&&prBan&&prBan.until===u){x.classList.add('out');setTimeout(()=>{if(prBan&&prBan.until===u)x.remove()},300)}},PR_MS-300)}
};
/* type de série : un appui sur le numéro ; c = 'a' séance en cours, 'r' routine */
const STY_OPTS=[['','Normale','1','Compte partout.'],['w','Échauffement','É','Ne compte ni dans les records, ni dans le volume, ni dans les suggestions.'],['f','Échec','E','Jusqu’à ne plus pouvoir faire une répétition. Compte comme une série normale.'],['d','Drop set','D','Charge baissée juste après une série, sans repos. Compte comme une série normale.']];
function stSet(c,ei,si){const x=c==='r'?curRoutine():S.active,e=x&&x.exercises[ei];return e&&e.sets[si]||null}
A['g-stype']=b=>{
  const {c,e,s}=b.dataset,set=stSet(c,+e,+s);if(!set)return;const cur=STYPES[set.t]?set.t:'';
  openSheet(`<h3>Type de la série</h3><div class="list">${STY_OPTS.map(([t,l,k,d])=>`<button class="li" data-act="g-stype-ok" data-c="${c}" data-e="${e}" data-s="${s}" data-t="${t}" aria-pressed="${t===cur}"><span class="stb${t?' t'+t:''}">${k}</span><div class="grow"><div class="t">${l}${t===cur?' ✓':''}</div><div class="small muted">${d}</div></div></button>`).join('')}</div>
  <button class="btn ghost block" style="margin-top:12px" data-act="close">Fermer</button>`);
};
A['g-stype-ok']=b=>{
  const {c,e,s,t}=b.dataset,set=stSet(c,+e,+s);if(!set)return;
  if(STYPES[t])set.t=t;else delete set.t;
  if(t==='w')delete set.pr;
  persist(c==='r'?'routines':'active');closeSheet();render();
};
/* appui sur la suggestion : pré-remplit la charge des séries de travail pas encore validées, rien d'autre */
A['g-sug']=b=>{
  const e=S.active&&S.active.exercises[+b.dataset.e],kg=num(b.dataset.kg);if(!e||!(kg>0))return;
  e.sets.forEach(s=>{if(!s.done&&isWork(s))s.kg=String(kg)});persist('active');render();toast('Charge pré-remplie : '+fmtKg(kg)+' kg');
};
A['g-addset']=b=>{const e=S.active.exercises[+b.dataset.e],l=e.sets[e.sets.length-1];e.sets.push({kg:l?l.kg:'',reps:l?l.reps:'',done:false});persist('active');render()};
A['g-rest-skip']=()=>{restEnd=0;syncRestBar()};
A['g-exmenu']=b=>{
  const ei=b.dataset.e,e=S.active.exercises[+ei];
  openSheet(`<h3>${esc(e.name)}</h3><div class="grid2"><button class="btn ghost" data-act="g-rmset" data-e="${ei}">Retirer la dernière série</button><button class="btn danger" data-act="g-rmex" data-e="${ei}">Retirer l’exercice</button></div>`);
};
A['g-rmset']=b=>{const e=S.active.exercises[+b.dataset.e];if(e.sets.length)e.sets.pop();persist('active');closeSheet();render()};
A['g-rmex']=b=>{S.active.exercises.splice(+b.dataset.e,1);persist('active');closeSheet();render()};
A['g-cancel']=()=>confirmSheet('Abandonner la séance ?','Tout ce que tu as saisi sera perdu.','Abandonner',()=>{S.active=null;restEnd=0;gymOpen=false;persist('active');render()});

/* exercise picker */
/* filtre muscle (principal) et équipement ; un exercice créé à la main n'a ni l'un ni l'autre */
const EXVOC={};
const exOk1=n=>{const e=EXI[n];return(!exMus||!!e&&e.m.includes(exMus))&&(!exEq||!!e&&e.eq===exEq)};
const exOk=n=>EXV[n]?EXV[n][1].some(([,m])=>exOk1(m)):exOk1(n);
function exFilters(){
  const sel=(k,lab,all,v,list)=>`<select class="inp" data-ch="${k}" aria-label="${lab}" style="flex:1;min-width:0;min-height:44px;padding:0 10px">
    <option value="">${all}</option>${list.map(x=>`<option value="${esc(x)}"${x===v?' selected':''}>${esc(x)}</option>`).join('')}</select>`;
  return `<div class="row" id="exfilt" style="gap:8px;margin:-4px 0 12px">${sel('exmus','Filtrer par muscle','Tous les muscles',exMus,EX_MUS)}${sel('exeq','Filtrer par équipement','Tout équipement',exEq,EX_EQ)}</div>`;
}
function exPicker(){
  const q=normTxt(exQuery).trim(),all=allExNames(),filt=!!(exMus||exEq);
  const tgt=routEdit&&!(S.active&&gymOpen)?curRoutine():S.active;
  const used=new Set(tgt?tgt.exercises.flatMap(e=>[e.name,GRIP[e.name]]):[]);
  const row=n=>{const e=EXI[n],v=EXV[n];return `<button class="li" data-act="g-pickex" data-name="${esc(n)}" ${used.has(n)?'style="opacity:.5"':''}>${thumb(n)}<div class="grow"><div class="t">${esc(n)}</div>${e?'<div class="small muted">'+esc(e.m.join(', ')+(e.eq?' · '+e.eq:'')+(v?' · '+v[1].length+' '+v[0].toLowerCase()+'s':''))+'</div>':''}</div>${used.has(n)?'<span class="small muted">ajouté</span>':''}</button>`};
  const create=q&&!all.some(n=>n.toLowerCase()===q)?`<button class="btn soft block" style="margin-bottom:10px" data-act="g-newex" data-name="${esc(exQuery.trim())}">${ICON.plus} Créer « ${esc(exQuery.trim())} »</button>`:'';
  if(q){
    /* une prise trouvée seule s'affiche telle quelle ; si l'exercice de la famille est trouvé aussi, lui seul */
    /* mots dans n'importe quel ordre, pluriel et fautes tolérés (fzAlts, js2f.js) ; exact d'abord */
    const t=fzAlts(exQuery,fzCache(EXVOC,all.length,()=>all.map(normTxt))),sc={};
    const hit=all.filter(n=>exOk1(n)&&(sc[n]=fzScore(normTxt(n),t))!==null),hs=new Set(hit);
    const names=hit.filter(n=>!(gripHidden(n)&&hs.has(GRIP[n]))).sort((a,b)=>sc[a]-sc[b]||a.length-b.length||a.localeCompare(b,'fr'));return create+(names.length?'<div class="list">'+names.map(row).join('')+'</div>':'<div class="empty">Aucun exercice avec ces filtres.</div>')}
  if(filt){
    let h='',k=0;
    LIB.forEach(([g,names])=>{const l=names.filter(n=>!gripHidden(n)&&exOk(n));k+=l.length;if(l.length)h+='<div class="sec" style="margin-top:16px">'+g+' <span class="muted">· '+l.length+'</span></div><div class="list">'+l.map(row).join('')+'</div>'});
    return k?h:'<div class="empty">Aucun exercice avec ces filtres.</div>';
  }
  const inLib=new Set(LIB.flatMap(g=>g[1])),rec=[];
  for(const ses of S.sessions){for(const e of ses.exercises)if(!rec.includes(e.name))rec.push(e.name);if(rec.length>=6)break}
  const others=all.filter(n=>!inLib.has(n)).sort((a,b)=>a.localeCompare(b,'fr'));
  let h='';
  if(rec.length)h+='<div class="sec">Récents</div><div class="list">'+rec.slice(0,6).map(row).join('')+'</div>';
  LIB.forEach(([g,names])=>{h+='<div class="sec" style="margin-top:16px">'+g+'</div><div class="list">'+names.filter(n=>!gripHidden(n)).map(row).join('')+'</div>'});
  if(others.length)h+='<div class="sec" style="margin-top:16px">Mes exercices</div><div class="list">'+others.map(row).join('')+'</div>';
  return h;
}
A['g-addex']=()=>{exQuery='';exMus='';exEq='';openSheet(`<h3>Ajouter un exercice</h3><div class="field"><input class="inp" id="exq" data-in="exq" placeholder="Rechercher ou créer" aria-label="Rechercher un exercice"></div>${exFilters()}<div id="exlist">${exPicker()}</div>`)};
I.exq=t=>{exQuery=t.value;$('#exlist').innerHTML=exPicker()};
I.exmus=t=>{exMus=t.value;$('#exlist').innerHTML=exPicker()};
I.exeq=t=>{exEq=t.value;$('#exlist').innerHTML=exPicker()};
function pushEx(name){
  if(routEdit&&!(S.active&&gymOpen)){rAskSets(name);return}   /* routine : d'abord « Combien de séries ? » (js3b.js) */
  S.active.exercises.push({name,sets:mkSets(3)});persist('active');closeSheet();render();
  setTimeout(()=>{const cs=document.querySelectorAll('.ex');if(cs.length)cs[cs.length-1].scrollIntoView({behavior:'smooth',block:'center'})},60);
}
A['g-pickex']=b=>pushEx(b.dataset.name);
/* changer de prise : l'exercice prend le nom de la prise (séries déjà saisies conservées) */
A['g-grip']=b=>{const e=S.active&&S.active.exercises[+b.dataset.i];if(!e)return;e.name=b.dataset.n;persist('active');render()};
A['g-newex']=b=>{const n=b.dataset.name;if(!n)return;if(!allExNames().includes(n)){S.exercises.push(n);persist('exercises')}pushEx(n)};

/* finish */
A['g-finish']=()=>{
  const a=S.active,done=a.exercises.reduce((t,e)=>t+e.sets.filter(s=>s.done).length,0),skip=a.exercises.reduce((t,e)=>t+e.sets.filter(s=>!s.done).length,0);
  if(!done){toast('Coche au moins une série');return}
  confirmSheet('Terminer la séance ?',done+' série'+(done>1?'s':'')+' validée'+(done>1?'s':'')+(skip?'. '+skip+' non cochée'+(skip>1?'s':'')+' ne seront pas gardées.':'.'),'Terminer',finishSession);
};
function finishSession(){
  const a=S.active;
  const exs=a.exercises.map(e=>({name:e.name,sets:e.sets.filter(s=>s.done).map(s=>withT({kg:num(s.kg),reps:num(s.reps)},s))})).filter(e=>e.sets.length);
  const date=ymd(new Date(a.start));
  /* records battus pendant la séance, gardés avec elle (pour un futur résumé) */
  const prs=[];a.exercises.forEach(e=>e.sets.forEach(s=>{if(s.done&&s.pr&&isWork(s))prs.push({ex:e.name,k:s.pr.k,txt:s.pr.txt})}));
  const ses={id:a.id,date,name:a.name||'Séance',dur:Math.max(1,Math.round((Date.now()-a.start)/60000)),exercises:exs};
  if(prs.length)ses.prs=prs;
  S.sessions.unshift(ses);S.sessions.sort((x,y)=>y.date.localeCompare(x.date));
  S.active=null;restEnd=0;gymOpen=false;prBan=null;persist('sessions',date);persist('active');
  const recs=prs.map(r=>r.txt);
  openSheet(`<h3>Séance enregistrée</h3><div class="stats" style="margin-bottom:14px"><div class="stat"><span>Durée</span><b>${ses.dur}</b><span>min</span></div><div class="stat"><span>Séries</span><b>${exs.reduce((t,e)=>t+e.sets.length,0)}</b><span>validées</span></div><div class="stat"><span>Volume</span><b>${nf(sessVol(ses),0)}</b><span>kg</span></div></div>
  ${recs.length?'<div class="card" style="box-shadow:none"><h2>Records battus</h2>'+recs.map(r=>'<div style="padding:4px 0;font-weight:600">🏆 '+esc(r)+'</div>').join('')+'</div>':''}
  <div class="grid2"><button class="btn soft" data-act="g-saver" data-id="${ses.id}">Garder comme routine</button><button class="btn" data-act="close">Fermer</button></div>`);
  render();
}

/* session detail */
A['g-view']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  openSheet(`<h3>${esc(s.name)}</h3><div class="small muted" style="margin:-8px 0 12px">${esc(fmtLong(s.date))} · ${s.dur||'?'} min · ${nf(sessVol(s),0)} kg</div>
  ${Array.isArray(s.prs)&&s.prs.length?`<div class="card" style="box-shadow:none">${s.prs.map(r=>`<div class="small" style="padding:2px 0;font-weight:600">🏆 ${esc(r.txt)}</div>`).join('')}</div>`:''}
  ${s.exercises.map(e=>`<div class="card" style="box-shadow:none"><b>${esc(e.name)}</b><div class="small" style="margin-top:6px;line-height:1.7">${e.sets.map(x=>`<span class="pill neutral${x.t==='w'?' pw':''}" style="margin:0 6px 4px 0"${STYPES[x.t]?` title="${STYPES[x.t][1]}"`:''}>${STYPES[x.t]?STYPES[x.t][0]+' · ':''}${nf(num(x.kg),2)} × ${nf(num(x.reps),0)}</span>`).join('')}</div></div>`).join('')}
  <div class="grid2" style="margin-bottom:10px"><button class="btn soft" data-act="g-redo" data-id="${s.id}">Refaire</button><button class="btn soft" data-act="g-saver" data-id="${s.id}">En faire une routine</button></div>
  <button class="btn danger block" data-act="g-sdel" data-id="${s.id}">Supprimer</button>`);
};
A['g-redo']=b=>{const s=S.sessions.find(x=>x.id===b.dataset.id);closeSheet();if(s)startSession(s.name,s.exercises.map(e=>({name:e.name,sets:e.sets.map(x=>withT({kg:'',reps:''},x))})))};
A['g-saver']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  openSheet(`<h3>Nouvelle routine</h3><div class="field"><label for="rn">Nom</label><input class="inp" id="rn" value="${esc(s.name)}"></div><button class="btn block" data-act="g-saver-ok" data-id="${s.id}">Enregistrer la routine</button>`);
};
A['g-saver-ok']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  S.routines.push({id:uid(),name:$('#rn').value.trim()||s.name,exercises:s.exercises.map(e=>({name:e.name,sets:e.sets.map(x=>withT({kg:'',reps:''},x))}))});
  persist('routines');closeSheet();toast('Routine enregistrée');render();
};
A['g-sdel']=b=>confirmSheet('Supprimer cette séance ?','Elle sera retirée de l’historique et de la progression.','Supprimer',()=>{const s=S.sessions.find(x=>x.id===b.dataset.id);S.sessions=S.sessions.filter(x=>x.id!==b.dataset.id);if(s)persist('sessions',s.date);render()});

/* séries par muscle sur 7 jours glissants (2026.10.14-5) : par série de travail, +1 à chaque muscle principal
   et +0,5 à chaque secondaire (EXI, js3c.js) ; exercice sans muscles renseignés ignoré */
function musWeek(){
  const from=dn(today())-7,c={};
  for(const ses of S.sessions){
    if(!ses||!ses.date||dn(ses.date)<=from)continue;
    for(const e of ses.exercises||[]){
      const x=EXI[e.name],n=workSets(e.sets).length;if(!x||!n)continue;
      (Array.isArray(x.m)?x.m:[]).forEach(m=>{c[m]=(c[m]||0)+n});
      (Array.isArray(x.s)?x.s:[]).forEach(m=>{c[m]=(c[m]||0)+n*.5});
    }
  }
  return Object.entries(c).filter(([,v])=>v>0).sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'fr'));
}
const MUS_LO=10,MUS_HI=20;
function musCard(){
  const ui=S.ui||(S.ui={}),closed=!!ui.gMusClosed,l=musWeek();
  const top=Math.max(MUS_HI+2,...l.map(x=>x[1])),pc=v=>Math.round(v/top*1000)/10;
  const body=l.length?`<div class="musl">${l.map(([m,v])=>`<div class="musr"><div class="row sb"><span>${esc(m)}</span><b class="num">${nf(v,1)}</b></div>
    <div class="mtrack" aria-hidden="true"><i class="mzone" style="left:${pc(MUS_LO)}%;width:${pc(MUS_HI-MUS_LO)}%"></i><i class="mfill" style="width:${pc(v)}%"></i></div></div>`).join('')}</div>
    <div class="small muted" style="margin-top:10px">Repère courant : ${MUS_LO} à ${MUS_HI} séries par muscle et par semaine (zone claire). Une série compte 1 pour le muscle principal et 0,5 pour un muscle secondaire ; l’échauffement ne compte pas.</div>`
    :'<div class="small muted">Aucune série de travail ces 7 derniers jours.</div>';
  return `<div class="card"><h2 style="margin:0"><button class="whead" data-act="g-mus" aria-expanded="${!closed}" aria-controls="gmus">${ICON.chev}<span>Séries par muscle (7 jours)</span>${closed&&l.length?`<small>${l.length} muscle${l.length>1?'s':''}</small>`:''}</button></h2>${closed?'':`<div id="gmus" style="margin-top:12px">${body}</div>`}</div>`;
}
A['g-mus']=()=>{const ui=S.ui||(S.ui={});ui.gMusClosed=!ui.gMusClosed;saveLocal();render()};

/* progression */
function progressView(){
  const names=[...new Set(S.sessions.flatMap(s=>s.exercises.filter(e=>workSets(e.sets).length).map(e=>e.name)))];
  if(!names.length)return '<div class="card empty">Termine une séance pour voir l’évolution de tes charges, exercice par exercice.</div>';
  const rows=names.map(n=>{const h=history(n);return{n,h,last:h[h.length-1]}}).sort((a,b)=>b.last.date.localeCompare(a.last.date));
  if(!progEx||!names.includes(progEx))progEx=rows[0].n;
  const cur=rows.find(r=>r.n===progEx),h=cur.h;
  const val=p=>progMetric==='top'?num(p.top.kg):progMetric==='e1'?p.e1:p.vol;
  const unit='kg';
  const best=h.reduce((b,p)=>!b||num(p.top.kg)>num(b.top.kg)?p:b,null),bestE=h.reduce((m,p)=>Math.max(m,p.e1),0);
  const list=rows.map(r=>{
    const l=r.h[r.h.length-1],pv=r.h[r.h.length-2],dl=pv?num(l.top.kg)-num(pv.top.kg):null;
    return `<button class="li" data-act="g-prog" data-n="${esc(r.n)}" ${r.n===progEx?'style="font-weight:700"':''}>${thumb(r.n,44)}<div class="grow"><div class="t">${esc(r.n)}</div><div class="small muted">${nf(num(l.top.kg),2)} kg × ${nf(num(l.top.reps),0)} · ${r.h.length} séance${r.h.length>1?'s':''}</div></div>${dl==null?'<span class="small muted">1re fois</span>':`<span class="num delta ${dl>0?'up':dl<0?'down':''}" style="font-weight:800">${dl>0?'▲ +':dl<0?'▼ −':'= '}${dl===0?'':nf(Math.abs(dl),2)}</span>`}</button>`;
  }).join('');
  return `<div class="card"><div class="row sb" style="margin-bottom:10px"><h2 style="margin:0">${esc(progEx)}</h2></div>
  <div class="seg"><button data-act="g-metric" data-m="top" aria-selected="${progMetric==='top'}">Charge max</button><button data-act="g-metric" data-m="e1" aria-selected="${progMetric==='e1'}">1RM estimé</button><button data-act="g-metric" data-m="vol" aria-selected="${progMetric==='vol'}">Volume</button></div>
  <div class="readout" id="gread"></div><div class="chartbox" id="gchart"></div>
  <div class="stats" style="margin-top:12px;grid-template-columns:1fr 1fr"><div class="stat"><span>Record de charge</span><b>${nf(num(best.top.kg),2)}</b><span>kg × ${nf(num(best.top.reps),0)}</span></div><div class="stat"><span>1RM estimé max</span><b>${nf(bestE,1)}</b><span>kg (formule d’Epley)</span></div></div></div>
  ${musCard()}
  <div class="card"><h2>Mes exercices</h2><div class="list">${list}</div><div class="small muted" style="margin-top:8px">La flèche compare ta charge max à la séance précédente.</div></div>`;
}
VIEWS.gym_after=()=>{
  tick();
  const el=$('#gchart');if(!el||!progEx)return;
  const h=history(progEx);if(!h.length)return;
  const val=p=>progMetric==='top'?num(p.top.kg):progMetric==='e1'?p.e1:p.vol;
  const pts=h.map(p=>({x:p.x,y:Math.round(val(p)*100)/100,p}));
  const rd=$('#gread');
  const show=pt=>{const p=pt.p;rd.innerHTML='<b>'+nf(pt.y,progMetric==='vol'?0:2)+' kg</b> <span class="muted small">'+esc(fmtDay(p.date))+' · '+nf(num(p.top.kg),2)+' × '+nf(num(p.top.reps),0)+'</span>'};
  show(pts[pts.length-1]);
  chart(el,{pts,lineRaw:true,dot:4,minSpan:progMetric==='vol'?100:5,label:'Progression de '+progEx,onPick:show});
};
A['g-prog']=b=>{progEx=b.dataset.n;render();window.scrollTo({top:0,behavior:'smooth'})};
A['g-metric']=b=>{progMetric=b.dataset.m;render()};

