/* ===== ILLUSTRATIONS DES MOUVEMENTS (open-exercise-illustrations, CC0) ===== */
const ILL={"Développé couché": "bench-press", "Développé incliné barre": "incline-bench-press", "Développé incliné haltères": "incline-dumbbell-press", "Développé couché haltères": "dumbbell-chest-press", "Développé décliné": "decline-bench-press", "Développé couché machine": "chest-press-machine", "Écarté haltères": "dumbbell-fly", "Écarté poulie": "cable-crossover", "Pec deck": "pec-deck", "Pompes": "push-up", "Dips": "dips", "Tractions": "pull-up", "Tractions supination": "chin-up", "Tirage vertical": "lat-pulldown", "Tirage vertical prise serrée": "close-grip-lat-pulldown", "Rowing barre": "bent-over-row", "Rowing haltère": "dumbbell-row", "Tirage horizontal": "seated-cable-row", "Rowing T-bar": "t-bar-row", "Soulevé de terre": "deadlift", "Pull-over poulie": "straight-arm-pulldown", "Shrugs haltères": "dumbbell-shrug", "Développé militaire": "overhead-press", "Développé haltères assis": "dumbbell-shoulder-press", "Arnold press": "arnold-press", "Élévations latérales": "lateral-raises", "Élévations frontales": "front-raises", "Oiseau": "rear-delt-fly", "Face pull": "face-pulls", "Curl barre": "barbell-curl", "Curl haltères": "biceps-curl", "Curl marteau": "hammer-curls", "Curl pupitre": "preacher-curl", "Curl incliné": "incline-dumbbell-curl", "Curl poulie": "cable-curl", "Extension poulie": "tricep-pushdowns", "Extension poulie corde": "tricep-pushdowns", "Barre au front": "skull-crushers", "Dips banc": "bench-dip", "Extension nuque haltère": "overhead-triceps-extension", "Extension verticale poulie": "cable-overhead-triceps-extension", "Développé serré": "close-grip-bench-press", "Squat": "squat", "Squat avant": "front-squat", "Goblet squat": "goblet-squat", "Hack squat": "hack-squat", "Presse à cuisses": "leg-press", "Fentes": "dumbbell-lunge", "Fentes marchées": "dumbbell-lunge", "Leg extension": "leg-extension", "Leg curl": "leg-curl", "Leg curl assis": "seated-leg-curl", "Soulevé de terre roumain": "romanian-deadlift", "Hip thrust": "hip-thrusts", "Mollets debout": "calf-raises", "Mollets assis": "seated-calf-raise", "Crunch": "crunches", "Crunch poulie": "cable-crunch", "Relevé de jambes": "hanging-leg-raise", "Gainage": "plank"};
const ILL1=new Set(['plank']);
/* ===== MINUTEUR DE REPOS : barre fixe, accessible au pouce pendant toute la séance ===== */
let restTotal=0,restBarState='',restRang=false;
const mmss=s=>Math.floor(s/60)+':'+pad(s%60);
function startRest(sec){restTotal=sec;restEnd=Date.now()+sec*1000;restRang=false;syncRestBar()}
function syncRestBar(){
  let el=$('#rbar');
  const want=(tab==='gym'&&gymOpen&&S.active)?(restEnd>Date.now()?'on':'idle'):'';
  if(!want){if(el)el.remove();restBarState='';return}
  if(!el||restBarState!==want){
    if(el)el.remove();
    el=document.createElement('div');el.id='rbar';el.className='rbar'+(want==='on'?' on':'');
    el.innerHTML=want==='on'
      ?`<i id="rfill"></i><button class="rmain" data-act="g-rest-less" aria-label="Enlever 15 secondes">−15</button>
        <button class="rclock" data-act="g-rest-dur" aria-label="Changer la durée du repos"><span class="small" style="opacity:.75;font-weight:700">REPOS</span><b id="rclk">0:00</b></button>
        <button class="rmain" data-act="g-rest-more" aria-label="Ajouter 15 secondes">+15</button>
        <button class="rmain" data-act="g-rest-skip">Passer</button>`
      :`<button class="rgo" data-act="g-rest-go">⏱ Démarrer le repos</button>
        <button class="rdur" data-act="g-rest-dur" aria-label="Changer la durée du repos"><span id="rdef">${mmss(S.settings.rest)}</span> ▾</button>`;
    document.body.appendChild(el);restBarState=want;
  }
  if(want==='on'){
    const ms=restEnd-Date.now(),left=Math.ceil(ms/1000);
    if(left<=0){
      if(!restRang){restRang=true;toast('Repos terminé');try{navigator.vibrate&&navigator.vibrate([200,90,200])}catch(_){}}
      restEnd=0;syncRestBar();return;
    }
    const c=$('#rclk');if(c)c.textContent=mmss(left);
    const f=$('#rfill');if(f&&restTotal)f.style.width=clamp(ms/(restTotal*1000)*100,0,100)+'%';
  }else{const d=$('#rdef');if(d)d.textContent=mmss(S.settings.rest)}
}
A['g-rest-go']=()=>startRest(S.settings.rest);
A['g-rest-more']=()=>{restEnd=Math.max(restEnd,Date.now())+15000;restTotal+=15;syncRestBar()};
A['g-rest-less']=()=>{restEnd=Math.max(Date.now()+1000,restEnd-15000);syncRestBar()};
A['g-rest-dur']=()=>{
  const opts=[30,45,60,90,120,150,180,240];
  openSheet(`<h3>Durée du repos</h3><p class="muted small" style="margin:-8px 0 14px">La durée choisie démarre le repos et devient ta durée par défaut après chaque série validée.</p>
  <div class="durs">${opts.map(s=>`<button class="dur${s===S.settings.rest?' on':''}" data-act="g-rest-set" data-s="${s}">${mmss(s)}</button>`).join('')}</div>
  <button class="btn ghost block" style="margin-top:14px" data-act="close">Fermer</button>`);
};
A['g-rest-set']=b=>{S.settings.rest=+b.dataset.s;persist('settings');closeSheet();startRest(S.settings.rest)};

