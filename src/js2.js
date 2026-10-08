/* ===== WEIGHT ===== */
let wRange=30,wDate=null,wVal=null,wAll=false;
const sortedW=()=>Object.keys(S.weights).sort().map(d=>({d,x:dn(d),y:S.weights[d]}));
function movAvg(arr){return arr.map(p=>{const w=arr.filter(q=>q.x<=p.x&&q.x>p.x-7);return{x:p.x,y:w.reduce((s,q)=>s+q.y,0)/w.length}})}
function slopePerDay(arr){
  if(arr.length<4)return null;
  const n=arr.length,mx=arr.reduce((s,p)=>s+p.x,0)/n,my=arr.reduce((s,p)=>s+p.y,0)/n;
  let a=0,b=0;arr.forEach(p=>{a+=(p.x-mx)*(p.y-my);b+=(p.x-mx)*(p.x-mx)});
  return b?a/b:null;
}
const sgn=(v,d=1)=>(v>0?'+':v<0?'−':'')+nf(Math.abs(v),d);

/* progress ring toward the goal weight, one segment per step (default 2.5 kg) */
function milestones(start,goal,step){
  const dir=start>goal?-1:1,out=[],n=Math.floor(Math.abs(start-goal)/step+1e-9);
  for(let k=n;k>=1;k--){const v=goal-dir*k*step;if(dir<0?v<start-1e-6:v>start+1e-6)out.push(Math.round(v*100)/100)}
  out.push(goal);return out;
}
function arcPath(cx,cy,r,a0,a1){
  const p=a=>[cx+r*Math.cos((a-90)*Math.PI/180),cy+r*Math.sin((a-90)*Math.PI/180)];
  const [x0,y0]=p(a0),[x1,y1]=p(a1);return 'M'+x0.toFixed(2)+' '+y0.toFixed(2)+' A'+r+' '+r+' 0 '+((a1-a0)>180?1:0)+' 1 '+x1.toFixed(2)+' '+y1.toFixed(2);
}
function ringCard(arr){
  const g=S.settings.goalW,step=S.settings.step||2.5;
  if(!g)return '';
  if(!arr.length)return '<div class="card"><h2>Objectif '+nf(g)+' kg</h2><div class="muted small">Enregistre ta première pesée : le cercle se remplit à chaque palier de '+nf(step)+' kg.</div></div>';
  const start=S.settings.startW||arr[0].y,cur=arr[arr.length-1].y;
  const dir=start>g?-1:1,total=Math.abs(start-g);
  if(total<0.05)return '';
  const prog=clamp(dir<0?start-cur:cur-start,0,total);
  const ms=milestones(start,g,step),bounds=[start].concat(ms);
  const N=ms.length,gap=N>1?6:0,avail=360-gap*N,C=140,R=88;
  const pt=(ang,r)=>[C+r*Math.cos((ang-90)*Math.PI/180),C+r*Math.sin((ang-90)*Math.PI/180)];
  let a=gap/2,cum=0,reached=0,tracks='',fills='',ticks='',labels='',markerAng=null;
  const nextI=ms.findIndex(v=>dir<0?cur>v+0.05:cur<v-0.05),next=nextI<0?null:ms[nextI];
  for(let i=0;i<N;i++){
    const len=Math.abs(bounds[i+1]-bounds[i]),ang=len/total*avail,f=clamp((prog-cum)/len,0,1);
    tracks+='<path d="'+arcPath(C,C,R,a,a+ang)+'" fill="none" stroke="var(--surface2)" stroke-width="16" stroke-linecap="round"/>';
    if(f>0.001)fills+='<path d="'+arcPath(C,C,R,a,a+Math.max(ang*f,0.6))+'" fill="none" stroke="var(--accent)" stroke-width="16" stroke-linecap="round"/>';
    if(markerAng==null&&prog<=cum+len+1e-9)markerAng=a+ang*clamp((prog-cum)/len,0,1);
    const ok=f>=0.999,isNext=i===nextI,last=i===N-1,bA=a+ang+gap/2,[tx,ty]=pt(bA,R);
    if(ok)reached++;
    ticks+='<circle cx="'+tx.toFixed(1)+'" cy="'+ty.toFixed(1)+'" r="'+(last?9:7)+'" fill="'+(ok?'var(--accent)':'var(--surface)')+'" stroke="'+(ok?'var(--surface)':isNext?'var(--accent)':'var(--muted)')+'" stroke-width="'+(ok?3:isNext?3.5:2)+'"/>';
    const v=nf(bounds[i+1],2),col=ok?'var(--accent)':isNext?'var(--ink)':'var(--muted)',fw=ok||isNext||last?800:600;
    if(last)labels+='<text x="'+C+'" y="'+(C-R-21)+'" text-anchor="middle" font-size="14" font-weight="800" fill="'+col+'" class="num">'+v+' kg</text>';
    else{const [lx,ly]=pt(bA,R+27);labels+='<text x="'+lx.toFixed(1)+'" y="'+(ly+4.5).toFixed(1)+'" text-anchor="middle" font-size="13" font-weight="'+fw+'" fill="'+col+'" class="num">'+v+'</text>'}
    cum+=len;a+=ang+gap;
  }

  const [mx,my]=pt(markerAng==null?0:markerAng,R);
  const marker='<circle cx="'+mx.toFixed(1)+'" cy="'+my.toFixed(1)+'" r="11" fill="var(--accent)" stroke="var(--surface)" stroke-width="4"/><circle cx="'+mx.toFixed(1)+'" cy="'+my.toFixed(1)+'" r="3.5" fill="var(--on-accent)"/>';
  const done=prog>=total-0.05,pct=Math.round(prog/total*100),left=next==null?0:Math.abs(cur-next);
  const chips=ms.map((v,i)=>{const ok=dir<0?cur<=v+0.05:cur>=v-0.05;return '<span class="pal'+(ok?' ok':i===nextI?' next':'')+'">'+(ok?'✓ ':'')+nf(v,2)+'</span>'}).join('');
  return `<div class="card"><div class="row sb" style="margin-bottom:2px"><h2 style="margin:0">Objectif ${nf(g)} kg</h2><span class="pill neutral">${reached} / ${N} paliers</span></div>
  <div class="ringbig"><svg viewBox="0 0 280 280" role="img" aria-label="Progression vers ${nf(g)} kg : ${pct} pour cent, ${reached} paliers sur ${N}">${tracks}${fills}${ticks}${marker}${labels}</svg>
    <div class="c"><b class="num">${nf(cur)}</b><span class="muted small">kg</span><span class="pill ${done?'good':'neutral'}" style="margin-top:6px">${done?'Objectif atteint':pct+' %'}</span></div></div>
  <div style="text-align:center;margin:0 0 4px;font-weight:600">${done?'Bravo, tu es à ton objectif.':next==null?'':'Prochain palier : <b class="num">'+nf(next,2)+' kg</b> <span class="muted">· encore '+nf(left,1)+' kg</span>'}</div>
  <div class="small muted" style="text-align:center;margin-bottom:12px">Départ ${nf(start,1)} kg · ${nf(Math.abs(start-cur),1)} kg parcourus sur ${nf(total,1)}</div>
  <div class="pals">${chips}</div></div>`;
}
VIEWS.weight=()=>{
  const arr=sortedW(),d=wDate||today();
  if(wVal==null)wVal=S.weights[d]??(arr.length?arr[arr.length-1].y:70);
  const has=S.weights[d]!=null;
  let stats='';
  if(arr.length){
    const lastX=arr[arr.length-1].x;
    const l7=arr.filter(p=>p.x>lastX-7),avg7=l7.reduce((s,p)=>s+p.y,0)/l7.length;
    const l28=arr.filter(p=>p.x>lastX-28),sl=slopePerDay(l28);
    const third=S.settings.goalW?['Objectif',(()=>{const r=arr[arr.length-1].y-S.settings.goalW;return Math.abs(r)<0.05?'atteint':sgn(-r)+' kg'})(),'restant']:null;
    stats='<div class="stats"><div class="stat"><span>Moyenne 7 j</span><b>'+nf(avg7)+'</b><span>kg</span></div>'+
      '<div class="stat"><span>Tendance</span><b>'+(sl==null?'—':sgn(sl*7,1))+'</b><span>kg / semaine</span></div>'+
      (third?'<div class="stat"><span>'+third[0]+'</span><b>'+third[1]+'</b><span>'+third[2]+'</span></div>':
        '<div class="stat"><span>Entrées</span><b>'+arr.length+'</b><span>pesées</span></div>')+'</div>';
  }
  const hist=arr.slice().reverse(),shown=wAll?hist:hist.slice(0,14);
  const rows=shown.map((p,i)=>{
    const prev=hist[hist.indexOf(p)+1],dl=prev?p.y-prev.y:null;
    return '<button class="li" data-act="w-edit" data-d="'+p.d+'"><div class="grow"><div class="t">'+esc(fmtDay(p.d))+'</div></div>'+
      (dl!=null?'<span class="small muted num">'+(Math.abs(dl)<0.05?'=':sgn(dl))+'</span>':'')+
      '<b class="num" style="font-size:19px;min-width:64px;text-align:right">'+nf(p.y)+' kg</b></button>';
  }).join('');
  return `${ringCard(arr)}${actCard()}
  <div class="card">
    <div class="row sb" style="margin-bottom:6px">
      <h2 style="margin:0">Pesée</h2>
      <label class="chip" style="position:relative">${d===today()?'Aujourd’hui':esc(fmtShort(d))}
        <input type="date" data-ch="wdate" value="${d}" max="${today()}" aria-label="Date de la pesée" style="position:absolute;inset:0;opacity:0;width:100%;height:100%">
      </label>
    </div>
    <div class="wbig">
      <button class="step" data-act="w-step" data-s="-0.1" aria-label="Moins 0,1 kilo">−</button>
      <input id="wval" type="text" inputmode="decimal" data-in="wval" value="${nf(wVal)}" aria-label="Poids en kilos">
      <button class="step" data-act="w-step" data-s="0.1" aria-label="Plus 0,1 kilo">+</button>
    </div>
    <div class="muted small" style="text-align:center;margin:-2px 0 14px">kilogrammes</div>
    <button class="btn block" data-act="w-save">${has?'Mettre à jour':'Enregistrer'}</button>
  </div>
  ${seedCard()}
  ${arr.length?`<div class="card">
    <div class="row sb" style="margin-bottom:10px"><h2 style="margin:0">Évolution</h2>
      <div class="row" style="gap:6px">${[[14,'14 j'],[30,'30 j'],[90,'90 j'],[0,'Tout']].map(r=>`<button class="chip" style="min-height:32px;padding:0 11px;font-size:13px" data-act="w-range" data-r="${r[0]}" aria-pressed="${wRange===r[0]}">${r[1]}</button>`).join('')}</div></div>
    <div class="readout" id="wread"></div>
    <div class="chartbox" id="wchart"></div>
    <div class="small muted" style="margin-top:8px">Points : pesées. Courbe : moyenne sur 7 jours, qui lisse les écarts du quotidien.</div>
  </div>${stats?'<div class="card">'+stats+'</div>':''}
  <div class="card"><h2>Historique</h2><div class="list">${rows}</div>
    ${hist.length>14?`<button class="btn ghost block" style="margin-top:10px" data-act="w-all">${wAll?'Réduire':'Tout afficher ('+hist.length+')'}</button>`:''}</div>`
  :'<div class="card empty">Entre ton premier poids ci-dessus.<br>Le graphique et la tendance apparaîtront dès la 2e pesée.</div>'}`;
};
VIEWS.weight_after=()=>{
  const el=$('#wchart');if(!el)return;
  const arr=sortedW();if(!arr.length)return;
  const lastX=arr[arr.length-1].x,avg=movAvg(arr);
  const from=wRange?lastX-wRange:-1e9;
  const pts=arr.filter(p=>p.x>=from),ln=avg.filter(p=>p.x>=from);
  const read=$('#wread');
  const show=(p,r)=>{read.innerHTML='<b>'+nf(p.y)+' kg</b> <span class="muted small">'+esc(fmtDay(xToDate(p.x)))+(r?' · moyenne '+nf(r.y):'')+'</span>'};
  show(pts[pts.length-1],ln[ln.length-1]);
  chart(el,{pts,line:ln,goal:S.settings.goalW,label:'Courbe de poids',minSpan:2,onPick:show});
};
I.wval=t=>{wVal=num(t.value)||0};
I.wdate=t=>{if(!t.value)return;wDate=t.value;wVal=null;render()};
A['w-step']=b=>{
  const inp=$('#wval');const v=Math.round((num(inp.value)+num(b.dataset.s))*10)/10;
  wVal=Math.max(0,v);inp.value=nf(wVal);
};
A['w-save']=()=>{
  const inp=$('#wval');const v=num(inp.value);
  if(v<20||v>400){toast('Entre un poids valide (en kg)');return}
  const d=wDate||today();S.weights[d]=Math.round(v*10)/10;wVal=S.weights[d];
  persist('weights');toast('Poids enregistré');render();
};
A['w-range']=b=>{wRange=Number(b.dataset.r);render()};
A['w-all']=()=>{wAll=!wAll;render()};
A['w-edit']=b=>{
  const d=b.dataset.d;
  openSheet(`<h3>${esc(fmtLong(d))}</h3><div class="field"><label for="ew">Poids (kg)</label><input class="inp" id="ew" inputmode="decimal" value="${nf(S.weights[d])}"></div>
  <div class="grid2"><button class="btn danger" data-act="w-del" data-d="${d}">Supprimer</button><button class="btn" data-act="w-upd" data-d="${d}">Enregistrer</button></div>`);
};
A['w-upd']=b=>{const v=num($('#ew').value);if(v<20||v>400){toast('Poids invalide');return}S.weights[b.dataset.d]=Math.round(v*10)/10;persist('weights');closeSheet();render()};
A['w-del']=b=>{delete S.weights[b.dataset.d];persist('weights');wVal=null;closeSheet();render()};

