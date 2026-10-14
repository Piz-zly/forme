/* ===== REPAS : ajouts rapides, fiabilité des valeurs, semaine et courses, frigo, bilan (2026.10.14-4) =====
   Chargé après js2f.js (Chercher) et avant js3c.js. Données (toutes dans SLICES, donc exportées et synchronisées) :
   S.combos = [ {id, name, slot, items:[{name,kcal,p,c,f}]} ]          repas types
   S.fixes  = { idAliment: {k,p,c,f} }                                  valeurs corrigées pour 100 g (ou 100 ml)
   S.plan   = { days:{ 'AAAA-MM-JJ': { bk:[{r:idRecette, ok:0|1}], … } }, shop:{ done:{clé:1}, extra:[…] } }
   S.fridge = { have:[ 'nom normalisé', … ] }                          ce qu'il a chez lui */
const CB=()=>Array.isArray(S.combos)?S.combos:(S.combos=[]);
const FX=()=>S.fixes&&typeof S.fixes==='object'?S.fixes:(S.fixes={});
const PL=()=>{const p=S.plan&&typeof S.plan==='object'?S.plan:(S.plan={});p.days=p.days||{};p.shop=p.shop||{};p.shop.done=p.shop.done||{};p.shop.extra=p.shop.extra||[];return p};
const FR=()=>{const f=S.fridge&&typeof S.fridge==='object'?S.fridge:(S.fridge={});f.have=Array.isArray(f.have)?f.have:[];return f};
const slotName=k=>(SLOTS.find(s=>s[0]===k)||['',''])[1];
const kcalOf=l=>l.reduce((t,e)=>t+num(e.kcal),0);

/* ---------- 1. ajouts rapides ---------- */
/* onglet Manuel : raccourcis de calories ; le nom devient facultatif */
const QUICK_KCAL=[100,200,300,500];
A['m-plus']=b=>{const i=$('#mk');if(!i)return;i.value=nf(num(i.value)+Number(b.dataset.v),0)};
I.mn=t=>{const r=$('#mfavrow');if(r)r.style.display=t.value.trim()?'':'none'};

/* copier un repas (ou toute une journée) depuis un des 28 derniers jours */
function copyDays(slot){
  const out=[];
  for(let i=0;i<=28;i++){const d=addDays(today(),-i);if(d===fDate)continue;const es=dayEntries(d).filter(e=>!slot||e.slot===slot);if(es.length)out.push([d,es])}
  return out;
}
A['f-copy']=b=>{
  const slot=b.dataset.slot||'',ds=copyDays(slot);
  const rows=ds.map(([d,es])=>`<button class="li" data-act="f-copy-ok" data-d="${d}" data-slot="${slot}"><div class="grow"><div class="t">${esc(fmtDay(d))}</div><div class="small muted">${esc(es.slice(0,3).map(e=>e.name).join(', ')+(es.length>3?'…':''))}</div></div><b class="num">${nf(kcalOf(es),0)}</b></button>`).join('');
  openSheet(`<h3>${slot?'Copier un '+esc(slotName(slot).toLowerCase()):'Copier une journée'}</h3>
  <p class="small muted" style="margin:-6px 0 12px">Vers ${fDate===today()?'aujourd’hui':esc(fmtLong(fDate))}. ${slot?'Choisis le jour à reprendre.':'Tous les repas du jour choisi sont ajoutés, chacun à sa place.'}</p>
  ${rows?'<div class="list">'+rows+'</div>':'<div class="empty">Aucun repas noté ces 28 derniers jours.</div>'}
  <button class="btn ghost block" style="margin-top:12px" data-act="close">Annuler</button>`);
};
A['f-copy-ok']=b=>{
  const slot=b.dataset.slot||'',src=dayEntries(b.dataset.d).filter(e=>!slot||e.slot===slot);if(!src.length)return;
  const dst=S.meals[fDate]=S.meals[fDate]||[];
  src.forEach(e=>dst.push({id:uid(),slot:e.slot,name:e.name,kcal:e.kcal,p:e.p,c:e.c,f:e.f}));   /* nouveaux identifiants */
  persist('meals',fDate);closeSheet();toast(src.length+(src.length>1?' aliments copiés':' aliment copié'));render();
};

