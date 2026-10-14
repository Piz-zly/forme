/* ===== ÉTIQUETTE : texte lu sur une photo -> valeurs, puis feuille de vérification (2026.10.14-4) =====
   La lecture elle-même (Tesseract.js, hors ligne) est dans js5.js (ocrRun), version téléphone seulement :
   sans ocrRun (forme.html), aucun bouton n'apparaît. Chargé avant js4.js. Les chiffres lus sont TOUJOURS
   montrés pour vérification avant d'être enregistrés (S.scans, src:'label'). */
const LB_F=[['kcal','Énergie (kcal)'],['fat','Matières grasses (g)'],['sat','dont saturées (g)'],['carbs','Glucides (g)'],['sugar','dont sucres (g)'],['fiber','Fibres (g)'],['prot','Protéines (g)'],['salt','Sel (g)']];
const LB_NAME={kcal:'énergie',fat:'matières grasses',sat:'saturées',carbs:'glucides',sugar:'sucres',fiber:'fibres',prot:'protéines',salt:'sel'};
/* mot-clé de chaque ligne, dans cet ordre : « saturés » avant « gras », « sucres » avant « glucides » */
const LB_KEYS=[['sat',/satur/],['sugar',/\bsucres?\b|\bsugars?\b/],['fiber',/\bfibres?\b|\bfibers?\b/],['prot',/proteine|protein/],
  ['salt',/\bsel\b|\bsalt\b/],['sodium',/\bsodium\b/],['carbs',/glucides|carbohydrate|hydrates? de carbone/],['fat',/matieres? grasses?|\blipides\b|\bgraisses\b|\bfat\b/]];
/* nombres d'une ligne (déjà normalisée), sans les « 100 g » d'en-tête ni les pourcentages (AR).
   Chaque nombre porte ses lectures possibles (c), la plus probable d'abord : tel quel ; « g » collé lu
   comme 9 ou 0 (« 129 » pour 12 g) ; virgule perdue en plus (« 839 » pour 8,3 g) ; zéro de tête sans
   virgule (« 0859 » pour 0,85 g) ; une décimale de trop finissant par 9 (« 4,19 ») d'abord lue sans. */
