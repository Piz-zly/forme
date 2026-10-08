
/* ===== CHERCHER : aliments de base sans code-barres =====
   Premier onglet de la feuille « Ajouter » du Repas. Cherche dans FOODS (js2e.js,
   généré) sans tenir compte des accents ni des majuscules, puis demande la quantité
   (grammes, ou une unité usuelle : œuf, tranche, càs…) avec le calcul en direct. */
/* Sections : les memes que la bibliotheque du Scan (SLIB, js4b.js). Chaque aliment a une categorie « section.sous-section ». */
const foodCats=()=>[['top','Courants']].concat(SLIB.filter(c=>FOODS.some(f=>f.cat.split('.')[0]===c.id)).map(c=>[c.id,c.s]));
const normTxt=s=>String(s??'').toLowerCase().replace(/œ/g,'oe').replace(/æ/g,'ae').normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’'\-]/g,' ');
FOODS.forEach(f=>{f._k=normTxt(f.n+' '+(f.a||''))});
let bq='',bcat='top',bSel=null,bUnit=-1,bQty=100,bSlot='bk';   /* bUnit : -1 = grammes (ou ml), sinon rang dans f.u */

/* ---- recherche ---- */
function foodSearch(q){
  /* tous les mots doivent se trouver ; « oeufs » trouve « œuf » (pluriel retiré) */
  const t=normTxt(q).split(/\s+/).filter(Boolean).map(w=>w.length>3&&/[sx]$/.test(w)?w.slice(0,-1):w);
  if(!t.length)return[];
  const res=[];
  for(const f of FOODS){
    let sc=0,ok=true;
    for(const w of t){
      const i=f._k.indexOf(w);
      if(i<0){ok=false;break}
      sc+=i===0?0:f._k[i-1]===' '?1:3;      /* début du nom, début d'un mot, ailleurs */
    }
    if(ok)res.push({f,sc:sc-(f.top?.5:0)});
  }
  return res.sort((a,b)=>a.sc-b.sc||a.f.n.length-b.f.n.length).slice(0,50).map(x=>x.f);
}
function foodList(){
  if(bq.trim())return foodSearch(bq);
  if(bcat==='top')return FOODS.filter(f=>f.top).sort((a,b)=>a.top-b.top);
  return FOODS.filter(f=>f.cat.split('.')[0]===bcat).sort((a,b)=>a.n.localeCompare(b.n,'fr'));
}
function foodRow(f){
  return `<button class="li" data-act="b-pick" data-id="${f.id}"><div class="grow"><div class="t">${esc(f.n)}</div><div class="small muted">P ${nf(f.p)} · G ${nf(f.c)} · L ${nf(f.f)} · pour 100 ${f.ml?'ml':'g'}</div></div><div style="text-align:right;flex:none"><b class="num" style="font-size:18px">${nf(f.k,0)}</b><div class="small muted">kcal</div></div></button>`;
}
function foodRows(){
  const list=foodList();
  if(!list.length)return '<div class="empty">Aucun aliment trouvé.<br>Ajoute-le à la main dans l’onglet « Manuel ».</div>';
  if(!bq.trim()&&bcat!=='top'){   /* une section : les aliments par sous-section */
    const sec=SLIB.find(c=>c.id===bcat);
    return (sec?sec.subs:[]).map(([k,n])=>{
      const l=list.filter(f=>f.cat===bcat+'.'+k);
      return l.length?`<div class="sec libsub">${esc(n)} <span class="muted">· ${l.length}</span></div><div class="list">${l.map(foodRow).join('')}</div>`:'';
    }).join('');
  }
  return '<div class="list">'+list.map(foodRow).join('')+'</div>';
}
function foodSearchHtml(slot){
  const chips=foodCats().map(([k,n])=>`<button class="chip" data-act="b-cat" data-k="${k}" aria-pressed="${!bq.trim()&&bcat===k}">${n}</button>`).join('');
  return `<div class="field"><input class="inp" type="search" id="bqin" data-in="bq" placeholder="Ex : œuf, riz, poulet…" value="${esc(bq)}" aria-label="Chercher un aliment" autocomplete="off"></div>
  <div class="chips" id="bchips">${chips}</div>
  <div id="bres">${foodRows()}</div>
  <div class="small muted" style="margin-top:12px">Valeurs moyennes pour 100 g, indicatives. Pour un produit de marque, utilise « Scanner ».</div>`;
}
/* Met à jour la liste et les puces sans refaire la feuille (le clavier reste ouvert). */
function foodRefresh(){
  const q=bq.trim();
  document.querySelectorAll('#bchips .chip').forEach(c=>c.setAttribute('aria-pressed',String(!q&&c.dataset.k===bcat)));
  const r=$('#bres');if(r)r.innerHTML=foodRows();
  const i=$('#bqin');if(i&&i.value!==bq)i.value=bq;
}
I.bq=t=>{bq=t.value;foodRefresh()};
A['b-cat']=b=>{bcat=b.dataset.k;bq='';foodRefresh()};