/* repas types */
A['cb-save']=b=>{
  const slot=b.dataset.slot,es=dayEntries(fDate).filter(e=>e.slot===slot);if(!es.length)return;
  openSheet(`<h3>Enregistrer comme repas type</h3><p class="small muted" style="margin:-6px 0 12px">${es.length} aliment${es.length>1?'s':''} · ${nf(kcalOf(es),0)} kcal. Tu le retrouveras dans « Favoris », à ajouter en un geste.</p>
  <div class="field"><label for="cbn">Nom</label><input class="inp" id="cbn" value="${esc(slotName(slot)+' habituel')}"></div>
  <div class="grid2"><button class="btn ghost" data-act="close">Annuler</button><button class="btn" data-act="cb-save-ok" data-slot="${slot}">Enregistrer</button></div>`);
};
A['cb-save-ok']=b=>{
  const slot=b.dataset.slot,es=dayEntries(fDate).filter(e=>e.slot===slot),name=($('#cbn').value||'').trim()||slotName(slot)+' habituel';
  if(!es.length)return;
  CB().unshift({id:uid(),name,slot,items:es.map(e=>({name:e.name,kcal:r1(e.kcal),p:r1(e.p),c:r1(e.c),f:r1(e.f)}))});
  persist('combos');closeSheet();toast('Repas type enregistré');render();
};
function combosHtml(slot,q){
  const t=q?fzWords(q):[],list=CB().filter(c=>!t.length||t.every(w=>normTxt(c.name+' '+c.items.map(i=>i.name).join(' ')).includes(w)));
  if(!list.length)return '';
  return '<div class="sec">Mes repas types</div><div class="list" style="margin-bottom:14px">'+list.map(c=>`<div class="row" style="border-top:1px solid var(--line)"><button class="li" style="border:0" data-act="cb-add" data-id="${c.id}" data-slot="${slot}"><div class="grow"><div class="t">${esc(c.name)}</div><div class="small muted">${c.items.length} aliment${c.items.length>1?'s':''} · ${esc(c.items.slice(0,3).map(i=>i.name).join(', ')+(c.items.length>3?'…':''))}</div></div><b class="num">${nf(kcalOf(c.items),0)}</b></button><button class="iconbtn" style="box-shadow:none;width:44px;height:44px" data-act="cb-del" data-id="${c.id}" data-slot="${slot}" aria-label="Supprimer le repas type ${esc(c.name)}">×</button></div>`).join('')+'</div>';
}
A['cb-add']=b=>{
  const c=CB().find(x=>x.id===b.dataset.id);if(!c)return;
  c.items.forEach(i=>addEntry(b.dataset.slot,i));closeSheet();toast('Ajouté : '+c.name);render();
};
A['cb-del']=b=>{S.combos=CB().filter(x=>x.id!==b.dataset.id);persist('combos');toast('Repas type supprimé');const l=$('#favlist');if(l)l.innerHTML=mineList(b.dataset.slot)};

/* souvent à ce repas : saisi au moins 2 fois dans ce repas sur les 60 derniers jours (4 au plus) */
let oftenMap={};
function oftenFoods(slot){
  const from=addDays(today(),-60),to=today(),m={};
  for(const d in S.meals){
    if(d<from||d>to)continue;
    for(const e of S.meals[d]){if(e.slot!==slot)continue;const k=normTxt(e.name).trim(),o=m[k]||(m[k]={e,n:0,last:''});o.n++;if(d>=o.last){o.last=d;o.e=e}}
  }
  return Object.values(m).filter(o=>o.n>=2).sort((a,b)=>b.n-a.n||b.last.localeCompare(a.last)).slice(0,4).map(o=>o.e);
}
function oftenHtml(slot){
  const l=oftenFoods(slot);oftenMap={};if(!l.length)return '';
  return `<div class="sec">Souvent ${esc(SLOT_TO[slot])}</div><div class="list" style="margin-bottom:14px">${l.map(e=>{const id=uid();oftenMap[id]=e;return `<button class="li" data-act="f-often" data-id="${id}" data-slot="${slot}"><div class="grow"><div class="t">${esc(e.name)}</div><div class="small muted">P ${nf(e.p,0)} · G ${nf(e.c,0)} · L ${nf(e.f,0)}</div></div><b class="num">${nf(e.kcal,0)}</b></button>`}).join('')}</div>`;
}
A['f-often']=b=>{const e=oftenMap[b.dataset.id];if(!e)return;addEntry(b.dataset.slot,e);closeSheet();toast('Ajouté : '+e.name);render()};

/* ---------- 2. fiabilité des valeurs ---------- */
/* corrections : appliquées aux objets de ALLFOODS (donc à la recherche, à la fiche, aux calculs) ;
   l'original est gardé dans _o. Appelée au chargement, à la synchro (applyDoc) et à l'import. */
