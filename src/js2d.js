
/* ===== RECETTES : sous-onglets « Recettes » et « Déjà faites » du Repas =====
   Les recettes viennent de RECIPES (js2c.js, généré) + S.recipes.mine (les siennes).
   S.recipes = { done:{ id:{n,last} }, notes:{ id:texte }, mine:[ recette ] }.
   Classées selon ce qu'il reste de la journée affichée (fDate) : calories,
   protéines, glucides, lipides. */
const RC=()=>{const r=S.recipes||(S.recipes={});r.done=r.done||{};r.notes=r.notes||{};r.mine=r.mine||[];return r};
const allRecipes=()=>RECIPES.concat(RC().mine);
const recipeById=id=>allRecipes().find(r=>r.id===id);
const SLOT_SHORT={bk:'Petit-déj.',lu:'Déjeuner',di:'Dîner',sn:'Collation'};
const SLOT_TO={bk:'au petit-déjeuner',lu:'au déjeuner',di:'au dîner',sn:'aux collations'};
const SLOT_W={bk:.25,lu:.35,di:.3,sn:.1};   /* poids d'un repas dans la journée */
let rcSlot='all',rcFast=false,rcPrep=false,rcVeg=false,rcOpenId=null,rcK=1,rcAdd='lu',rcEditId=null,rcFormSlot='lu';

/* ---- ce qu'il reste, et ce qui convient le mieux ---- */
function rcRem(){
  const g=goals(),t=totals(dayEntries(fDate));
  return{k:g.kcal-t.kcal,p:g.p-t.p,c:g.c-t.c,f:g.f-t.f};
}
/* Part du reste de la journée qu'un repas de ce type devrait couvrir : on divise
   le reste entre les repas pas encore saisis (plus celui-ci). */
function rcTarget(rem,slot){
  const filled=new Set(dayEntries(fDate).map(e=>e.slot));
  let sum=SLOT_W[slot];
  for(const s in SLOT_W)if(s!==slot&&!filled.has(s))sum+=SLOT_W[s];
  const sh=SLOT_W[slot]/sum,pos=v=>Math.max(0,v)*sh;
  return{k:pos(rem.k),p:pos(rem.p),c:pos(rem.c),f:pos(rem.f)};
}
/* Prochain repas à viser quand aucun filtre n'est choisi : celui de l'heure s'il
   n'est pas encore saisi, sinon le suivant ; un jour passé commence au petit-déjeuner. */
function rcNextSlot(){
  const filled=new Set(dayEntries(fDate).map(e=>e.slot)),h=new Date().getHours(),order=['bk','lu','di'];
  const i=order.indexOf(fDate!==today()?'bk':h<11?'bk':h<16?'lu':'di');
  for(let n=0;n<3;n++){const s=order[(i+n)%3];if(!filled.has(s))return s}
  return 'sn';
}
const rcSlotOf=r=>rcSlot==='all'?rcNextSlot():r.s.includes(rcSlot)?rcSlot:r.s[0];
/* Plus c'est bas, mieux c'est. Les protéines en dessous de la cible coûtent cher,
   au-dessus presque rien : on veut des repas protéinés. */
function rcScore(r,rem){
  const t=rcTarget(rem,rcSlotOf(r)),rel=(a,b,m)=>Math.abs(a-b)/Math.max(b,m);
  const dp=r.p>=t.p?.4*(r.p-t.p)/Math.max(t.p,15):1.5*(t.p-r.p)/Math.max(t.p,15);
  const hors=rcSlot==='all'&&!r.s.includes(rcSlotOf(r))?.35:0;   /* pas prévue pour ce repas */
  return dp+1.2*rel(r.k,t.k,150)+.6*rel(r.c,t.c,20)+.6*rel(r.f,t.f,8)+hors;
}
/* Ce qui dépasse du reste de la journée (avec un peu de tolérance). */
function rcOver(r,rem){
  const o=[],x=(v,u)=>'+'+nf(Math.round(v),0)+u;
  if(r.k>rem.k+30)o.push({w:(r.k-rem.k)/100,t:x(r.k-rem.k,' kcal en trop')});
  if(r.f>rem.f+4)o.push({w:(r.f-rem.f)/8,t:x(r.f-rem.f,' g de lipides en trop')});
  if(r.c>rem.c+8)o.push({w:(r.c-rem.c)/20,t:x(r.c-rem.c,' g de glucides en trop')});
  return o;   /* dans l'ordre d'importance pour l'affichage : calories, lipides, glucides */
}