/* ===== FICHE D’EXERCICE : le mouvement en images qui s’enchaînent ===== */
let movT=null;
function playMov(){
  clearInterval(movT);
  movT=setInterval(()=>{
    const w=$('#mov');
    if(!w||!document.body.contains(w)){clearInterval(movT);movT=null;return}
    if(w.dataset.play==='0')return;
    const n=w.dataset.f==='1'?'0':'1';w.dataset.f=n;
    w.querySelectorAll('img').forEach((im,i)=>im.classList.toggle('on',String(i)===n));
    const c=$('#movcap');if(c)c.textContent=n==='1'?'Arrivée':'Départ';
  },950);
}
A['mov-toggle']=()=>{
  const w=$('#mov');if(!w)return;
  const p=w.dataset.play==='0'?'1':'0';w.dataset.play=p;
  const b=$('#movbtn');if(b)b.textContent=p==='0'?'▶ Reprendre':'❚❚ Pause';
};
let movRed=true;
A['mov-red']=()=>{
  const w=$('#mov');if(!w)return;
  movRed=!movRed;
  w.querySelectorAll('img').forEach((im,i)=>im.src='ill/'+w.dataset.id+'-'+i+(movRed?'r':'')+'.webp');
  const b=$('#redbtn');if(b)b.textContent=movRed?'Muscles en rouge':'Image simple';
};
A['g-exinfo']=b=>{
  const n=b.dataset.name,id=ILL[n],e=EXI[n];
  if(!id&&!e){openSheet(`<h3>${esc(n)}</h3><div class="muted" style="margin-bottom:12px">Pas d’illustration pour cet exercice.</div><button class="btn block" data-act="close">Fermer</button>`);return}
  const one=!id||ILL1.has(id),sfx=movRed?'r':'';
  const movie=id?`<div class="mov" id="mov" data-id="${id}" data-f="0" data-play="${one?'0':'1'}">
    <img src="ill/${id}-0${sfx}.webp" alt="Position de départ" class="on">${one?'':`<img src="ill/${id}-1${sfx}.webp" alt="Position d’arrivée">`}
    <span class="movcap" id="movcap">${one?'Position tenue':'Départ'}</span></div>
  <div class="row" style="gap:8px;margin:10px 0 4px">${one?'':`<button class="chip" id="movbtn" data-act="mov-toggle">❚❚ Pause</button>`}<button class="chip" id="redbtn" data-act="mov-red">${movRed?'Muscles en rouge':'Image simple'}</button></div>
  <div class="small muted" style="margin-bottom:16px">Rouge vif : muscles principaux. Rose : muscles secondaires.</div>`:'';
  openSheet(`<h3>${esc(n)}</h3>${movie}
  ${e?`<div class="sec">Muscles sollicités</div>
  <div class="row" style="align-items:flex-start;gap:14px;margin-bottom:6px">
    <img class="mmap" style="width:42%;max-width:132px" src="img2/${e.i}-m.png" alt="Schéma des muscles : ${esc(e.m.join(', '))}">
    <div class="grow" style="min-width:0">
      <div class="small muted" style="margin-bottom:4px">Principaux</div>
      <div class="row" style="flex-wrap:wrap;gap:6px;margin-bottom:10px">${e.m.map(m=>`<span class="pill bad">${esc(m)}</span>`).join('')}</div>
      ${e.s.length?`<div class="small muted" style="margin-bottom:4px">Secondaires</div><div class="row" style="flex-wrap:wrap;gap:6px">${e.s.map(m=>`<span class="pill neutral">${esc(m)}</span>`).join('')}</div>`:''}
    </div></div>`:''}
  <button class="btn ghost block" style="margin-top:14px" data-act="close">Fermer</button>`);
  if(!one)playMov();
};