function applyFixes(){
  const fx=FX();
  for(const f of ALLFOODS){
    if(f._o){Object.assign(f,f._o);delete f._o}
    const v=fx[f.id];
    if(v){f._o={k:f.k,p:f.p,c:f.c,f:f.f};f.k=num(v.k);f.p=num(v.p);f.c=num(v.c);f.f=num(v.f)}
  }
}
applyFixes();
const foodSrc=f=>f.cq?'Source : Anses, Table Ciqual 2025':'Source : valeurs moyennes des tables nutritionnelles, saisies pour Forme';
function foodTools(f){
  const tw=cookTwin(f);
  return `<div class="small muted" style="margin:-8px 0 10px">${f._o?'<b style="color:var(--warn)">Valeurs corrigées par toi.</b> Original : '+nf(f._o.k,0)+' kcal · P '+nf(f._o.p)+' · G '+nf(f._o.c)+' · L '+nf(f._o.f)+'<br>':''}${foodSrc(f)}</div>
  <div class="row" style="gap:8px;flex-wrap:wrap;margin-bottom:14px">${tw?`<button class="chip" data-act="b-twin" data-id="${tw.id}">${twWords(tw.n).some(x=>/^cuit/.test(x))?'Version cuite':'Version crue'}</button>`:''}<button class="chip" data-act="b-fix">Corriger les valeurs</button></div>`;
}
A['b-fix']=()=>{
  const f=bSel;if(!f)return;const u=f.ml?'ml':'g',v=(id,l,x)=>`<div class="field"><label for="${id}">${l}</label><input class="inp" id="${id}" inputmode="decimal" value="${nf(x,1)}"></div>`;
  reSheet(`<div class="rc"><h3>Corriger les valeurs</h3><p class="small muted" style="margin:-6px 0 12px">${esc(f.n)}, pour 100 ${u}. La correction vaut pour tes prochains ajouts ; ce qui est déjà dans ton journal ne change pas.</p>
  <div class="grid2">${v('xk','Calories (kcal)',f.k)}${v('xp','Protéines (g)',f.p)}${v('xc','Glucides (g)',f.c)}${v('xf','Lipides (g)',f.f)}</div>
  <button class="btn block" data-act="b-fix-ok">Enregistrer la correction</button>
  ${f._o?'<button class="btn ghost block" style="margin-top:8px" data-act="b-fix-reset">Rétablir l’original</button>':''}
  <button class="btn ghost block" style="margin-top:8px" data-act="b-fix-back">Annuler</button></div>`);
};
const bReopen=()=>{addSheet(bSlot);bDraw()};
A['b-fix-back']=bReopen;
A['b-fix-ok']=()=>{
  const f=bSel;if(!f)return;const g=id=>num($('#'+id).value),v={k:g('xk'),p:g('xp'),c:g('xc'),f:g('xf')};
  if(!(v.k>0)||v.k>950){toast('Calories pour 100 g : entre 1 et 950');return}
  FX()[f.id]=v;persist('fixes');applyFixes();toast('Valeurs corrigées');bReopen();
};
A['b-fix-reset']=()=>{const f=bSel;if(!f)return;delete FX()[f.id];persist('fixes');applyFixes();toast('Valeurs d’origine rétablies');bReopen()};

/* cru / cuit : l'aliment jumeau, même nom avec l'autre mot (cru ↔ cuit, accordé) */
const TWIN={cru:'cuit',crue:'cuite',crus:'cuits',crues:'cuites',cuit:'cru',cuite:'crue',cuits:'crus',cuites:'crues'};
const twWords=n=>normTxt(n).replace(/[(),]/g,' ').split(/\s+/).filter(Boolean);
function cookTwin(f){
  if(!f||/^jambon/i.test(f.n))return null;   /* jambon cru et jambon cuit sont deux produits différents */
  const w=twWords(f.n);if(!w.some(x=>TWIN[x]))return null;
  const key=w.map(x=>TWIN[x]||x).join(' '),c=ALLFOODS.filter(g=>g!==f&&twWords(g.n).join(' ')===key);
  return c.find(g=>!!g.cq===!!f.cq)||c[0]||null;
}
A['b-twin']=b=>{
  const f=ALLFOODS.find(x=>x.id===b.dataset.id);if(!f)return;
  bSel=f;if(f.u&&f.u.length){bUnit=0;bQty=1}else{bUnit=-1;bQty=f.ml?200:100}
  bReopen();
};

/* ---------- 4. recettes : lire un ingrédient, calculer les valeurs ---------- */
/* « 150 g de poulet », « 2 œufs », « 1 càs d’huile d’olive », « ½ verre de lait » -> {q, u, n}
   u : 'g', 'ml', '' (à l'unité) ou une unité usuelle (càs, càc, tranche, verre…) */
const ING_UNITS=[['kg','g',1000],['kilo','g',1000],['kilos','g',1000],['g','g',1],['gr','g',1],['gramme','g',1],['grammes','g',1],['mg','g',.001],
  ['ml','ml',1],['cl','ml',10],['l','ml',1000],['litre','ml',1000],['litres','ml',1000],
  ['cas','càs'],['c a s','càs'],['cs','càs'],['cuillere a soupe','càs'],['cuilleres a soupe','càs'],
  ['cac','càc'],['c a c','càc'],['cc','càc'],['cuillere a cafe','càc'],['cuilleres a cafe','càc'],
  ['pincee','pincée'],['pincees','pincée'],['tranche','tranche'],['tranches','tranche'],['verre','verre'],['verres','verre'],['bol','bol'],['bols','bol'],
  ['sachet','sachet'],['sachets','sachet'],['boite','boîte'],['boites','boîte'],['dose','dose'],['doses','dose'],['gousse','gousse'],['gousses','gousse'],
  ['poignee','poignée'],['poignees','poignée'],['pot','pot'],['pots','pot'],['brique','brique'],['briques','brique']];