/* ---- liste ---- */
function rcRow(r,rem,withDone){
  const over=rcOver(r,rem),d=RC().done[r.id],note=RC().notes[r.id];
  const pills=(over.length?`<span class="pill warn">${over[0].t}</span>`:'<span class="pill good">Tient dans ton reste</span>')
    +(d&&d.n?`<span class="pill neutral">✓ Faite ${d.n}×</span>`:'')
    +(!over.length&&rem.p>5&&!(d&&d.n)?`<span class="pill neutral">${Math.min(100,Math.round(r.p/rem.p*100))} % des protéines restantes</span>`:'');
  return `<button class="li" data-act="rc-open" data-id="${esc(r.id)}"><div class="grow">
    <div class="t">${esc(r.n)}</div>
    <div class="small muted">${r.t} min · P ${nf(r.p,0)} · G ${nf(r.c,0)} · L ${nf(r.f,0)}${r.mine?' · Ma recette':''}</div>
    ${withDone&&d?`<div class="small muted">Dernière fois : ${esc(fmtShort(d.last))}${note?' · « '+esc(note.length>60?note.slice(0,58)+'…':note)+' »':''}</div>`:''}
    <div class="row" style="gap:6px;flex-wrap:wrap;margin-top:5px">${pills}</div></div>
    <div style="text-align:right;flex:none"><b class="num" style="font-size:19px">${nf(r.k,0)}</b><div class="small muted">kcal</div></div></button>`;
}
function rcBanner(rem){
  const stat=(l,v)=>`<div class="stat"><b class="num"${v<0?' style="color:var(--bad)"':''}>${v<0?'−':''}${nf(Math.abs(v),0)}</b><span>${l}</span></div>`;
  return `<div class="card"><h2>Il te reste ${fDate===today()?'aujourd’hui':'le '+esc(fmtShort(fDate))}</h2>
    <div class="stats" style="grid-template-columns:repeat(4,1fr)">${stat('kcal',rem.k)}${stat('prot. (g)',rem.p)}${stat('gluc. (g)',rem.c)}${stat('lip. (g)',rem.f)}</div>
    <div class="small muted" style="margin-top:12px">${rem.k<=0?'Tu as atteint ton objectif de calories : voici les recettes les plus légères.':'Classées pour '+(rcSlot==='all'?'ton prochain repas ('+SLOT_SHORT[rcNextSlot()].toLowerCase()+')':'le choix « '+SLOT_SHORT[rcSlot].toLowerCase()+' »')+' : les mieux adaptées à ce reste d’abord.'}</div></div>`;
}
function recipesView(){
  if(foodSub==='done')return doneView();
  const rem=rcRem();
  let list=allRecipes().filter(r=>(rcSlot==='all'||r.s.includes(rcSlot))&&(!rcFast||r.t<=15)&&(!rcPrep||r.prep)&&(!rcVeg||r.veg))
    .map(r=>({r,o:rcOver(r,rem),sc:rcScore(r,rem)}));
  const exc=x=>x.o.reduce((s,y)=>s+y.w,0);
  list.sort((a,b)=>{const ao=a.o.length>0,bo=b.o.length>0;if(ao!==bo)return ao?1:-1;return ao?(exc(a)-exc(b)||a.sc-b.sc):a.sc-b.sc});
  const chip=(k,label,on)=>`<button class="chip" data-act="rc-flag" data-k="${k}" aria-pressed="${on}">${label}</button>`;
  const slots=[['all','Tous'],['bk','Petit-déj.'],['lu','Déjeuner'],['di','Dîner'],['sn','Collation']]
    .map(([k,n])=>`<button role="tab" data-act="rc-slot" data-s="${k}" aria-selected="${rcSlot===k}">${n}</button>`).join('');
  const flags=chip('fast','Rapide ≤ 15 min',rcFast)+chip('prep','À l’avance',rcPrep)+chip('veg','Végétarien',rcVeg);
  return dateBar()+rcBanner(rem)+
    `<div class="seg rcslotseg" role="tablist" aria-label="Repas" style="margin-bottom:10px">${slots}</div>
     <div class="chips">${flags}</div>`+
    (list.length?`<div class="card"><h2>${list.length} recette${list.length>1?'s':''}</h2><div class="list">${list.map(x=>rcRow(x.r,rem)).join('')}</div></div>`
      :'<div class="card empty">Aucune recette avec ces filtres.</div>')+
    `<button class="btn ghost block" data-act="rc-new" style="margin-bottom:14px">${ICON.plus} Ajouter ma recette</button>
     <div class="small muted" style="margin-bottom:14px">Valeurs par portion, calculées à partir de valeurs moyennes : elles sont indicatives.</div>`;
}
function doneView(){
  const rem=rcRem(),d=RC().done;
  const list=allRecipes().filter(r=>d[r.id]&&d[r.id].n>0).sort((a,b)=>(d[b.id].last||'').localeCompare(d[a.id].last||''));
  return dateBar()+(list.length
    ?`<div class="card"><h2>${list.length} recette${list.length>1?'s':''} déjà faite${list.length>1?'s':''}</h2><div class="list">${list.map(r=>rcRow(r,rem,true)).join('')}</div></div>`
    :'<div class="card empty">Rien pour l’instant.<br>Ouvre une recette et appuie sur « Je l’ai préparée » : elle apparaît ici, avec la date et ta note.</div>');
}
A['rc-slot']=b=>{rcSlot=b.dataset.s;render()};
A['rc-flag']=b=>{const k=b.dataset.k;if(k==='fast')rcFast=!rcFast;else if(k==='prep')rcPrep=!rcPrep;else rcVeg=!rcVeg;render()};