/* ===== FOOD ===== */
const SLOTS=[['bk','Petit-déjeuner'],['lu','Déjeuner'],['di','Dîner'],['sn','Collations']];
/* Icônes des repas : une seule table à remplacer plus tard (SVG 24x24, trait currentColor). */
const SLOT_ICONS={
  bk:'<path d="M5 9h11v5a4 4 0 0 1-4 4H9a4 4 0 0 1-4-4V9z"/><path d="M16 10h1.5a2.5 2.5 0 0 1 0 5H16"/><path d="M8 3v3M12 3v3"/>',
  lu:'<circle cx="12" cy="12" r="4"/><path d="M12 3v2M12 19v2M3 12h2M19 12h2M5.6 5.6l1.4 1.4M17 17l1.4 1.4M5.6 18.4L7 17M17 7l1.4-1.4"/>',
  di:'<path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/>',
  sn:'<circle cx="12" cy="12" r="8"/><circle cx="9" cy="10" r=".9" fill="currentColor"/><circle cx="14.5" cy="9" r=".9" fill="currentColor"/><circle cx="13" cy="14.5" r=".9" fill="currentColor"/>'
};
const slotIcon=k=>'<span class="sloticon" aria-hidden="true"><svg viewBox="0 0 24 24">'+(SLOT_ICONS[k]||'')+'</svg></span>';
let fDate=today(),addTab=null,aiItems=[],aiBusy=false,hasAI=false,sampleFn=null,pickMap={},favQuery='';
const r1=v=>Math.round(num(v)*10)/10;
const dayEntries=d=>S.meals[d]||[];
function goals(){
  const s=S.settings,a=sortedW(),w=a.length?a[a.length-1].y:null;
  if(s.auto!==false&&w){
    const p=Math.round(w*(s.pkg||2)),f=Math.round(w*(s.fkg||1)),rest=s.kcal-4*p-9*f;
    return{kcal:s.kcal,p,f,c:Math.max(0,Math.round(rest/4)),auto:true,w,low:rest<0};
  }
  return{kcal:s.kcal,p:s.p,c:s.c,f:s.f,auto:false,w};
}
function totals(list){return list.reduce((t,e)=>({kcal:t.kcal+e.kcal,p:t.p+e.p,c:t.c+e.c,f:t.f+e.f}),{kcal:0,p:0,c:0,f:0})}
function dateBar(){
  const isToday=fDate===today();
  return `
  <div class="datebar">
    <button class="iconbtn" data-act="f-day" data-n="-1" aria-label="Jour précédent">${ICON.chevL}</button>
    <div class="d">${isToday?'Aujourd’hui':esc(fmtLong(fDate))}${isToday?'<div class="small muted" style="font-weight:500">'+esc(fmtLong(fDate))+'</div>':''}</div>
    <button class="iconbtn" data-act="f-day" data-n="1" aria-label="Jour suivant" ${isToday?'disabled style="opacity:.35"':''}>${ICON.chev}</button>
  </div>
  `;
}
let foodSub='journal';
const FOOD_SUBS=[['journal','Journal'],['recipes','Recettes'],['done','Déjà faites']];
const foodSeg=()=>'<div class="seg" role="tablist">'+FOOD_SUBS.map(([k,n])=>`<button role="tab" data-act="food-sub" data-s="${k}" aria-selected="${foodSub===k}">${n}</button>`).join('')+'</div>';
A['food-sub']=b=>{foodSub=b.dataset.s;render();window.scrollTo(0,0)};
VIEWS.food=()=>{
  if(foodSub!=='journal')return foodSeg()+recipesView();
  const list=dayEntries(fDate),t=totals(list),g=goals();
  const rem=g.kcal-t.kcal,over=rem<0,C=2*Math.PI*56,prog=clamp(t.kcal/g.kcal,0,1);
  const mac=(l,v,goal)=>`<div class="macro"><div class="row sb small"><b>${l}</b><span class="num">${nf(v,0)} / ${nf(goal,0)} g</span></div><div class="bar"><i style="width:${clamp(v/goal*100,0,100)}%"></i></div></div>`;
  const slots=SLOTS.map(([k,name])=>{
    const es=list.filter(e=>e.slot===k),st=totals(es);
    return `<div class="card slot"><div class="row sb" style="margin-bottom:4px"><h4 class="row" style="gap:10px">${slotIcon(k)}${name}</h4><span class="num muted">${nf(st.kcal,0)} kcal</span></div>
    ${es.map(e=>`<button class="entry" data-act="f-edit" data-id="${e.id}"><div class="grow"><div class="t" style="font-weight:600;overflow-wrap:anywhere">${esc(e.name)}</div><div class="small muted">P ${nf(e.p,0)} · G ${nf(e.c,0)} · L ${nf(e.f,0)}</div></div><b class="num">${nf(e.kcal,0)}</b></button>`).join('')}
    <button class="addslot" data-act="f-add" data-slot="${k}">${ICON.plus} Ajouter</button></div>`;
  }).join('');
  return foodSeg()+`
  ${dateBar()}
  <div class="card"><div class="row" style="gap:18px">
    <div class="ring"><svg viewBox="0 0 132 132"><circle cx="66" cy="66" r="56" fill="none" stroke="var(--surface2)" stroke-width="12"/><circle cx="66" cy="66" r="56" fill="none" stroke="${over?'var(--bad)':'var(--accent)'}" stroke-width="12" stroke-linecap="round" stroke-dasharray="${(C*prog).toFixed(1)} ${C.toFixed(1)}"/></svg>
      <div class="c"><b>${nf(t.kcal,0)}</b><span class="small muted">sur ${nf(g.kcal,0)} kcal</span></div></div>
    <div style="flex:1;min-width:0">${mac('Protéines',t.p,g.p)}${mac('Glucides',t.c,g.c)}${mac('Lipides',t.f,g.f)}
      <div class="small" style="margin-top:2px"><b class="num" style="color:${over?'var(--bad)':'var(--ink)'}">${nf(Math.abs(rem),0)} kcal</b> <span class="muted">${over?'au-dessus de l’objectif':'restantes'}</span></div></div>
  </div>${g.auto?`<div class="small muted" style="margin-top:12px">Objectifs calculés pour ${nf(g.w)} kg : ${nf(S.settings.pkg||2)} g de protéines et ${nf(S.settings.fkg||1)} g de lipides par kilo, glucides pour compléter les calories.${g.low?' Les calories sont trop basses pour ces réglages.':''}</div>`:''}</div>${slots}`;
};
A['f-day']=b=>{const n=Number(b.dataset.n);const nd=addDays(fDate,n);if(nd>today())return;fDate=nd;render()};
function addEntry(slot,e,date){
  const d=date||fDate;(S.meals[d]=S.meals[d]||[]).push({id:uid(),slot,name:e.name,kcal:r1(e.kcal),p:r1(e.p),c:r1(e.c),f:r1(e.f)});
  persist('meals',d);
}
function recents(){
  const seen=new Set(S.foods.map(f=>f.name.toLowerCase())),out=[];
  const days=Object.keys(S.meals).sort().reverse();
  for(const d of days){for(const e of S.meals[d].slice().reverse()){const k=e.name.toLowerCase();if(seen.has(k))continue;seen.add(k);out.push(e);if(out.length>=30)return out}}
  return out;
}
function mineList(slot){
  pickMap={};
  const q=favQuery.toLowerCase(),match=e=>!q||e.name.toLowerCase().includes(q);
  const mk=(e,fav)=>{const id=uid();pickMap[id]=e;return `<div class="row" style="border-top:1px solid var(--line)"><button class="li" style="border:0" data-act="f-pick" data-id="${id}" data-slot="${slot}"><div class="grow"><div class="t">${esc(e.name)}</div><div class="small muted">P ${nf(e.p,0)} · G ${nf(e.c,0)} · L ${nf(e.f,0)}</div></div><b class="num">${nf(e.kcal,0)}</b></button>${fav?`<button class="iconbtn" style="box-shadow:none;background:none" data-act="fav-del" data-fid="${e.id}" data-slot="${slot}" aria-label="Retirer des favoris"><span style="font-size:22px;color:var(--muted)">×</span></button>`:''}</div>`};
  const fav=S.foods.filter(match),rec=recents().filter(match);
  return (fav.length?'<div class="sec">Favoris</div>'+fav.map(e=>mk(e,true)).join(''):'')+(rec.length?'<div class="sec" style="margin-top:14px">Récents</div>'+rec.map(e=>mk(e,false)).join(''):'')+
    (!fav.length&&!rec.length?'<div class="empty">Rien pour l’instant. Ce que tu ajoutes apparaît ici pour le retrouver en un geste.</div>':'');
}
function addSheet(slot){
  if(!addTab)addTab='scan';
  const tabs=[...(hasAI?[['ai','Décrire']]:[]),['scan','Scanner'],['mine','Favoris'],['manual','Manuel']];
  const slotName=SLOTS.find(s=>s[0]===slot)[1];
  let body='';
  if(addTab==='ai'){
    body=`<div class="field"><label for="aitext">Qu’as-tu mangé ?</label><textarea class="inp" id="aitext" placeholder="Ex : 2 œufs brouillés, 2 tranches de pain complet, un café sans sucre"></textarea></div>
    <button class="btn block" id="aigo" data-act="ai-go" data-slot="${slot}">Estimer les calories</button>
    <div class="small muted" style="margin-top:8px">Estimation par Claude : à ajuster selon les portions réelles.</div><div id="airesult" style="margin-top:14px"></div>`;
  }else if(addTab==='scan'){
    body='<div id="scanbody">'+scanTabHtml(slot)+'</div>';
  }else if(addTab==='mine'){
    body=`<div class="field"><input class="inp" id="favq" data-in="favq" data-slot="${slot}" placeholder="Rechercher" value="${esc(favQuery)}" aria-label="Rechercher un aliment"></div>
    <div id="favlist">${mineList(slot)}</div>`;
  }else{
    body=`<div class="field"><label for="mn">Aliment</label><input class="inp" id="mn" placeholder="Ex : Yaourt grec 0 %"></div>
    <div class="grid2"><div class="field"><label for="mk">Calories (kcal)</label><input class="inp" id="mk" inputmode="decimal"></div><div class="field"><label for="mp">Protéines (g)</label><input class="inp" id="mp" inputmode="decimal"></div></div>
    <div class="grid2"><div class="field"><label for="mc">Glucides (g)</label><input class="inp" id="mc" inputmode="decimal"></div><div class="field"><label for="mf">Lipides (g)</label><input class="inp" id="mf" inputmode="decimal"></div></div>
    <label class="row" style="margin:4px 0 14px;min-height:44px"><input type="checkbox" id="mfav" style="width:22px;height:22px"> Garder dans mes favoris</label>
    <button class="btn block" data-act="f-manual" data-slot="${slot}">Ajouter</button>`;
  }
  openSheet(`<h3 class="row" style="gap:10px">${slotIcon(slot)}${esc(slotName)}</h3><div class="seg" role="tablist">${tabs.map(t=>`<button role="tab" data-act="add-tab" data-t="${t[0]}" data-slot="${slot}" aria-selected="${addTab===t[0]}">${t[1]}</button>`).join('')}</div>${body}`);
}
A['f-add']=b=>{addTab=null;favQuery='';aiItems=[];bcReset();addSheet(b.dataset.slot)};
A['add-tab']=b=>{addTab=b.dataset.t;addSheet(b.dataset.slot)};
I.favq=t=>{favQuery=t.value;const l=$('#favlist');if(l)l.innerHTML=mineList(t.dataset.slot)};
A['f-pick']=b=>{const e=pickMap[b.dataset.id];if(!e)return;addEntry(b.dataset.slot,e);closeSheet();toast('Ajouté : '+e.name);render()};
A['fav-del']=b=>{S.foods=S.foods.filter(f=>f.id!==b.dataset.fid);persist('foods');const l=$('#favlist');if(l)l.innerHTML=mineList(b.dataset.slot)};
A['f-manual']=b=>{
  const name=$('#mn').value.trim(),kcal=num($('#mk').value);
  if(!name||!kcal){toast('Indique un nom et les calories');return}
  const e={name,kcal,p:num($('#mp').value),c:num($('#mc').value),f:num($('#mf').value)};
  addEntry(b.dataset.slot,e);
  if($('#mfav').checked){S.foods.unshift({id:uid(),name:e.name,kcal:r1(e.kcal),p:r1(e.p),c:r1(e.c),f:r1(e.f)});persist('foods')}
  closeSheet();toast('Ajouté');render();
};
A['ai-go']=async b=>{
  const txt=$('#aitext').value.trim();if(!txt||aiBusy||!sampleFn)return;
  aiBusy=true;const out=$('#airesult');b.disabled=true;
  out.innerHTML='<div class="row muted"><span class="spin"></span> Estimation en cours…</div>';
  try{
    const prompt='Tu es nutritionniste. Estime les valeurs nutritionnelles de ce repas décrit en français : « '+txt+' ». Sépare en aliments distincts. Si la quantité manque, prends une portion courante. Réponds uniquement par un tableau JSON d’objets {"name": string avec la quantité, par exemple "2 œufs brouillés", "kcal": number, "p": number (protéines en g), "c": number (glucides en g), "f": number (lipides en g)}. Les valeurs sont pour la quantité indiquée, pas pour 100 g. Aucun texte autour.';
    const res=await sampleFn.json(prompt,{modelTier:'quick'});
    aiItems=(Array.isArray(res)?res:[]).filter(x=>x&&x.name).map(x=>({name:String(x.name),kcal:num(x.kcal),p:num(x.p),c:num(x.c),f:num(x.f),on:true}));
    if(!aiItems.length)throw{code:'empty'};
    drawAi(b.dataset.slot);
  }catch(e){
    out.innerHTML='<div class="card" style="box-shadow:none;background:var(--surface2)">'+(e&&e.code==='not_granted'?'L’accès à Claude a été refusé. Utilise l’onglet Manuel.':e&&e.code==='rate_limited'?'Trop de demandes. Réessaie dans un instant.':'Je n’ai pas réussi à estimer ce repas. Reformule ou utilise l’onglet Manuel.')+'</div>';
  }
  aiBusy=false;b.disabled=false;
};
function drawAi(slot){
  const out=$('#airesult');if(!out)return;
  const on=aiItems.filter(i=>i.on),t=totals(on);
  out.innerHTML=`<div class="list">${aiItems.map((i,n)=>`<button class="li" data-act="ai-tog" data-n="${n}" data-slot="${slot}" aria-pressed="${i.on}"><span class="ck" style="width:26px;height:26px;border-radius:8px;display:grid;place-items:center;background:${i.on?'var(--accent)':'var(--surface2)'};color:var(--on-accent);flex:none">${i.on?'✓':''}</span><div class="grow"><div class="t">${esc(i.name)}</div><div class="small muted">P ${nf(i.p,0)} · G ${nf(i.c,0)} · L ${nf(i.f,0)}</div></div><b class="num">${nf(i.kcal,0)}</b></button>`).join('')}</div>
  <button class="btn block" style="margin-top:12px" data-act="ai-add" data-slot="${slot}" ${on.length?'':'disabled'}>Ajouter ${on.length} aliment${on.length>1?'s':''} · ${nf(t.kcal,0)} kcal</button>`;
}
A['ai-tog']=b=>{const i=aiItems[Number(b.dataset.n)];if(i){i.on=!i.on;drawAi(b.dataset.slot)}};
A['ai-add']=b=>{aiItems.filter(i=>i.on).forEach(i=>addEntry(b.dataset.slot,i));closeSheet();toast('Repas ajouté');render()};
A['f-edit']=b=>{
  const e=dayEntries(fDate).find(x=>x.id===b.dataset.id);if(!e)return;
  openSheet(`<h3>Modifier</h3><div class="field"><label for="en">Aliment</label><input class="inp" id="en" value="${esc(e.name)}"></div>
  <div class="grid2"><div class="field"><label for="ek">Calories</label><input class="inp" id="ek" inputmode="decimal" value="${nf(e.kcal)}"></div><div class="field"><label for="ep">Protéines (g)</label><input class="inp" id="ep" inputmode="decimal" value="${nf(e.p)}"></div></div>
  <div class="grid2"><div class="field"><label for="ec">Glucides (g)</label><input class="inp" id="ec" inputmode="decimal" value="${nf(e.c)}"></div><div class="field"><label for="ef">Lipides (g)</label><input class="inp" id="ef" inputmode="decimal" value="${nf(e.f)}"></div></div>
  <div class="row" style="margin-bottom:12px"><button class="btn ghost" style="flex:1" data-act="f-scale" data-k="0.5">× ½</button><button class="btn ghost" style="flex:1" data-act="f-scale" data-k="1.5">× 1,5</button><button class="btn ghost" style="flex:1" data-act="f-scale" data-k="2">× 2</button></div>
  <div class="grid2"><button class="btn danger" data-act="f-del" data-id="${e.id}">Supprimer</button><button class="btn" data-act="f-save" data-id="${e.id}">Enregistrer</button></div>
  <button class="btn soft block" style="margin-top:10px" data-act="f-fav" data-id="${e.id}">Ajouter aux favoris</button>`);
};
A['f-scale']=b=>{const k=Number(b.dataset.k);['ek','ep','ec','ef'].forEach(id=>{const i=$('#'+id);i.value=nf(num(i.value)*k)})};
A['f-save']=b=>{
  const e=dayEntries(fDate).find(x=>x.id===b.dataset.id);if(!e)return;
  e.name=$('#en').value.trim()||e.name;e.kcal=r1($('#ek').value);e.p=r1($('#ep').value);e.c=r1($('#ec').value);e.f=r1($('#ef').value);
  persist('meals',fDate);closeSheet();render();
};
A['f-del']=b=>{S.meals[fDate]=dayEntries(fDate).filter(x=>x.id!==b.dataset.id);persist('meals',fDate);closeSheet();render()};
A['f-fav']=b=>{
  const e=dayEntries(fDate).find(x=>x.id===b.dataset.id);if(!e)return;
  if(!S.foods.some(f=>f.name.toLowerCase()===e.name.toLowerCase())){S.foods.unshift({id:uid(),name:e.name,kcal:e.kcal,p:e.p,c:e.c,f:e.f});persist('foods')}
  toast('Ajouté aux favoris');
};