const ING_UNIT=new Map(ING_UNITS.map(([k,u,m])=>[k,[u,m||0]]));
const ING_G={'càs':15,'càc':5,'pincée':1,'verre':200,'bol':250,'tranche':30,'gousse':5,'poignée':30,'dose':30};
function parseIng(line){
  const s=String(line||'').trim().replace(/^[-•*·]\s*/,'');if(!s)return null;
  const fr={'½':.5,'¼':.25,'¾':.75};
  const m=s.match(/^(\d+(?:[.,]\d+)?(?:\s*\/\s*\d+)?|[½¼¾])?\s*(.*)$/);
  let q=1,hasQ=false;
  if(m[1]){hasQ=true;const x=m[1];q=fr[x]!=null?fr[x]:x.includes('/')?(num(x.split('/')[0])/num(x.split('/')[1])||1):num(x)}
  let rest=m[2].replace(/^[½¼¾]/,y=>{q=(hasQ?q:0)+fr[y];hasQ=true;return ''}).trim(),u='',mult=0;
  const tok=rest.split(/\s+/);
  for(const n of [3,2,1]){
    if(tok.length<n)continue;
    const k=normTxt(tok.slice(0,n).join(' ')).replace(/\./g,' ').replace(/\s+/g,' ').trim(),hit=ING_UNIT.get(k)||ING_UNIT.get(k.replace(/\s/g,''));
    if(hit&&(n<tok.length||hit[0]==='g'||hit[0]==='ml')){[u,mult]=hit;tok.splice(0,n);break}
  }
  const name=tok.join(' ').replace(/^(de la|des|du|de)\s+/i,'').replace(/^(de l|d)[’']\s*/i,'').trim();
  if(!name)return null;
  if(u==='g'||u==='ml')q*=mult;
  return {q,u,n:name,hasQ};
}
const ingFoodCache=new Map();
/* l'aliment le plus proche dans la base : on enlève des mots à la fin tant que rien n'est trouvé ;
   la version crue est préférée quand le texte ne dit pas « cuit » (poids crus dans les recettes) */
function ingFood(name){
  const k=normTxt(name);if(ingFoodCache.has(k))return ingFoodCache.get(k);
  const w=k.replace(/[()]/g,' ').split(/\s+/).filter(Boolean);let f=null;
  while(w.length&&!f){f=foodSearch(w.join(' '))[0]||null;if(!f)w.pop()}
  if(f&&/\bcuit/.test(normTxt(f.n))&&!/\bcuit/.test(k)){const tw=cookTwin(f);if(tw)f=tw}
  ingFoodCache.set(k,f);return f;
}
/* grammes d'une ligne lue, ou null si on ne sait pas */
function ingGrams(x,f){
  if(!x)return null;
  if(x.u==='g'||x.u==='ml')return x.q;
  if(f&&f.u&&f.u.length){
    const want=normTxt(x.u);
    const u=x.u?f.u.find(v=>v[0].split('|').some(l=>{const n=normTxt(l);return n===want||n.startsWith(want+' ')})):(f.u.find(v=>v[2])||f.u[0]);
    if(u)return x.q*u[1];
  }
  return ING_G[x.u]!=null?x.q*ING_G[x.u]:null;
}
A['rc-calc']=()=>{
  const lines=$('#rfi').value.split('\n').map(x=>x.trim()).filter(Boolean),por=Math.max(1,num($('#rfpor').value)||1);
  if(!lines.length){toast('Écris d’abord les ingrédients, un par ligne');return}
  const t={k:0,p:0,c:0,f:0},ok=[],ko=[];
  for(const l of lines){
    const x=parseIng(l),f=x&&ingFood(x.n),g=f?ingGrams(x,f):null;
    if(!f||g==null){ko.push(l);continue}
    ['k','p','c','f'].forEach(m=>t[m]+=f[m]*g/100);ok.push(l+' → '+f.n+' ('+nf(g,0)+' '+(f.ml?'ml':'g')+')');
  }
  if(!ok.length){$('#rfcalc').innerHTML='<div class="pill warn" style="white-space:normal">Aucun ingrédient reconnu. Écris par exemple « 150 g de poulet » ou « 2 œufs ».</div>';return}
  $('#rfk').value=nf(t.k/por,0);$('#rfp').value=nf(t.p/por,1);$('#rfc').value=nf(t.c/por,1);$('#rff').value=nf(t.f/por,1);
  $('#rfcalc').innerHTML=`<div class="small" style="margin-bottom:4px"><b>${ok.length} ingrédient${ok.length>1?'s':''} reconnu${ok.length>1?'s':''} sur ${lines.length}</b>, valeurs divisées par ${nf(por,1)} portion${por>1?'s':''}. Vérifie, et corrige si besoin.</div>
  <ul class="small muted" style="margin:0 0 4px;padding-left:18px">${ok.map(x=>'<li>'+esc(x)+'</li>').join('')}</ul>${ko.length?'<div class="small" style="color:var(--warn)">Non compté : '+esc(ko.join(' · '))+'</div>':''}`;
};

/* ingrédients d'une recette, sous une même forme {q, u, n} (n peut porter le pluriel : « œuf|œufs ») */
function recIngs(r){
  if(r.ing)return r.ing.map(([q,u,n])=>({q:num(q),u:u?u.split('|')[0]:'',n,uu:u}));
  return (r.ingTxt||[]).map(parseIng).filter(Boolean).map(x=>({q:x.q,u:x.u,n:x.n,uu:x.u}));
}
const ingKey=n=>fzWords(String(n).split('|')[0]).join(' ');
const ingLabel=n=>{const s=String(n).split('|')[0];return s.charAt(0).toUpperCase()+s.slice(1)};
/* rayon d'un ingrédient : la section de la bibliothèque (SLIB) de l'aliment le plus proche */
const secCache=new Map();
function ingSec(n){
  const k=ingKey(n);if(secCache.has(k))return secCache.get(k);
  const f=ingFood(String(n).split('|')[0]),s=f?f.cat.split('.')[0]:'zz';secCache.set(k,s);return s;
}
const secName=id=>{const s=SLIB.find(c=>c.id===id);return s?s.n:'Autres'};
const secOrder=id=>{const i=SLIB.findIndex(c=>c.id===id);return i<0?99:i};

/* ---------- 4. semaine : planning de 7 jours et liste de courses ---------- */
const planDays=()=>Array.from({length:7},(_,i)=>addDays(today(),i));
const planDay=d=>PL().days[d]||{};
let plAdd=null,plSlot='lu',plQ='';
function weekView(){
  /* on oublie les jours passés de plus de 14 jours */
  const P=PL(),old=Object.keys(P.days).filter(d=>d<addDays(today(),-14));if(old.length){old.forEach(d=>delete P.days[d]);persist('plan')}
  const day=d=>{
    const pd=planDay(d),rows=SLOTS.map(([s])=>{
      const items=(pd[s]||[]).map((it,i)=>{const r=recipeById(it.r);if(!r)return '';return `<div class="plitem${it.ok?' ok':''}"><button class="plck" data-act="pl-log" data-d="${d}" data-s="${s}" data-i="${i}" aria-pressed="${!!it.ok}" aria-label="${it.ok?'Déjà notée au journal':'Noter au journal'}">✓</button><button class="grow plname" data-act="rc-open" data-id="${esc(r.id)}">${esc(r.n)} <span class="muted">· ${nf(r.k,0)} kcal</span></button><button class="plx" data-act="pl-del" data-d="${d}" data-s="${s}" data-i="${i}" aria-label="Retirer ${esc(r.n)}">×</button></div>`}).join('');
      return items?`<div class="plslot"><div class="small muted">${SLOT_SHORT[s]}</div>${items}</div>`:'';
    }).join(''),k=SLOTS.reduce((t,[s])=>t+(pd[s]||[]).reduce((u,it)=>{const r=recipeById(it.r);return u+(r?r.k:0)},0),0);
    return `<div class="card plday"><div class="row sb"><h4 style="margin:0">${d===today()?'Aujourd’hui':esc(fmtDay(d))}</h4>${k?`<span class="small muted num">${nf(k,0)} kcal prévues</span>`:''}</div>${rows}<button class="addslot" data-act="pl-add" data-d="${d}">${ICON.plus} Ajouter une recette</button></div>`;
  };
  return `<div class="small muted" style="margin:0 2px 12px">Pose des recettes sur les 7 prochains jours. ✓ les note dans ton journal ; leurs ingrédients vont dans la liste de courses.</div>
  ${planDays().map(day).join('')}${shopCard()}`;
}
A['pl-add']=b=>{plAdd=b.dataset.d;plQ='';const h=new Date().getHours();plSlot=plAdd===today()?(h<11?'bk':h<16?'lu':'di'):'lu';plSheet(false)};
function plSheet(update){
  const t=plQ?fzWords(plQ):[],list=allRecipes().filter(r=>r.s.includes(plSlot)).filter(r=>!t.length||t.every(w=>normTxt(r.n).includes(w))).sort((a,b)=>a.n.localeCompare(b.n,'fr'));
  if(update){const l=$('#pllist');if(l){l.innerHTML=plRows(list);return}}
  reSheet(`<h3>${plAdd===today()?'Aujourd’hui':esc(fmtLong(plAdd))}</h3>
  <div class="seg rcslotseg" role="tablist" aria-label="Repas">${SLOTS.map(([s])=>`<button role="tab" data-act="pl-slot" data-s="${s}" aria-selected="${plSlot===s}">${SLOT_SHORT[s]}</button>`).join('')}</div>
  <div class="field"><input class="inp" type="search" id="plq" data-in="plq" placeholder="Chercher une recette" value="${esc(plQ)}" aria-label="Chercher une recette" autocomplete="off"></div>
  <div id="pllist">${plRows(list)}</div>`);
}
const plRows=list=>list.length?'<div class="list">'+list.map(r=>`<button class="li" data-act="pl-pick" data-id="${esc(r.id)}"><div class="grow"><div class="t">${esc(r.n)}</div><div class="small muted">${r.t} min · P ${nf(r.p,0)} · G ${nf(r.c,0)} · L ${nf(r.f,0)}</div></div><b class="num">${nf(r.k,0)}</b></button>`).join('')+'</div>':'<div class="empty">Aucune recette pour ce repas.</div>';
A['pl-slot']=b=>{plSlot=b.dataset.s;plSheet(false)};
I.plq=t=>{plQ=t.value;plSheet(true)};
A['pl-pick']=b=>{
  const P=PL(),d=P.days[plAdd]||(P.days[plAdd]={});(d[plSlot]=d[plSlot]||[]).push({r:b.dataset.id,ok:0});
  persist('plan');closeSheet();toast('Ajoutée '+SLOT_TO[plSlot]);render();
};
A['pl-del']=b=>{const d=planDay(b.dataset.d),l=d[b.dataset.s];if(!l)return;l.splice(+b.dataset.i,1);if(!l.length)delete d[b.dataset.s];persist('plan');render()};
A['pl-log']=b=>{
  const d=b.dataset.d,s=b.dataset.s,it=(planDay(d)[s]||[])[+b.dataset.i],r=it&&recipeById(it.r);if(!r)return;
  if(it.ok){toast('Déjà notée dans ton journal');return}
  if(d>today()){toast('Tu pourras la noter le jour même');return}
  addEntry(s,{name:r.n,kcal:r.k,p:r.p,c:r.c,f:r.f},d);rcMark(r.id,d);it.ok=1;persist('plan');toast('Notée '+SLOT_TO[s]);render();
};

/* liste de courses : ingrédients des recettes prévues (pas encore notées) + ajouts, additionnés, par rayon */
function shopItems(){
  const P=PL(),acc=new Map();
  const add=(x,src)=>{
    const u=x.u||'',k=ingKey(x.n)+'|'+u;
    const o=acc.get(k)||{k,n:x.n,u,uu:x.uu||u,q:0,src:new Set(),ex:[]};
    o.q+=num(x.q);if(src)o.src.add(src);acc.set(k,o);return o;
  };
  for(const d of planDays()){const pd=planDay(d);for(const s in pd)for(const it of pd[s]){if(it.ok)continue;const r=recipeById(it.r);if(r)recIngs(r).forEach(x=>add(x,r.n))}}
  for(const e of P.shop.extra){
    if(e.t){acc.set('x:'+e.id,{k:'x:'+e.id,n:e.t,u:'',q:0,free:1,src:new Set(),ex:[e.id]});continue}
    add(e,null).ex.push(e.id);
  }
  return [...acc.values()].map(o=>Object.assign(o,{sec:o.free?ingSec(o.n.replace(/^[\d.,\s]+/,'')):ingSec(o.n)}));
}
function shopQty(o){
  if(o.free||!o.q)return '';
  if(o.u==='g')return o.q>=1000?nf(o.q/1000,2)+' kg':nf(Math.round(o.q),0)+' g';
  if(o.u==='ml')return o.q>=1000?nf(o.q/1000,2)+' l':nf(Math.round(o.q),0)+' ml';
  if(!o.u)return frac(o.q);
  return frac(o.q)+' '+rcPl(o.uu||o.u,o.q);
}
function shopCard(){
  const P=PL(),items=shopItems(),done=P.shop.done,secs=[...new Set(items.map(o=>o.sec))].sort((a,b)=>secOrder(a)-secOrder(b));
  const row=o=>{const on=!!done[o.k],name=o.free?o.n:(o.u?ingLabel(o.n):ingLabel(rcPl(o.n,o.q)));
    return `<div class="shrow${on?' on':''}"><button class="shck" data-act="sh-tog" data-k="${esc(o.k)}" aria-pressed="${on}"><span class="box" aria-hidden="true">✓</span><span class="grow">${esc(name)}</span><b class="num">${esc(shopQty(o))}</b></button>${!o.src.size?`<button class="plx" data-act="sh-del" data-k="${esc(o.k)}" aria-label="Retirer ${esc(name)}">×</button>`:''}</div>`};
  const nOn=items.filter(o=>done[o.k]).length;
  return `<div class="card" id="shop"><div class="row sb"><h2 style="margin:0">Liste de courses</h2>${items.length?`<span class="small muted">${nOn} / ${items.length}</span>`:''}</div>
  ${items.length?secs.map(s=>`<div class="sec" style="margin-top:14px">${esc(secName(s))}</div>${items.filter(o=>o.sec===s).sort((a,b)=>a.n.localeCompare(b.n,'fr')).map(row).join('')}`).join(''):'<div class="small muted" style="margin-top:8px">Vide pour l’instant : pose des recettes dans la semaine, ou ajoute un article.</div>'}
  <div class="row" style="gap:8px;margin-top:14px"><input class="inp" id="shnew" placeholder="Ajouter un article" aria-label="Ajouter un article" style="flex:1;min-width:0"><button class="btn" style="min-height:48px" data-act="sh-add">Ajouter</button></div>
  ${nOn?`<button class="btn soft block" style="margin-top:10px" data-act="sh-fridge">Ranger dans mon frigo (${nOn})</button>`:''}</div>`;
}
A['sh-tog']=b=>{const d=PL().shop.done,k=b.dataset.k;if(d[k])delete d[k];else d[k]=1;persist('plan');render()};
A['sh-add']=()=>{
  const v=($('#shnew').value||'').trim();if(!v)return;const x=parseIng(v);
  PL().shop.extra.push(x&&x.hasQ?{id:uid(),q:x.q,u:x.u,uu:x.u,n:x.n}:{id:uid(),t:v});persist('plan');render();
  setTimeout(()=>{const i=$('#shnew');if(i)i.focus()},30);
};
A['sh-del']=b=>{const P=PL(),o=shopItems().find(x=>x.k===b.dataset.k);if(!o)return;P.shop.extra=P.shop.extra.filter(e=>!o.ex.includes(e.id));delete P.shop.done[o.k];persist('plan');render()};
/* les articles cochés rejoignent le frigo ; ceux ajoutés à la main quittent la liste */
A['sh-fridge']=()=>{
  const P=PL(),items=shopItems().filter(o=>P.shop.done[o.k]),F=FR();
  items.forEach(o=>{const k=ingKey(o.free?o.n.replace(/^[\d.,\s]+/,''):o.n);if(k&&!F.have.includes(k))F.have.push(k)});
  const gone=items.filter(o=>!o.src.size);
  const ids=new Set(gone.flatMap(o=>o.ex));P.shop.extra=P.shop.extra.filter(e=>!ids.has(e.id));gone.forEach(o=>delete P.shop.done[o.k]);
  persist('plan');persist('fridge');toast(items.length+(items.length>1?' articles rangés':' article rangé')+' dans ton frigo');render();
};
/* depuis la fiche d'une recette : ses ingrédients (pour les portions choisies) vont dans la liste */
A['rc-shop']=()=>{
  const r=recipeById(rcOpenId);if(!r)return;const l=recIngs(r);
  l.forEach(x=>PL().shop.extra.push({id:uid(),q:x.q*rcK,u:x.u,uu:x.uu,n:x.n}));
  persist('plan');toast(l.length+' ingrédient'+(l.length>1?'s ajoutés':' ajouté')+' à ta liste de courses');
};

/* ---------- frigo : ce qu'il a déjà (sans photo) ---------- */
/* toujours considérés comme présents */
const ALWAYS=/^(sel|poivre|eau|huile|epice|cumin|paprika|curry|cannelle|curcuma|muscade|origan|thym|herbes de provence|piment|ras el hanout)\b/;
const isAlways=n=>ALWAYS.test(ingKey(n));
const inFridge=(n,have)=>{const k=ingKey(n);return isAlways(n)||have.some(h=>h===k||(' '+k+' ').includes(' '+h+' ')||(' '+h+' ').includes(' '+k+' '))};
function rcMissing(r){const have=FR().have;return recIngs(r).filter(x=>!inFridge(x.n,have)).map(x=>ingLabel(x.n))}
let rcFridge=false;
function fridgeSheet(){
  const have=FR().have,seen=new Map();
  allRecipes().forEach(r=>recIngs(r).forEach(x=>{const k=ingKey(x.n);if(k&&!isAlways(x.n)&&!seen.has(k))seen.set(k,ingLabel(x.n))}));
  have.forEach(k=>{if(!seen.has(k))seen.set(k,k.charAt(0).toUpperCase()+k.slice(1))});
  const all=[...seen.entries()].map(([k,n])=>({k,n,s:ingSec(n)})),secs=[...new Set(all.map(o=>o.s))].sort((a,b)=>secOrder(a)-secOrder(b));
  reSheet(`<div class="rc"><h3>Mon frigo</h3><p class="small muted" style="margin:-6px 0 12px">Coche ce que tu as chez toi : « Avec mon frigo » classe les recettes selon ce qui te manque. Sel, poivre, eau, huile et épices comptent toujours comme présents.</p>
  <div class="row" style="gap:8px;margin-bottom:12px"><input class="inp" id="frnew" placeholder="Ajouter un aliment" aria-label="Ajouter un aliment" style="flex:1;min-width:0"><button class="btn" style="min-height:48px" data-act="fr-add">Ajouter</button></div>
  ${secs.map(s=>`<div class="sec" style="margin-top:12px">${esc(secName(s))}</div><div class="frchips">${all.filter(o=>o.s===s).sort((a,b)=>a.n.localeCompare(b.n,'fr')).map(o=>`<button class="chip" data-act="fr-tog" data-k="${esc(o.k)}" aria-pressed="${have.includes(o.k)}">${esc(o.n)}</button>`).join('')}</div>`).join('')}
  <div class="grid2" style="margin-top:16px"><button class="btn ghost" data-act="fr-clear">Tout décocher</button><button class="btn" data-act="fr-done">Terminé</button></div></div>`);
}
A['fr-open']=()=>fridgeSheet();
A['fr-chip']=()=>{rcFridge=!rcFridge;render()};
A['fr-tog']=b=>{const h=FR().have,k=b.dataset.k,i=h.indexOf(k);if(i<0)h.push(k);else h.splice(i,1);persist('fridge');b.setAttribute('aria-pressed',String(i<0))};
A['fr-add']=()=>{const k=ingKey(($('#frnew').value||'').trim());if(!k)return;if(!FR().have.includes(k))FR().have.push(k);persist('fridge');fridgeSheet()};
A['fr-clear']=()=>{FR().have=[];persist('fridge');fridgeSheet()};
A['fr-done']=()=>{closeSheet();render()};

/* ---------- 5. bilan : 7 jours, série, calendrier du mois ---------- */
/* série de jours notés, qui pardonne : un jour sans rien est pardonné s'il n'y a pas eu d'autre jour
   sans rien dans les 7 jours précédents ; aujourd'hui pas encore noté ne casse pas la série */
function mealStreak(){
  const has=d=>dayEntries(d).length>0,days=Object.keys(S.meals).filter(has).sort();
  if(!days.length)return {n:0,fg:0};
  const first=days[0];let d=today(),n=0,fg=0;
  if(!has(d))d=addDays(d,-1);
  while(d>=first){
    if(has(d))n++;
    else{
      let other=false;
      for(let i=1;i<=7;i++){const x=addDays(d,-i);if(x<first)break;if(!has(x)){other=true;break}}
      if(other)break;fg++;
    }
    d=addDays(d,-1);
  }
  return {n,fg};
}
/* couleur d'un jour selon l'objectif : 60–110 % vert, jusqu'à 125 % orange, au-delà rouge, moins de 60 % gris */
function dayBand(d){
  const es=dayEntries(d);if(!es.length)return '';
  const pct=kcalOf(es)/Math.max(1,goals().kcal);
  return pct<.6?'blo':pct<=1.1?'bok':pct<=1.25?'bwarn':'bbad';
}
let blMonth=today().slice(0,7);
function bilanView(){
  const g=goals(),days=Array.from({length:7},(_,i)=>addDays(today(),i-6)),st=mealStreak();
  const bars=days.map(d=>{const k=kcalOf(dayEntries(d)),pct=k/Math.max(1,g.kcal);return `<div class="wkbar"><span class="small num">${k?nf(k,0):''}</span><div class="wkcol"><i class="${dayBand(d)}" style="height:${Math.min(pct,1.5)/1.5*100}%"></i><s style="bottom:${100/1.5}%"></s></div><span class="small muted">${esc(parseD(d).toLocaleDateString('fr-FR',{weekday:'narrow'}))}</span></div>`}).join('');
  const noted=days.filter(d=>dayEntries(d).length),avg=m=>noted.length?noted.reduce((t,d)=>t+totals(dayEntries(d))[m],0)/noted.length:0;
  const [y,mo]=blMonth.split('-').map(Number),first=blMonth+'-01',nDays=new Date(Date.UTC(y,mo,0)).getUTCDate(),lead=(parseD(first).getDay()+6)%7;
  let cells='';for(let i=0;i<lead;i++)cells+='<span></span>';
  for(let i=1;i<=nDays;i++){
    const d=blMonth+'-'+pad(i),fut=d>today(),k=kcalOf(dayEntries(d)),band=fut?'':dayBand(d);
    cells+=`<button class="calday ${band}${d===today()?' today':''}" data-act="bl-day" data-d="${d}" ${fut?'disabled':''} aria-label="${esc(fmtLong(d))}${k?' : '+nf(k,0)+' kcal, '+Math.round(k/Math.max(1,g.kcal)*100)+' % de l’objectif':' : rien de noté'}">${i}</button>`;
  }
  const mName=parseD(first).toLocaleDateString('fr-FR',{month:'long',year:'numeric'});
  return `<div class="card" id="blstreak"><h2>Ta série</h2><div style="font:800 22px/1.2 var(--font-display)">${st.n?'🔥 '+st.n+' jour'+(st.n>1?'s':'')+' noté'+(st.n>1?'s':'')+' de suite':'Pas encore de série'}</div>
    <div class="small muted" style="margin-top:6px">${st.fg?st.fg+' jour'+(st.fg>1?'s':'')+' sans rien de noté pardonné'+(st.fg>1?'s':'')+'. ':''}Un oubli est pardonné s’il n’y en a pas eu d’autre dans la semaine d’avant. Aujourd’hui compte dès que tu notes quelque chose.</div></div>
  <div class="card"><h2>7 derniers jours</h2><div class="wkbars" role="img" aria-label="Calories des 7 derniers jours">${bars}</div>
    <div class="small muted" style="margin-top:8px">Trait : ton objectif de ${nf(g.kcal,0)} kcal.</div>
    <div class="stats" id="blavg" style="grid-template-columns:repeat(4,1fr);margin-top:12px"><div class="stat"><b class="num">${nf(avg('kcal'),0)}</b><span>kcal / jour</span></div><div class="stat"><b class="num">${nf(avg('p'),0)}</b><span>prot. (g)</span></div><div class="stat"><b class="num">${nf(avg('c'),0)}</b><span>gluc. (g)</span></div><div class="stat"><b class="num">${nf(avg('f'),0)}</b><span>lip. (g)</span></div></div>
    <div class="small muted" style="margin-top:8px">Moyennes sur ${noted.length} jour${noted.length>1?'s':''} noté${noted.length>1?'s':''} sur 7.</div></div>
  <div class="card"><div class="row sb" style="margin-bottom:10px"><button class="iconbtn" data-act="bl-mon" data-n="-1" aria-label="Mois précédent">${ICON.chevL}</button><h2 style="margin:0">${esc(mName)}</h2><button class="iconbtn" data-act="bl-mon" data-n="1" aria-label="Mois suivant" ${blMonth>=today().slice(0,7)?'disabled style="opacity:.35"':''}>${ICON.chev}</button></div>
    <div class="cal">${['L','M','M','J','V','S','D'].map(x=>`<b>${x}</b>`).join('')}${cells}</div>
    <div class="callegend small muted"><span><i class="bok"></i>60–110 %</span><span><i class="bwarn"></i>jusqu’à 125 %</span><span><i class="bbad"></i>au-delà</span><span><i class="blo"></i>moins de 60 %</span></div>
    <div class="small muted" style="margin-top:6px">Par rapport à ton objectif de calories, indicatif. Touche un jour pour l’ouvrir.</div></div>`;
}
A['bl-mon']=b=>{const [y,m]=blMonth.split('-').map(Number),d=new Date(Date.UTC(y,m-1+Number(b.dataset.n),1)),v=d.getUTCFullYear()+'-'+pad(d.getUTCMonth()+1);if(v>today().slice(0,7))return;blMonth=v;render()};
A['bl-day']=b=>{const d=b.dataset.d;if(!d||d>today())return;fDate=d;foodSub='journal';render();window.scrollTo(0,0)};