/* ---- fiche d'une recette ---- */
const frac=v=>{
  v=Math.round(v*4)/4;const w=Math.floor(v),f=v-w;
  const s=f===.25?'¼':f===.5?'½':f===.75?'¾':'';
  return (w||!s?String(w):'')+(w&&s?' ':'')+s;
};
const rcPl=(s,n)=>{const p=s.split('|');return n>1?(p[1]||p[0]):p[0]};
const rcDe=n=>(/^(huile|[aeiouéèêâîôœ])/i.test(n)?'d’':'de ')+n;
function rcIng(r,k){
  if(r.ingTxt)return r.ingTxt.map(l=>`<li>${esc(l)}</li>`).join('')||'<li class="muted">Pas d’ingrédients notés.</li>';
  return r.ing.map(([q,u,n])=>{
    const v=q*k;
    if(u==='g'||u==='ml')return `<li>${nf(Math.round(v),0)} ${u} ${esc(rcDe(n))}</li>`;
    if(u==='')return `<li>${frac(v)} ${esc(rcPl(n,v))}</li>`;
    return `<li>${frac(v)} ${esc(rcPl(u,v))} ${esc(rcDe(n.split('|')[0]))}</li>`;
  }).join('');
}
function rcSheet(){
  const r=recipeById(rcOpenId);if(!r)return;
  const note=RC().notes[r.id]||'';
  openSheet(`<div class="rc"><h3>${esc(r.n)}</h3>
  <div class="row" style="flex-wrap:wrap;gap:6px;margin:-6px 0 14px"><span class="pill neutral">⏱ ${r.t} min</span>${r.veg?'<span class="pill good">Végétarien</span>':''}${r.prep?'<span class="pill neutral">À préparer à l’avance</span>':''}${r.mine?'<span class="pill neutral">Ma recette</span>':''}</div>
  <div class="sec">Portions</div>
  <div class="seg" id="rcseg" role="tablist" aria-label="Nombre de portions">${[[.5,'½'],[1,'1'],[1.5,'1,5'],[2,'2']].map(([k,n])=>`<button role="tab" data-act="rc-k" data-k="${k}" aria-selected="${rcK===k}">${n}</button>`).join('')}</div>
  <div class="stats" id="rcstats" style="grid-template-columns:repeat(4,1fr);margin-bottom:18px"></div>
  <div class="sec">Ingrédients</div>
  <ul class="rcl" id="rcing"></ul>
  <div class="sec">Préparation</div>
  <ol class="rcl">${r.st.length?r.st.map(s=>`<li>${esc(s)}</li>`).join(''):'<li class="muted">Pas d’étapes notées.</li>'}</ol>
  ${r.tip?`<div class="card" style="box-shadow:none;background:var(--surface2)"><b>Astuce</b><div style="margin-top:4px">${esc(r.tip)}</div></div>`:''}
  <div class="sec" style="margin-top:6px">Ajouter au journal</div>
  <div class="seg rcslotseg" id="rcslots" role="tablist" aria-label="Repas du journal"></div>
  <button class="btn block" id="rcaddbtn" data-act="rc-log"></button>
  <div id="rcmade" style="margin-top:12px"></div>
  <div class="field" style="margin-top:16px"><label for="rcnote">Ma note</label><textarea class="inp" id="rcnote" data-ch="rcnote" placeholder="Ex : un peu moins de sel, ajouter du piment…">${esc(note)}</textarea></div>
  ${r.mine?'<div class="grid2"><button class="btn ghost" data-act="rc-edit">Modifier</button><button class="btn danger" data-act="rc-del">Supprimer</button></div>':''}
  <div class="small muted" style="margin-top:14px">Valeurs indicatives. Poids crus pour les viandes, poissons, féculents et lentilles ; conserves égouttées.</div></div>`);
  rcDraw();
}
/* Met à jour les morceaux qui dépendent des portions, sans refaire toute la fiche
   (sinon elle remonterait en haut à chaque appui). */