/* ===== ROUTINES : préparer ses séances à l’avance ===== */
let routEdit=null;
const curRoutine=()=>S.routines.find(r=>r.id===routEdit)||null;
const NEWR='Nouvelle routine';
A['g-rnew']=()=>{const r={id:uid(),name:NEWR,exercises:[]};S.routines.push(r);persist('routines');routEdit=r.id;render();window.scrollTo(0,0)};
A['g-redit']=b=>{routEdit=b.dataset.id;render();window.scrollTo(0,0)};
A['g-rback']=()=>{
  const r=curRoutine();
  if(r&&!r.exercises.length&&r.name===NEWR){S.routines=S.routines.filter(x=>x.id!==r.id);persist('routines')}
  routEdit=null;render();window.scrollTo(0,0);
};
I.rname=t=>{const r=curRoutine();if(r){r.name=t.value;persist('routines')}};
I.rkg=t=>{const r=curRoutine();if(r){r.exercises[+t.dataset.i].kg=t.value;persist('routines')}};
I.rreps=t=>{const r=curRoutine();if(r){r.exercises[+t.dataset.i].reps=t.value;persist('routines')}};
A['g-rsets']=b=>{const r=curRoutine(),e=r.exercises[+b.dataset.i];e.sets=clamp((e.sets||3)+(+b.dataset.d),1,12);persist('routines');render()};
A['g-rexmenu']=b=>{
  const i=+b.dataset.i,r=curRoutine(),e=r.exercises[i];
  openSheet(`<h3>${esc(e.name)}</h3><div class="grid2" style="margin-bottom:10px">
  <button class="btn ghost" data-act="g-rmove" data-i="${i}" data-d="-1" ${i===0?'disabled style="opacity:.4"':''}>Monter</button>
  <button class="btn ghost" data-act="g-rmove" data-i="${i}" data-d="1" ${i===r.exercises.length-1?'disabled style="opacity:.4"':''}>Descendre</button></div>
  <button class="btn danger block" data-act="g-rdelex" data-i="${i}">Retirer de la routine</button>`);
};
A['g-rmove']=b=>{const r=curRoutine(),i=+b.dataset.i,j=i+(+b.dataset.d);if(j<0||j>=r.exercises.length)return;const a=r.exercises;[a[i],a[j]]=[a[j],a[i]];persist('routines');closeSheet();render()};
A['g-rdelex']=b=>{const r=curRoutine();r.exercises.splice(+b.dataset.i,1);persist('routines');closeSheet();render()};
A['g-rdup']=b=>{
  const r=S.routines.find(x=>x.id===b.dataset.id);if(!r)return;
  const c={id:uid(),name:r.name+' (copie)',exercises:r.exercises.map(e=>Object.assign({},e))};
  S.routines.push(c);persist('routines');closeSheet();routEdit=c.id;render();
};
A['g-rstart']=b=>{const r=S.routines.find(x=>x.id===b.dataset.id);if(!r||!r.exercises.length){toast('Ajoute au moins un exercice');return}routEdit=null;startSession(r.name,r.exercises)};
function routineView(){
  const r=curRoutine();if(!r)return gymHome();
  const rows=r.exercises.map((e,i)=>`<div class="card ex" style="padding:14px;margin-bottom:10px">
    <div class="hd"><button class="thumbbtn" data-act="g-exinfo" data-name="${esc(e.name)}" aria-label="Voir ${esc(e.name)}">${thumb(e.name,46)}</button>
      <b style="flex:1;min-width:0;overflow-wrap:anywhere">${esc(e.name)}</b>
      <button class="iconbtn" style="width:40px;height:40px;box-shadow:none;background:var(--surface2)" data-act="g-rexmenu" data-i="${i}" aria-label="Options"><span style="font-size:20px;line-height:1">⋯</span></button></div>
    <div class="rr">
      <button class="rstep" data-act="g-rsets" data-i="${i}" data-d="-1" aria-label="Une série de moins">−</button>
      <span><b class="num">${e.sets||3}</b><i>séries</i></span>
      <button class="rstep" data-act="g-rsets" data-i="${i}" data-d="1" aria-label="Une série de plus">+</button>
      <input class="rin" inputmode="decimal" data-in="rkg" data-i="${i}" value="${esc(e.kg||'')}" placeholder="kg" aria-label="Charge prévue en kg">
      <input class="rin" inputmode="numeric" data-in="rreps" data-i="${i}" value="${esc(e.reps||'')}" placeholder="reps" aria-label="Répétitions prévues">
    </div></div>`).join('');
  return `<div class="row sb" style="margin-bottom:12px"><button class="chip" data-act="g-rback">${ICON.chevL} Séances</button>
    <button class="btn" style="min-height:44px" data-act="g-rstart" data-id="${r.id}">Démarrer</button></div>
  <div class="field"><input class="inp" data-in="rname" value="${esc(r.name)}" aria-label="Nom de la routine" style="font-weight:700"></div>
  ${rows||'<div class="card empty">Ajoute les exercices de cette séance, dans l’ordre où tu les fais.</div>'}
  <button class="btn block" data-act="g-addex">${ICON.plus} Ajouter un exercice</button>
  <div class="small muted" style="margin:12px 2px 0">Les kilos et répétitions sont facultatifs : s’ils sont remplis, ils apparaîtront déjà saisis au début de la séance, il ne restera qu’à valider.</div>
  <div class="grid2" style="margin-top:16px"><button class="btn ghost" data-act="g-rdup" data-id="${r.id}">Dupliquer</button><button class="btn danger" data-act="g-rdel" data-id="${r.id}">Supprimer</button></div>`;
}
