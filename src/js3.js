/* ===== GYM ===== */
const LIB=[['Pectoraux',['Développé couché','Développé incliné barre','Développé incliné haltères','Développé couché haltères','Développé décliné','Développé couché machine','Écarté haltères','Écarté poulie','Pec deck','Pompes','Dips']],['Dos',['Tractions','Tractions supination','Tirage vertical','Tirage vertical prise serrée','Rowing barre','Rowing haltère','Tirage horizontal','Rowing T-bar','Soulevé de terre','Pull-over poulie','Shrugs haltères']],['Épaules',['Développé militaire','Développé haltères assis','Arnold press','Élévations latérales','Élévations frontales','Oiseau','Face pull']],['Biceps',['Curl barre','Curl haltères','Curl marteau','Curl pupitre','Curl incliné','Curl poulie']],['Triceps',['Extension poulie','Extension poulie corde','Barre au front','Dips banc','Extension nuque haltère','Extension verticale poulie','Développé serré']],['Jambes',['Squat','Squat avant','Goblet squat','Hack squat','Presse à cuisses','Fentes','Fentes marchées','Leg extension','Leg curl','Leg curl assis','Soulevé de terre roumain','Hip thrust','Mollets debout','Mollets assis']],['Abdos',['Crunch','Crunch poulie','Relevé de jambes','Gainage']]];
/* muscles sollicités par exercice */
const EXI={"Développé couché":{"i":"barbell-bench-press-medium-grip","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé incliné barre":{"i":"barbell-incline-bench-press-medium-grip","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé incliné haltères":{"i":"incline-dumbbell-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé couché haltères":{"i":"dumbbell-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé décliné":{"i":"decline-barbell-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Développé couché machine":{"i":"machine-bench-press","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Écarté haltères":{"i":"dumbbell-flyes","m":["Pectoraux"],"s":[]},"Écarté poulie":{"i":"cable-crossover","m":["Pectoraux"],"s":["Épaules"]},"Pec deck":{"i":"butterfly","m":["Pectoraux"],"s":[]},"Pompes":{"i":"pushups","m":["Pectoraux"],"s":["Épaules","Triceps"]},"Dips":{"i":"parallel-bar-dip","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Tractions":{"i":"pullups","m":["Grand dorsal"],"s":["Biceps","Milieu du dos"]},"Tractions supination":{"i":"chin-up","m":["Grand dorsal"],"s":["Biceps","Avant-bras","Milieu du dos"]},"Tirage vertical":{"i":"wide-grip-lat-pulldown","m":["Grand dorsal"],"s":["Biceps","Milieu du dos","Épaules"]},"Tirage vertical prise serrée":{"i":"close-grip-front-lat-pulldown","m":["Grand dorsal"],"s":["Biceps","Milieu du dos","Épaules"]},"Rowing barre":{"i":"bent-over-barbell-row","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Rowing haltère":{"i":"one-arm-dumbbell-row","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Tirage horizontal":{"i":"seated-cable-rows","m":["Milieu du dos"],"s":["Biceps","Grand dorsal","Épaules"]},"Rowing T-bar":{"i":"t-bar-row-with-handle","m":["Milieu du dos"],"s":["Biceps","Grand dorsal"]},"Soulevé de terre":{"i":"barbell-deadlift","m":["Lombaires"],"s":["Mollets","Avant-bras","Fessiers"]},"Pull-over poulie":{"i":"straight-arm-pulldown","m":["Grand dorsal"],"s":[]},"Shrugs haltères":{"i":"dumbbell-shrug","m":["Trapèzes"],"s":[]},"Développé militaire":{"i":"standing-military-press","m":["Épaules"],"s":["Triceps"]},"Développé haltères assis":{"i":"dumbbell-shoulder-press","m":["Épaules"],"s":["Triceps"]},"Élévations latérales":{"i":"side-lateral-raise","m":["Épaules"],"s":[]},"Élévations frontales":{"i":"front-dumbbell-raise","m":["Épaules"],"s":[]},"Oiseau":{"i":"reverse-flyes","m":["Épaules"],"s":[]},"Face pull":{"i":"face-pull","m":["Épaules"],"s":["Milieu du dos"]},"Arnold press":{"i":"arnold-dumbbell-press","m":["Épaules"],"s":["Triceps"]},"Curl barre":{"i":"barbell-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl haltères":{"i":"dumbbell-bicep-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl marteau":{"i":"hammer-curls","m":["Biceps"],"s":[]},"Curl pupitre":{"i":"preacher-curl","m":["Biceps"],"s":[]},"Curl incliné":{"i":"alternate-incline-dumbbell-curl","m":["Biceps"],"s":["Avant-bras"]},"Curl poulie":{"i":"standing-biceps-cable-curl","m":["Biceps"],"s":[]},"Extension poulie":{"i":"triceps-pushdown","m":["Triceps"],"s":[]},"Extension poulie corde":{"i":"triceps-pushdown-rope-attachment","m":["Triceps"],"s":[]},"Barre au front":{"i":"ez-bar-skullcrusher","m":["Triceps"],"s":["Avant-bras"]},"Dips banc":{"i":"bench-dips","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Extension nuque haltère":{"i":"standing-dumbbell-triceps-extension","m":["Triceps"],"s":[]},"Extension verticale poulie":{"i":"cable-rope-overhead-triceps-extension","m":["Triceps"],"s":[]},"Développé serré":{"i":"close-grip-barbell-bench-press","m":["Triceps"],"s":["Pectoraux","Épaules"]},"Squat":{"i":"barbell-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Squat avant":{"i":"front-barbell-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Goblet squat":{"i":"goblet-squat","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Hack squat":{"i":"barbell-hack-squat","m":["Quadriceps"],"s":["Mollets","Avant-bras","Ischio-jambiers"]},"Presse à cuisses":{"i":"leg-press","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Fentes":{"i":"dumbbell-lunges","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Fentes marchées":{"i":"barbell-walking-lunge","m":["Quadriceps"],"s":["Mollets","Fessiers","Ischio-jambiers"]},"Leg extension":{"i":"leg-extensions","m":["Quadriceps"],"s":[]},"Leg curl":{"i":"lying-leg-curls","m":["Ischio-jambiers"],"s":[]},"Leg curl assis":{"i":"seated-leg-curl","m":["Ischio-jambiers"],"s":[]},"Soulevé de terre roumain":{"i":"romanian-deadlift","m":["Ischio-jambiers"],"s":["Mollets","Fessiers","Lombaires"]},"Hip thrust":{"i":"barbell-hip-thrust","m":["Fessiers"],"s":["Mollets","Ischio-jambiers"]},"Mollets debout":{"i":"standing-calf-raises","m":["Mollets"],"s":[]},"Mollets assis":{"i":"seated-calf-raise","m":["Mollets"],"s":[]},"Crunch":{"i":"crunches","m":["Abdominaux"],"s":[]},"Relevé de jambes":{"i":"hanging-leg-raise","m":["Abdominaux"],"s":[]},"Crunch poulie":{"i":"cable-crunch","m":["Abdominaux"],"s":[]},"Gainage":{"i":"plank","m":["Abdominaux"],"s":[]}};
function thumb(name,size){
  const id=ILL[name],st=size?'style="width:'+size+'px;height:'+size+'px"':'';
  return id?'<img class="thumb" '+st+' src="ill/'+id+'-t.webp" alt="" loading="lazy" decoding="async">':'<div class="thumb ph" '+st+' aria-hidden="true">'+esc((name||'?').trim().charAt(0).toUpperCase())+'</div>';
}

let gymTab='sessions',gymOpen=false,progEx=null,progMetric='top',exQuery='',restEnd=0;
const fmtKg=v=>nf(v,2);
const e1rm=(kg,reps)=>reps<=1?kg:kg*(1+reps/30);
const setVol=s=>num(s.kg)*num(s.reps);
const topSet=sets=>sets.reduce((b,s)=>!b||num(s.kg)>num(b.kg)||(num(s.kg)===num(b.kg)&&num(s.reps)>num(b.reps))?s:b,null);
const sessVol=ses=>ses.exercises.reduce((t,e)=>t+e.sets.reduce((u,s)=>u+setVol(s),0),0);
function lastPerf(name){
  for(const ses of S.sessions){const e=ses.exercises.find(x=>x.name===name);if(e)return e.sets}
  return null;
}
function history(name){
  const out=[];
  for(const ses of S.sessions.slice().reverse()){
    const e=ses.exercises.find(x=>x.name===name);if(!e||!e.sets.length)continue;
    const top=topSet(e.sets),best=e.sets.reduce((m,s)=>Math.max(m,e1rm(num(s.kg),num(s.reps))),0);
    out.push({date:ses.date,x:dn(ses.date),top,e1:best,vol:e.sets.reduce((t,s)=>t+setVol(s),0)});
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
  S.active={id:uid(),name:name||'Séance',start:Date.now(),exercises:exs.map(e=>({name:e.name,sets:mkSets(e.sets||3).map(x=>({kg:e.kg?String(e.kg):'',reps:e.reps?String(e.reps):'',done:false}))}))};
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
  ${S.routines.length?'<div class="list">'+S.routines.map(r=>`<div class="row"><button class="li" data-act="g-rstart" data-id="${r.id}"><div class="grow"><div class="t">${esc(r.name)}</div><div class="small muted">${r.exercises.length} exercice${r.exercises.length>1?'s':''}${r.exercises.length?' · '+esc(r.exercises.slice(0,3).map(e=>e.name).join(', '))+(r.exercises.length>3?'…':''):''}</div></div><span class="pill neutral">Démarrer</span></button><button class="iconbtn" style="box-shadow:none;background:var(--surface2)" data-act="g-redit" data-id="${r.id}" aria-label="Modifier la routine ${esc(r.name)}"><span style="font-size:19px;line-height:1">⋯</span></button></div>`).join('')+'</div>'
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
    const prev=lastPerf(e.name)||[];
    const rows=e.sets.map((s,si)=>{
      const p=prev[si];
      return `<div class="r ${s.done?'done':''}" style="display:contents"><div class="n">${si+1}</div><div class="prev">${p?nf(num(p.kg),2)+' × '+nf(num(p.reps),0):'—'}</div>
      <input inputmode="decimal" data-in="set" data-e="${ei}" data-s="${si}" data-f="kg" value="${esc(s.kg)}" placeholder="${p?nf(num(p.kg),2):'kg'}" aria-label="Charge série ${si+1}">
      <input inputmode="numeric" data-in="set" data-e="${ei}" data-s="${si}" data-f="reps" value="${esc(s.reps)}" placeholder="${p?nf(num(p.reps),0):'reps'}" aria-label="Répétitions série ${si+1}">
      <button class="ck" data-act="g-check" data-e="${ei}" data-s="${si}" aria-pressed="${s.done}" aria-label="Série ${si+1} faite">${ICON.check}</button></div>`;
    }).join('');
    return `<div class="card ex"><div class="hd"><button class="thumbbtn" data-act="g-exinfo" data-name="${esc(e.name)}" aria-label="Voir l’exercice ${esc(e.name)}">${thumb(e.name,48)}</button><b style="flex:1;min-width:0;overflow-wrap:anywhere">${esc(e.name)}</b><button class="iconbtn" style="width:40px;height:40px;box-shadow:none;background:var(--surface2)" data-act="g-exmenu" data-e="${ei}" aria-label="Options de l’exercice"><span style="font-size:20px;line-height:1">⋯</span></button></div>
    <div class="sets"><div class="h">#</div><div class="h">Avant</div><div class="h">kg</div><div class="h">Reps</div><div class="h">OK</div>${rows}</div>
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
    s.done=true;startRest(S.settings.rest);
  }else s.done=false;
  persist('active');render();
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
function exPicker(){
  const q=exQuery.toLowerCase().trim(),all=allExNames();
  const tgt=routEdit&&!(S.active&&gymOpen)?curRoutine():S.active;
  const used=new Set(tgt?tgt.exercises.map(e=>e.name):[]);
  const row=n=>{const e=EXI[n];return `<button class="li" data-act="g-pickex" data-name="${esc(n)}" ${used.has(n)?'style="opacity:.5"':''}>${thumb(n)}<div class="grow"><div class="t">${esc(n)}</div>${e?'<div class="small muted">'+esc(e.m.join(', '))+'</div>':''}</div>${used.has(n)?'<span class="small muted">ajouté</span>':''}</button>`};
  const create=q&&!all.some(n=>n.toLowerCase()===q)?`<button class="btn soft block" style="margin-bottom:10px" data-act="g-newex" data-name="${esc(exQuery.trim())}">${ICON.plus} Créer « ${esc(exQuery.trim())} »</button>`:'';
  if(q){const names=all.filter(n=>n.toLowerCase().includes(q)).sort((a,b)=>a.localeCompare(b,'fr'));return create+'<div class="list">'+names.map(row).join('')+'</div>'}
  const inLib=new Set(LIB.flatMap(g=>g[1])),rec=[];
  for(const ses of S.sessions){for(const e of ses.exercises)if(!rec.includes(e.name))rec.push(e.name);if(rec.length>=6)break}
  const others=all.filter(n=>!inLib.has(n)).sort((a,b)=>a.localeCompare(b,'fr'));
  let h='';
  if(rec.length)h+='<div class="sec">Récents</div><div class="list">'+rec.slice(0,6).map(row).join('')+'</div>';
  LIB.forEach(([g,names])=>{h+='<div class="sec" style="margin-top:16px">'+g+'</div><div class="list">'+names.map(row).join('')+'</div>'});
  if(others.length)h+='<div class="sec" style="margin-top:16px">Mes exercices</div><div class="list">'+others.map(row).join('')+'</div>';
  return h;
}
A['g-addex']=()=>{exQuery='';openSheet(`<h3>Ajouter un exercice</h3><div class="field"><input class="inp" id="exq" data-in="exq" placeholder="Rechercher ou créer" aria-label="Rechercher un exercice"></div><div id="exlist">${exPicker()}</div>`)};
I.exq=t=>{exQuery=t.value;$('#exlist').innerHTML=exPicker()};
function pushEx(name){
  if(routEdit&&!(S.active&&gymOpen)){const r=curRoutine();if(r){r.exercises.push({name,sets:3,kg:'',reps:''});persist('routines')}closeSheet();render();return}
  S.active.exercises.push({name,sets:mkSets(3)});persist('active');closeSheet();render();
  setTimeout(()=>{const cs=document.querySelectorAll('.ex');if(cs.length)cs[cs.length-1].scrollIntoView({behavior:'smooth',block:'center'})},60);
}
A['g-pickex']=b=>pushEx(b.dataset.name);
A['g-newex']=b=>{const n=b.dataset.name;if(!n)return;if(!allExNames().includes(n)){S.exercises.push(n);persist('exercises')}pushEx(n)};

/* finish */
A['g-finish']=()=>{
  const a=S.active,done=a.exercises.reduce((t,e)=>t+e.sets.filter(s=>s.done).length,0),skip=a.exercises.reduce((t,e)=>t+e.sets.filter(s=>!s.done).length,0);
  if(!done){toast('Coche au moins une série');return}
  confirmSheet('Terminer la séance ?',done+' série'+(done>1?'s':'')+' validée'+(done>1?'s':'')+(skip?'. '+skip+' non cochée'+(skip>1?'s':'')+' ne seront pas gardées.':'.'),'Terminer',finishSession);
};
function finishSession(){
  const a=S.active;
  const exs=a.exercises.map(e=>({name:e.name,sets:e.sets.filter(s=>s.done).map(s=>({kg:num(s.kg),reps:num(s.reps)}))})).filter(e=>e.sets.length);
  const date=ymd(new Date(a.start)),prevBest={};
  exs.forEach(e=>{const h=history(e.name);prevBest[e.name]=h.reduce((m,x)=>Math.max(m,num(x.top.kg)),0)});
  const ses={id:a.id,date,name:a.name||'Séance',dur:Math.max(1,Math.round((Date.now()-a.start)/60000)),exercises:exs};
  S.sessions.unshift(ses);S.sessions.sort((x,y)=>y.date.localeCompare(x.date));
  S.active=null;restEnd=0;gymOpen=false;persist('sessions',date);persist('active');
  const recs=exs.filter(e=>{const t=topSet(e.sets);return prevBest[e.name]>0&&num(t.kg)>prevBest[e.name]}).map(e=>{const t=topSet(e.sets);return e.name+' : '+nf(num(t.kg),2)+' kg × '+nf(num(t.reps),0)});
  openSheet(`<h3>Séance enregistrée</h3><div class="stats" style="margin-bottom:14px"><div class="stat"><span>Durée</span><b>${ses.dur}</b><span>min</span></div><div class="stat"><span>Séries</span><b>${exs.reduce((t,e)=>t+e.sets.length,0)}</b><span>validées</span></div><div class="stat"><span>Volume</span><b>${nf(sessVol(ses),0)}</b><span>kg</span></div></div>
  ${recs.length?'<div class="card" style="box-shadow:none"><h2>Nouveaux records de charge</h2>'+recs.map(r=>'<div style="padding:4px 0;font-weight:600">'+esc(r)+'</div>').join('')+'</div>':''}
  <div class="grid2"><button class="btn soft" data-act="g-saver" data-id="${ses.id}">Garder comme routine</button><button class="btn" data-act="close">Fermer</button></div>`);
  render();
}

/* session detail */
A['g-view']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  openSheet(`<h3>${esc(s.name)}</h3><div class="small muted" style="margin:-8px 0 12px">${esc(fmtLong(s.date))} · ${s.dur||'?'} min · ${nf(sessVol(s),0)} kg</div>
  ${s.exercises.map(e=>`<div class="card" style="box-shadow:none"><b>${esc(e.name)}</b><div class="small" style="margin-top:6px;line-height:1.7">${e.sets.map((x,i)=>`<span class="pill neutral" style="margin:0 6px 4px 0">${nf(num(x.kg),2)} × ${nf(num(x.reps),0)}</span>`).join('')}</div></div>`).join('')}
  <div class="grid2" style="margin-bottom:10px"><button class="btn soft" data-act="g-redo" data-id="${s.id}">Refaire</button><button class="btn soft" data-act="g-saver" data-id="${s.id}">En faire une routine</button></div>
  <button class="btn danger block" data-act="g-sdel" data-id="${s.id}">Supprimer</button>`);
};
A['g-redo']=b=>{const s=S.sessions.find(x=>x.id===b.dataset.id);closeSheet();if(s)startSession(s.name,s.exercises.map(e=>({name:e.name,sets:e.sets.length})))};
A['g-saver']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  openSheet(`<h3>Nouvelle routine</h3><div class="field"><label for="rn">Nom</label><input class="inp" id="rn" value="${esc(s.name)}"></div><button class="btn block" data-act="g-saver-ok" data-id="${s.id}">Enregistrer la routine</button>`);
};
A['g-saver-ok']=b=>{
  const s=S.sessions.find(x=>x.id===b.dataset.id);if(!s)return;
  S.routines.push({id:uid(),name:$('#rn').value.trim()||s.name,exercises:s.exercises.map(e=>({name:e.name,sets:e.sets.length}))});
  persist('routines');closeSheet();toast('Routine enregistrée');render();
};
A['g-sdel']=b=>confirmSheet('Supprimer cette séance ?','Elle sera retirée de l’historique et de la progression.','Supprimer',()=>{const s=S.sessions.find(x=>x.id===b.dataset.id);S.sessions=S.sessions.filter(x=>x.id!==b.dataset.id);if(s)persist('sessions',s.date);render()});

/* progression */
function progressView(){
  const names=[...new Set(S.sessions.flatMap(s=>s.exercises.map(e=>e.name)))];
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

A['g-exinfo']=b=>{
  const n=b.dataset.name,e=EXI[n];
  if(!e){openSheet(`<h3>${esc(n)}</h3><div class="muted" style="margin-bottom:12px">Pas d’illustration pour cet exercice.</div><button class="btn block" data-act="close">Fermer</button>`);return}
  openSheet(`<h3>${esc(n)}</h3>
  <img class="mmap" src="img2/${e.i}-m.png" alt="Muscles sollicités : ${esc(e.m.join(', '))}">
  <div class="row" style="gap:14px;justify-content:center;margin:6px 0 14px"><span class="small"><i class="lg" style="background:#D8483A"></i>Principal</span><span class="small"><i class="lg" style="background:#F0AAA2"></i>Secondaire</span><span class="small muted">Face · Dos</span></div>
  <div class="sec">Muscles principaux</div><div class="row" style="flex-wrap:wrap;gap:6px;margin-bottom:12px">${e.m.map(m=>`<span class="pill bad">${esc(m)}</span>`).join('')}</div>
  ${e.s.length?`<div class="sec">Muscles secondaires</div><div class="row" style="flex-wrap:wrap;gap:6px;margin-bottom:14px">${e.s.map(m=>`<span class="pill neutral">${esc(m)}</span>`).join('')}</div>`:''}
  <div class="sec">Le mouvement</div>
  <div class="exinfo"><figure><img src="img/${e.i}-0.jpg" alt="Position de départ"><figcaption>Départ</figcaption></figure><figure><img src="img/${e.i}-1.jpg" alt="Position d’arrivée"><figcaption>Arrivée</figcaption></figure></div>`);
};