function rcDraw(){
  const r=recipeById(rcOpenId);if(!r||!$('#rcstats'))return;
  const k=rcK,d=RC().done[r.id];
  $('#rcstats').innerHTML=[['kcal',r.k],['prot. (g)',r.p],['gluc. (g)',r.c],['lip. (g)',r.f]].map(([l,v])=>`<div class="stat"><b class="num">${nf(v*k,0)}</b><span>${l}</span></div>`).join('');
  $('#rcing').innerHTML=rcIng(r,k);
  document.querySelectorAll('#rcseg button').forEach(b=>b.setAttribute('aria-selected',String(Number(b.dataset.k)===k)));
  $('#rcslots').innerHTML=SLOTS.map(([s])=>`<button role="tab" data-act="rc-addslot" data-s="${s}" aria-selected="${rcAdd===s}">${SLOT_SHORT[s]}</button>`).join('');
  $('#rcaddbtn').textContent='Ajouter à '+(fDate===today()?'aujourd’hui':fmtShort(fDate))+' · '+nf(r.k*k,0)+' kcal';
  $('#rcmade').innerHTML=d&&d.n
    ?`<div class="card" style="box-shadow:none;background:var(--surface2);margin:0 0 10px"><b>✓ Préparée ${d.n} fois</b><div class="small muted">Dernière fois : ${esc(fmtLong(d.last))}</div></div>
      <div class="grid2"><button class="btn soft" data-act="rc-made">+ Refaite aujourd’hui</button><button class="btn ghost" data-act="rc-unmade">Retirer des faites</button></div>`
    :'<button class="btn soft block" data-act="rc-made">✓ Je l’ai préparée</button>';
}
function rcMark(id,date){
  const dn=RC().done,d=dn[id]||(dn[id]={n:0,last:''});
  if(d.n&&d.last===date)return false;
  d.n++;if(date>d.last)d.last=date;persist('recipes');return true;
}
A['rc-open']=b=>{
  const r=recipeById(b.dataset.id);if(!r)return;
  rcOpenId=r.id;rcK=1;rcAdd=rcSlot!=='all'&&r.s.includes(rcSlot)?rcSlot:r.s[0];rcSheet();
};
A['rc-k']=b=>{rcK=Number(b.dataset.k);rcDraw()};
A['rc-addslot']=b=>{rcAdd=b.dataset.s;rcDraw()};
A['rc-log']=()=>{
  const r=recipeById(rcOpenId);if(!r)return;const k=rcK;
  addEntry(rcAdd,{name:r.n+(k===1?'':k===.5?' (½ portion)':' ('+nf(k)+' portions)'),kcal:r.k*k,p:r.p*k,c:r.c*k,f:r.f*k});
  rcMark(r.id,fDate);closeSheet();toast('Ajouté '+SLOT_TO[rcAdd]);render();
};
A['rc-made']=()=>{
  if(!rcMark(rcOpenId,today())){toast('Déjà noté pour aujourd’hui');return}
  toast('Noté dans tes recettes faites');rcDraw();render();
};
A['rc-unmade']=()=>{delete RC().done[rcOpenId];persist('recipes');toast('Retirée des recettes faites');rcDraw();render()};
I.rcnote=t=>{
  if(!rcOpenId)return;const n=RC().notes,v=t.value.trim();
  if(v)n[rcOpenId]=v;else delete n[rcOpenId];
  persist('recipes');render();
};