/* ---- quantité ---- */
const bBase=f=>f.ml?'ml':'g';
const bGrams=()=>bUnit<0?bQty:bQty*bSel.u[bUnit][1];
const bFmt=q=>Math.abs(q*4-Math.round(q*4))<1e-9?frac(q):nf(q,2);
/* Texte écrit dans le journal : « 2 œufs », « 150 g de riz basmati cuit », « 1 càs d’huile d’olive ». */
function bLabel(){
  const f=bSel,low=f.n.charAt(0).toLowerCase()+f.n.slice(1);
  if(bUnit<0)return nf(bQty,2)+' '+bBase(f)+' '+rcDe(low);
  const [lab,,self]=f.u[bUnit],q=bFmt(bQty)+' '+rcPl(lab,bQty);
  return self?q:q+' '+rcDe(low);
}
function bQuick(){
  const v=bUnit<0?(bSel.ml?[100,200,250,330]:[50,100,150,200,250]):[.5,1,2,3,4];
  return v.map(x=>`<button class="chip" data-act="b-q" data-v="${x}" aria-pressed="${bQty===x}">${bUnit<0?x:frac(x)}</button>`).join('');
}
function foodQtyHtml(){
  const f=bSel,units=[[-1,bBase(f)]].concat((f.u||[]).map((u,i)=>[i,u[0].split('|')[0]]));
  return `<button class="btn ghost" style="min-height:44px;margin-bottom:12px" data-act="b-back">${ICON.chevL} Retour</button>
  <div class="t" style="font:800 20px/1.2 var(--font-display);margin-bottom:2px">${esc(f.n)}</div>
  <div class="small muted" style="margin-bottom:14px">Pour 100 ${bBase(f)} : ${nf(f.k,0)} kcal · P ${nf(f.p)} · G ${nf(f.c)} · L ${nf(f.f)}</div>
  ${units.length>1?`<div class="seg rcslotseg" id="bunits" role="tablist" aria-label="Unité">${units.map(([i,n])=>`<button role="tab" data-act="b-unit" data-i="${i}" aria-selected="${bUnit===i}">${esc(n)}</button>`).join('')}</div>`:''}
  <div class="field"><label for="bqty">Quantité (<span id="bu">${esc(bUnit<0?bBase(f):f.u[bUnit][0].split('|')[1]||f.u[bUnit][0])}</span>)</label><input class="inp" id="bqty" data-in="bqty" inputmode="decimal" value="${String(bQty).replace('.',',')}"></div>
  <div class="chips" id="bquick">${bQuick()}</div>
  <div class="stats" id="bmac" style="grid-template-columns:repeat(4,1fr)"></div>
  <div class="small muted" id="bgrams" style="margin:8px 0 12px;min-height:18px"></div>
  <label class="row" style="margin:0 0 14px;min-height:44px"><input type="checkbox" id="bfav" style="width:22px;height:22px"> Garder dans mes favoris</label>
  <button class="btn block" id="badd" data-act="b-add"></button>`;
}
function bDraw(typing){
  const f=bSel;if(!f||!$('#bmac'))return;
  const g=bGrams(),m=x=>x*g/100;
  $('#bmac').innerHTML=[['kcal',m(f.k),0],['prot. (g)',m(f.p),1],['gluc. (g)',m(f.c),1],['lip. (g)',m(f.f),1]].map(([l,v,d])=>`<div class="stat"><b class="num">${nf(v,d)}</b><span>${l}</span></div>`).join('');
  $('#bgrams').textContent=bUnit<0?'':'= '+nf(g,0)+' '+bBase(f);
  const a=$('#badd');a.textContent='Ajouter · '+nf(m(f.k),0)+' kcal';a.disabled=!(bQty>0);
  document.querySelectorAll('#bunits button').forEach(b=>b.setAttribute('aria-selected',String(Number(b.dataset.i)===bUnit)));
  $('#bquick').innerHTML=bQuick();
  $('#bu').textContent=bUnit<0?bBase(f):f.u[bUnit][0].split('|')[1]||f.u[bUnit][0];
  if(!typing)$('#bqty').value=String(bQty).replace('.',',');
}
A['b-pick']=b=>{
  const f=FOODS.find(x=>x.id===b.dataset.id);if(!f)return;
  bSel=f;
  if(f.u&&f.u.length){bUnit=0;bQty=1}else{bUnit=-1;bQty=f.ml?200:100}
  addSheet(bSlot);bDraw();
};
A['b-back']=()=>{bSel=null;addSheet(bSlot)};
A['b-unit']=b=>{
  /* on garde la même quantité en grammes : 2 œufs deviennent 110 g */
  const g=bGrams(),i=Number(b.dataset.i);bUnit=i;
  bQty=i<0?Math.round(g):Math.max(.25,Math.round(g/bSel.u[i][1]*4)/4);
  bDraw();
};
A['b-q']=b=>{bQty=Number(b.dataset.v);bDraw()};
I.bqty=t=>{bQty=num(t.value);bDraw(true)};
A['b-add']=()=>{
  const f=bSel;if(!f||!(bQty>0))return;
  const g=bGrams(),m=x=>x*g/100,e={name:bLabel(),kcal:m(f.k),p:m(f.p),c:m(f.c),f:m(f.f)};
  addEntry(bSlot,e);
  if($('#bfav')&&$('#bfav').checked){S.foods.unshift({id:uid(),name:e.name,kcal:r1(e.kcal),p:r1(e.p),c:r1(e.c),f:r1(e.f)});persist('foods')}
  bSel=null;closeSheet();toast('Ajouté : '+e.name);render();
};