function lbNums(l){
  l=l.replace(/(pour|par|per|\/)\s*100\s*(g|ml)\b/g,' ').replace(/\b100\s*(g|ml)\b/g,' ');
  const out=[],re=/(<\s*)?(\d{1,4}(?:[.,]\d{1,3})?)\s*(kcal|kj|mg|g|%)?/g;let m;
  while((m=re.exec(l))){
    const u=m[3]||'';if(u==='%')continue;
    const raw=m[2],f=x=>parseFloat(x.replace(',','.'))/(u==='mg'?1000:1),c=[],add=x=>{if(x!=null&&isFinite(x)&&!c.includes(x))c.push(x)};
    const sep=/[.,]/.test(raw),dec=(raw.split(/[.,]/)[1]||'').length,g9=!u&&raw.length>1&&/[90]$/.test(raw);
    const cut=g9?raw.slice(0,-1).replace(/[.,]$/,''):'',two=g9&&dec===2&&/9$/.test(raw);
    if(!sep&&raw.length>1&&raw[0]==='0'){if(cut.length>1)add(f('0.'+cut.slice(1)));add(f('0.'+raw.slice(1)))}
    else{
      if(g9&&(dec>=3||two))add(f(cut));
      add(f(raw));
      if(cut)add(f(cut));
      if(cut&&!sep&&cut.length>=2)add(f(cut)/10);
    }
    out.push({raw,u,v:c[0],rv:f(raw),c,two});
  }
  return out;
}
function parseLabel(text){
  const lines=String(text||'').split(/\r?\n/).map(l=>normTxt(l).replace(/[|]/g,' ').replace(/\s+/g,' ').trim()).filter(Boolean),all=lines.join(' ');
  /* colonne « 100 g » : la première, sauf si l'en-tête annonce la portion avant les 100 g */
  let col=0;
  for(const l of lines){
    const i100=l.search(/100\s*(g|ml)\b/);if(i100<0)continue;
    const ip=l.replace(/100\s*(g|ml)/,'      ').search(/portion|\bpart\b|pour \d+\s*(g|ml)|par \d|\(\d+\s*(g|ml)\)/);
    if(ip>=0){col=ip<i100?1:0;break}
  }
  const has100=/100\s*(g|ml)\b/.test(all);
  let portion=null;
  {const re=/(?:portion|\bpart\b|pour|par|soit|\()[^0-9]{0,14}(\d{1,3}(?:[.,]\d)?)\s*(?:g|ml)\b/g;let m;while((m=re.exec(all))){const v=parseFloat(m[1].replace(',','.'));if(v!==100&&v>0){portion=v;break}}}
  const pick=l=>l.length?l[Math.min(col,l.length-1)]:null;
  /* énergie : kcal d'abord, sinon kJ converti */
  let kcal=null;
  for(let i=0;i<lines.length&&kcal==null;i++){const kc=lbNums(lines[i]).filter(x=>x.u==='kcal');if(kc.length)kcal=pick(kc).rv}
  if(kcal==null)for(let i=0;i<lines.length&&kcal==null;i++){const kj=lbNums(lines[i]).filter(x=>x.u==='kj');if(kj.length)kcal=pick(kj).rv/4.184}
  if(kcal==null){
    const i=lines.findIndex(l=>/energ/.test(l)),ns=i<0?[]:lbNums(lines[i]);
    if(ns.length>=2&&Math.abs(ns[0].rv/ns[1].rv-4.184)<.3)kcal=ns[1].rv;
  }
  /* autres valeurs : une ligne par mot-clé (la première). Photo penchée : la valeur est parfois lue sur
     une ligne à part ; les noms restés sans valeur reçoivent, dans l'ordre, les lignes de chiffres seules */
  const tok={},need=[],orph=[],keyOf=l=>(LB_KEYS.find(([,re])=>re.test(l))||[])[0],vals=l=>lbNums(l).filter(x=>x.u!=='kcal'&&x.u!=='kj');
  lines.forEach((l,i)=>{
    const k=keyOf(l);
    if(k){if(tok[k]||need.includes(k))return;const t=pick(vals(l));if(t)tok[k]=t;else need.push(k)}
    else if(!/kcal|kj|energ|100\s*(g|ml)|portion|\bpart\b|nutriti|valeurs/.test(l)&&vals(l).length)orph.push(i);
  });
  need.forEach((k,j)=>{const i=orph[j];if(i!=null){const t=pick(vals(lines[i]));if(t)tok[k]=t}});
  if(!tok.salt&&tok.sodium){const t=tok.sodium;tok.salt={raw:t.raw,rv:t.rv*2.5,c:t.c.map(x=>x*2.5),two:false}}
  const res={kcal:kcal==null?null:Math.round(kcal),portion,basis:has100||!portion?'100':'portion',col,warn:[]};
  /* lectures possibles : on garde la combinaison la plus cohérente avec les calories */
  const cand=k=>{const t=tok[k];if(!t)return [null];return k==='salt'&&t.two?[t.rv].concat(t.c.filter(x=>x!==t.rv)):t.c};
  const main=['fat','carbs','prot','fiber'];
  let best=null;
  const walk=(i,pk,alts)=>{
    if(i===main.length){
      const v=Object.fromEntries(main.map((k,j)=>[k,pk[j]]));
      const over=main.some(k=>v[k]!=null&&v[k]>100)?1e6:0;
      const err=res.kcal!=null&&v.fat!=null&&v.carbs!=null&&v.prot!=null?Math.abs(9*v.fat+4*v.carbs+4*v.prot+2*(v.fiber||0)-res.kcal):0;
      const sc=over+err+alts*(res.kcal!=null?Math.max(8,res.kcal*.04):1);
      if(!best||sc<best.sc)best={sc,v};return;
    }
    cand(main[i]).forEach((c,j)=>walk(i+1,pk.concat([c]),alts+j));
  };
  walk(0,[],0);
  Object.assign(res,best.v);
  const sub=(k,parent)=>{const c=cand(k);if(c[0]==null)return null;const ok=c.filter(x=>x<=100&&(parent==null||x<=parent+.05));return ok.length?ok[0]:c[c.length-1]};
  res.sat=sub('sat',res.fat);res.sugar=sub('sugar',res.carbs);
  {const c=cand('salt');res.salt=c[0]==null?null:(c.find(x=>x<=25)??c[c.length-1])}
  for(const k of ['fat','carbs','prot','fiber','sat','sugar','salt'])if(res[k]!=null){
    const t=tok[k];
    if(t&&Math.abs(res[k]-t.rv)>1e-9)res.warn.push(LB_NAME[k]+' : '+nf(res[k],2)+' (lu « '+t.raw+' » : un « g » ou une virgule mal lus ?)');
    res[k]=Math.round(res[k]*100)/100;
  }
  if(res.kcal!=null&&res.fat!=null&&res.carbs!=null&&res.prot!=null){
    const calc=9*res.fat+4*res.carbs+4*res.prot+2*(res.fiber||0);
    if(Math.abs(calc-res.kcal)>Math.max(25,res.kcal*.15))res.warn.push('Les calories ('+nf(res.kcal,0)+') ne collent pas avec les macros (≈ '+nf(calc,0)+') : vérifie les chiffres.');
  }
  const miss=LB_F.map(([k])=>k).filter(k=>res[k]==null);
  if(miss.length)res.warn.push('Non trouvé : '+miss.map(k=>LB_NAME[k]).join(', ')+'.');
  res.n=8-miss.length;
  return res;
}

/* ---- boutons Photo / Galerie (téléphone seulement) ---- */
function ocrBtns(ctx,slot){
  if(typeof ocrRun!=='function')return '';
  const inp=cap=>`<input type="file" accept="image/*" ${cap?'capture="environment" ':''}data-ch="ocr-file" data-ctx="${ctx}" data-slot="${slot||''}" class="hidden">`;
  return `<div class="ocrbtns"><div class="sec">Lire une étiquette</div><div class="grid2"><label class="btn" style="cursor:pointer">${ICON.cam} Photo${inp(1)}</label><label class="btn ghost" style="cursor:pointer">Galerie${inp(0)}</label></div>
  <div class="small muted" id="ocrmsg" style="margin-top:6px">Photographie le tableau nutritionnel, bien à plat : il est lu sur ton téléphone, hors ligne, puis tu vérifies les chiffres.</div></div>`;
}
let ocrBusy=false,lbState=null;
document.addEventListener('change',e=>{
  const t=e.target;if(!t.dataset||t.dataset.ch!=='ocr-file')return;
  const f=t.files&&t.files[0],ctx=t.dataset.ctx,slot=t.dataset.slot;t.value='';if(f)ocrFlow(f,ctx,slot);
});
async function ocrFlow(file,ctx,slot){
  if(ocrBusy||typeof ocrRun!=='function')return;ocrBusy=true;
  const set=h=>{const m=$('#ocrmsg');if(m)m.innerHTML=h};
  set('<span class="row" style="gap:8px"><span class="spin"></span> Lecture de l’étiquette…'+(window.Tesseract?'':' La première fois, environ 5 Mo sont téléchargés une seule fois.')+'</span>');
  try{
    const {text,res}=await ocrRun(file);
    lbState={ctx,slot,code:ctx==='food'?'':pendingCode,url:URL.createObjectURL(file),text,res,basis:res.basis};
    labelSheet();
  }catch(e){set('<span style="color:var(--bad)">La lecture a échoué. Réessaie avec une photo plus nette et bien éclairée, ou saisis les valeurs à la main.</span>')}
  ocrBusy=false;
}
function labelSheet(){
  const s=lbState,r=s.res,val=k=>r[k]==null?'':String(k==='kcal'?Math.round(r[k]):Math.round(r[k]*100)/100).replace('.',',');
  openSheet(`<div class="rc"><h3>Vérifie l’étiquette</h3>
  <img class="ocrimg" src="${s.url}" alt="Photo de l’étiquette">
  <div class="pill warn lbwarn">Vérifie chaque chiffre avec l’étiquette : la lecture automatique peut se tromper.</div>
  <div id="lbwarns">${r.warn.map(w=>`<div class="pill neutral lbwarn">${esc(w)}</div>`).join('')}</div>
  <div class="field" style="margin-top:10px"><label for="lbn">Nom du produit</label><input class="inp" id="lbn" placeholder="Ex : Céréales croustillantes"></div>
  <div class="seg" id="lbbasis" role="tablist" aria-label="Valeurs lues pour">${[['100','Pour 100 g'],['portion','Pour une portion']].map(([b,n])=>`<button role="tab" data-act="lb-basis" data-b="${b}" aria-selected="${s.basis===b}">${n}</button>`).join('')}</div>
  <div class="field" id="lbporf" style="${s.basis==='portion'?'':'display:none'}"><label for="lbpor">Poids d’une portion (g ou ml)</label><input class="inp" id="lbpor" inputmode="decimal" value="${r.portion?String(r.portion).replace('.',','):''}"></div>
  <div class="grid2">${LB_F.map(([k,l])=>`<div class="field"><label for="lb-${k}">${l}</label><input class="inp" id="lb-${k}" inputmode="decimal" value="${val(k)}"></div>`).join('')}</div>
  <details style="margin:4px 0 14px"><summary class="small muted" style="min-height:44px;display:flex;align-items:center">Texte lu sur la photo</summary><pre class="small" style="white-space:pre-wrap;margin:0">${esc(s.text)}</pre></details>
  <div class="grid2"><button class="btn ghost" data-act="close">Annuler</button><button class="btn" data-act="lb-save">Enregistrer</button></div>
  <div class="small muted" style="margin-top:10px">Les valeurs enregistrées sont pour 100 g (une portion est convertie). Indicatif.</div></div>`);
}
A['lb-basis']=b=>{
  if(!lbState)return;lbState.basis=b.dataset.b;
  document.querySelectorAll('#lbbasis button').forEach(x=>x.setAttribute('aria-selected',String(x.dataset.b===lbState.basis)));
  const f=$('#lbporf');if(f)f.style.display=lbState.basis==='portion'?'':'none';
};
A['lb-save']=()=>{
  const s=lbState;if(!s)return;
  const name=($('#lbn').value||'').trim(),g=k=>num($('#lb-'+k).value);
  if(!name){toast('Indique le nom du produit');return}
  if(!(g('kcal')>0)){toast('Indique l’énergie (kcal)');return}
  let k=1;
  if(s.basis==='portion'){const p=num($('#lbpor').value);if(!(p>0)){toast('Indique le poids d’une portion');return}k=100/p}
  const v=x=>Math.round(g(x)*k*100)/100;
  const p={id:uid(),date:today(),name,brand:'',code:s.code||'',src:'label',per:{kcal:Math.round(g('kcal')*k),fat:v('fat'),sat:v('sat'),carbs:v('carbs'),sugar:v('sugar'),salt:v('salt'),fiber:v('fiber'),prot:v('prot'),fv:0},additives:[]};
  saveScan(p);try{URL.revokeObjectURL(s.url)}catch(_){}lbState=null;pendingCode='';
  toast('Produit enregistré');
  if(s.ctx==='scan'){scanCur=p;closeSheet();render();setTimeout(()=>{const r=$('#sres');if(r)r.scrollIntoView({behavior:'smooth',block:'start'})},80);return}
  bcProd=p;addTab='scan';addSheet(s.slot||bcSlot);
};