/* ---- ses propres recettes ---- */
function rcForm(r){
  rcEditId=r?r.id:null;rcFormSlot=r?r.s[0]:'lu';
  const v=r||{n:'',t:'',k:'',p:'',c:'',f:'',ingTxt:[],st:[]};
  openSheet(`<div class="rc"><h3>${r?'Modifier ma recette':'Ma recette'}</h3>
  <div class="field"><label for="rfn">Nom</label><input class="inp" id="rfn" value="${esc(v.n)}" placeholder="Ex : Poulet au curry de maman"></div>
  <div class="sec">Repas</div>
  <div class="seg" id="rfseg" role="tablist">${SLOTS.map(([s])=>`<button role="tab" data-act="rc-fslot" data-s="${s}" aria-selected="${rcFormSlot===s}">${SLOT_SHORT[s]}</button>`).join('')}</div>
  <div class="grid2"><div class="field"><label for="rft">Temps (min)</label><input class="inp" id="rft" inputmode="numeric" value="${esc(v.t)}"></div><div class="field"><label for="rfk">Calories (kcal)</label><input class="inp" id="rfk" inputmode="decimal" value="${esc(v.k)}"></div></div>
  <div class="grid2"><div class="field"><label for="rfp">Protéines (g)</label><input class="inp" id="rfp" inputmode="decimal" value="${esc(v.p)}"></div><div class="field"><label for="rfc">Glucides (g)</label><input class="inp" id="rfc" inputmode="decimal" value="${esc(v.c)}"></div></div>
  <div class="field"><label for="rff">Lipides (g)</label><input class="inp" id="rff" inputmode="decimal" value="${esc(v.f)}"></div>
  <div class="field"><label for="rfi">Ingrédients (un par ligne)</label><textarea class="inp" id="rfi" placeholder="150 g de poulet&#10;70 g de riz">${esc((v.ingTxt||[]).join('\n'))}</textarea></div>
  <div class="field"><label for="rfs">Préparation (une étape par ligne)</label><textarea class="inp" id="rfs">${esc((v.st||[]).join('\n'))}</textarea></div>
  <div class="small muted" style="margin-bottom:12px">Les valeurs sont pour une portion.</div>
  <button class="btn block" data-act="rc-save">Enregistrer</button></div>`);
}
A['rc-new']=()=>rcForm(null);
A['rc-edit']=()=>{const r=recipeById(rcOpenId);if(r&&r.mine)rcForm(r)};
A['rc-fslot']=b=>{rcFormSlot=b.dataset.s;document.querySelectorAll('#rfseg button').forEach(x=>x.setAttribute('aria-selected',String(x.dataset.s===rcFormSlot)))};
A['rc-save']=()=>{
  const n=$('#rfn').value.trim(),k=num($('#rfk').value);
  if(!n||!k){toast('Indique un nom et les calories');return}
  const lines=id=>$('#'+id).value.split('\n').map(x=>x.trim()).filter(Boolean),m=RC().mine,i=m.findIndex(x=>x.id===rcEditId);
  const o=Object.assign({veg:0,prep:0,tip:''},i>=0?m[i]:{},{
    id:i>=0?rcEditId:'u_'+uid(),n,s:[rcFormSlot],t:Math.max(1,Math.round(num($('#rft').value))||15),
    k:Math.round(k),p:r1($('#rfp').value),c:r1($('#rfc').value),f:r1($('#rff').value),
    ingTxt:lines('rfi'),st:lines('rfs'),mine:1});
  if(i>=0)m[i]=o;else m.unshift(o);
  persist('recipes');rcOpenId=o.id;rcK=1;rcAdd=o.s[0];render();rcSheet();toast('Recette enregistrée');
};
A['rc-del']=()=>{
  const r=recipeById(rcOpenId);if(!r||!r.mine)return;
  confirmSheet('Supprimer cette recette ?','« '+r.n+' » disparaît de ta liste, avec ta note.','Supprimer',()=>{
    const s=RC();s.mine=s.mine.filter(x=>x.id!==r.id);delete s.done[r.id];delete s.notes[r.id];
    persist('recipes');rcOpenId=null;render();toast('Recette supprimée');
  });
};
