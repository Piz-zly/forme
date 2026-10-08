/* ===== SCAN ===== */
let scanFiles=[],scanUrls=[],scanBusy=false,scanCur=null,hasVision=false,maxImgs=3,dl=null,scanErr='';
const ENERGY=[335,670,1005,1340,1675,2010,2345,2680,3015,3350],SUGAR=[4.5,9,13.5,18,22.5,27,31,36,40,45],SAT=[1,2,3,4,5,6,7,8,9,10],SODIUM=[90,180,270,360,450,540,630,720,810,900],FIBER=[.9,1.9,2.8,3.7,4.7],PROT=[1.6,3.2,4.8,6.4,8];
const cnt=(v,arr)=>arr.filter(t=>v>t).length;
function evalProduct(p){
  const q=p.per;
  const neg=cnt(q.kcal*4.184,ENERGY)+cnt(q.sugar,SUGAR)+cnt(q.sat,SAT)+cnt(q.salt*400,SODIUM);
  const fvp=q.fv>80?5:q.fv>60?2:q.fv>40?1:0;
  const pos=cnt(q.fiber,FIBER)+fvp+((neg>=11&&fvp<5)?0:cnt(q.prot,PROT));
  const pts=neg-pos;
  const letter=pts<=-1?'A':pts<=2?'B':pts<=10?'C':pts<=18?'D':'E';
  const nutri100=clamp((40-pts)/55*100,0,100);
  const adds=p.additives||[];
  const pen=adds.reduce((t,a)=>t+(a.risk==='high'?15:a.risk==='moderate'?7:2),0);
  let score=clamp(Math.round(nutri100-pen),0,100);
  if(adds.some(a=>a.risk==='high'))score=Math.min(score,49);
  const v=score>=75?['Excellent','#12865A']:score>=50?['Bon','#5E9E2E']:score>=25?['Médiocre','#C77A0A']:['Mauvais','#C93B30'];
  const lvl=(x,lo,hi)=>x<=lo?'good':x<=hi?'warn':'bad';
  const rows=[
    ['Énergie',nf(q.kcal,0)+' kcal',q.kcal>400?'warn':'neutral'],
    ['Matières grasses',nf(q.fat)+' g',lvl(q.fat,3,17.5)],
    ['dont saturées',nf(q.sat)+' g',lvl(q.sat,1.5,5)],
    ['Glucides',nf(q.carbs)+' g','neutral'],
    ['dont sucres',nf(q.sugar)+' g',lvl(q.sugar,5,22.5)],
    ['Sel',nf(q.salt,2)+' g',lvl(q.salt,.3,1.5)],
    ['Fibres',nf(q.fiber)+' g',q.fiber>=3?'good':'neutral'],
    ['Protéines',nf(q.prot)+' g',q.prot>=10?'good':'neutral']
  ];
  const pros=[],cons=[];
  if(q.sat<=1.5)pros.push('Peu de graisses saturées');else if(q.sat>5)cons.push('Riche en graisses saturées');
  if(q.sugar<=5)pros.push('Peu de sucres');else if(q.sugar>22.5)cons.push('Très sucré');
  if(q.salt<=.3)pros.push('Peu de sel');else if(q.salt>1.5)cons.push('Très salé');
  if(q.fat>17.5)cons.push('Riche en matières grasses');
  if(q.fiber>=3)pros.push('Source de fibres');
  if(q.prot>=10)pros.push('Riche en protéines');
  if(q.kcal>400)cons.push('Très calorique');
  adds.forEach(a=>{if(a.risk!=='low')cons.push('Additif : '+a.name)});
  return{pts,letter,score,verdict:v[0],color:v[1],rows,pros,cons,estimated:p.src==='estimate'};
}
const PRODUCT_PROMPT=`Tu analyses la ou les photos d’un produit alimentaire (emballage, tableau nutritionnel, liste d’ingrédients, code-barres). Réponds uniquement par un objet JSON de la forme :
{"name": string, "brand": string ou null, "source": "label" si tu as lu le tableau nutritionnel sur les photos, sinon "estimate", "per100": {"kcal": number, "fat": number, "sat": number, "carbs": number, "sugar": number, "salt": number, "fiber": number, "protein": number}, "fruitVeg": number (pourcentage estimé de fruits, légumes, légumineuses et noix dans le produit, 0 si aucun ou inconnu), "additives": [{"name": "E250 Nitrite de sodium", "risk": "low" ou "moderate" ou "high"}], "barcode": string ou null (chiffres du code-barres seulement si lisibles)}.
Règles : toutes les valeurs sont pour 100 g (ou 100 ml). Si le tableau est donné par portion, convertis avec le poids de la portion. Si seul le sodium est indiqué, sel = sodium × 2,5. Sans tableau lisible, estime au mieux d’après le produit reconnu et mets source "estimate". Additifs : relève ceux de la liste d’ingrédients ; "high" seulement pour ceux largement jugés à risque (nitrites E249 à E252, E171, colorants azoïques comme E102, E110, E122, E124, E129, etc.), "moderate" pour ceux discutés, "low" pour les inoffensifs. Si les photos ne montrent aucun produit alimentaire, réponds {"error": "illisible"}.`;

/* ===== BARCODE (decoded on the phone, products remembered) ===== */
const EAN_OK=c=>{if(!/^(\d{8}|\d{12,13})$/.test(c))return false;const d=c.split('').map(Number),chk=d.pop();let s=0;d.reverse().forEach((v,i)=>s+=v*(i%2?1:3));return (10-s%10)%10===chk};
let zxP=null;
function loadZX(){
  if(window.ZXing)return Promise.resolve(window.ZXing);
  if(zxP)return zxP;
  zxP=new Promise((res,rej)=>{const s=document.createElement('script');s.src=window.ZX_URL||'https://cdn.jsdelivr.net/npm/@zxing/library@0.21.3/umd/index.min.js';s.onload=()=>res(window.ZXing);s.onerror=()=>{zxP=null;rej(new Error('zxing'))};document.head.appendChild(s)});
  return zxP;
}
function rot90(l,w,h){const o=new Uint8ClampedArray(l.length);for(let y=0;y<h;y++)for(let x=0;x<w;x++)o[x*h+(h-1-y)]=l[y*w+x];return[o,h,w]}
function decodeLuma(ZX,lum,w,h){
  const hints=new Map();hints.set(ZX.DecodeHintType.POSSIBLE_FORMATS,[ZX.BarcodeFormat.EAN_13,ZX.BarcodeFormat.EAN_8,ZX.BarcodeFormat.UPC_A,ZX.BarcodeFormat.UPC_E]);hints.set(ZX.DecodeHintType.TRY_HARDER,true);
  const r=new ZX.MultiFormatReader();r.setHints(hints);
  try{return r.decode(new ZX.BinaryBitmap(new ZX.HybridBinarizer(new ZX.RGBLuminanceSource(lum,w,h)))).getText()}catch(e){return null}
}
function tryAll(ZX,lum,w,h){
  let c=decodeLuma(ZX,lum,w,h);if(c&&EAN_OK(c))return c;
  const [l2,w2,h2]=rot90(lum,w,h);c=decodeLuma(ZX,l2,w2,h2);return c&&EAN_OK(c)?c:null;
}
async function loadBitmap(file){
  try{return await createImageBitmap(file,{imageOrientation:'from-image'})}catch(_){}
  try{return await createImageBitmap(file)}catch(_){}
  return await new Promise((res,rej)=>{const u=URL.createObjectURL(file),im=new Image();im.onload=()=>{URL.revokeObjectURL(u);res(im)};im.onerror=rej;im.src=u});
}
async function readBarcode(file){
  const bmp=await loadBitmap(file);
  const W=bmp.width||bmp.naturalWidth,H=bmp.height||bmp.naturalHeight;
  try{ /* native detector when the browser has one */
    if('BarcodeDetector' in window){const det=new BarcodeDetector({formats:['ean_13','ean_8','upc_a','upc_e']});const r=await det.detect(bmp);for(const x of r)if(EAN_OK(x.rawValue))return x.rawValue}
  }catch(_){}
  try{
    const ZX=await loadZX();
    for(const mx of [1400,900,640]){
      const s=Math.min(1,mx/Math.max(W,H)),w=Math.round(W*s),h=Math.round(H*s);
      const cv=document.createElement('canvas');cv.width=w;cv.height=h;
      const cx=cv.getContext('2d',{willReadFrequently:true});cx.drawImage(bmp,0,0,w,h);
      const px=cx.getImageData(0,0,w,h).data,lum=new Uint8ClampedArray(w*h);
      for(let i=0,k=0;i<px.length;i+=4,k++)lum[k]=(px[i]*299+px[i+1]*587+px[i+2]*114)/1000;
      const c=tryAll(ZX,lum,w,h);if(c)return c;
      await new Promise(r=>setTimeout(r,0));
    }
  }catch(_){}
  if(sampleFn&&hasVision){ /* last resort: Claude reads the printed digits, checked with the EAN checksum */
    try{
      const r=await sampleFn('Cette photo montre un code-barres de produit. Lis les chiffres imprimés sous les barres. Réponds uniquement par ces chiffres, sans espace ni texte. Si tu ne les lis pas, réponds 0.',{images:[file],modelTier:'quick',cache:false});
      const c=String(r.text||'').replace(/\D/g,'');if(EAN_OK(c))return c;
    }catch(_){}
  }
  return null;
}
const findByCode=c=>S.scans.find(p=>p.code===c);
let bc={busy:false,msg:''},pendingCode='',bcProd=null,bcLabelBusy=false,bcSlot='bk',manualFrom='';
function bcReset(){bc={busy:false,msg:''};pendingCode='';bcProd=null}
const errMsg=e=>e&&e.code==='not_granted'?'L’accès à Claude a été refusé. Utilise la saisie manuelle.':e&&e.code==='rate_limited'?'Trop de demandes. Réessaie dans un instant.':e&&e.code==='unreadable'?'Je n’ai pas reconnu de produit sur ces photos. Cadre le tableau nutritionnel de près.':'L’analyse a échoué. Réessaie, ou saisis les valeurs à la main.';
async function analyseProduct(files,code){
  if(!sampleFn)throw{code:'not_granted'};
  const res=await sampleFn.json(PRODUCT_PROMPT+libPrompt(),{images:files,modelTier:'default'});
  if(!res||res.error||!res.per100)throw{code:'unreadable'};
  const q=res.per100;
  return{id:uid(),date:today(),name:String(res.name||'Produit'),brand:res.brand?String(res.brand):'',code:code||(res.barcode&&EAN_OK(String(res.barcode))?String(res.barcode):''),src:res.source==='label'?'label':'estimate',cat:libOk(String(res.category||''))&&res.category!=='autre.autre'?String(res.category):undefined,
    per:{kcal:num(q.kcal),fat:num(q.fat),sat:num(q.sat),carbs:num(q.carbs),sugar:num(q.sugar),salt:num(q.salt),fiber:num(q.fiber),prot:num(q.protein),fv:num(res.fruitVeg)},
    additives:(Array.isArray(res.additives)?res.additives:[]).filter(a=>a&&a.name).map(a=>({name:String(a.name),risk:['low','moderate','high'].includes(a.risk)?a.risk:'low'}))};
}
function redrawScan(){const el=$('#scanbody');if(el)el.innerHTML=scanTabHtml(bcSlot)}
const refreshBc=ctx=>{if(ctx==='food')redrawScan();else render()};
function scanTabHtml(slot){
  bcSlot=slot;
  const cam=(label,attr)=>`<label class="btn block" style="cursor:pointer">${ICON.cam} ${label}<input type="file" accept="image/*" capture="environment" ${attr} class="hidden"></label>`;
  const msg=bc.msg?`<div class="pill bad" style="margin-top:10px;white-space:normal">${esc(bc.msg)}</div>`:'';
  if(bc.busy)return '<div class="bcbox"><span class="spin"></span><div class="muted" style="margin-top:8px">Lecture du code-barres…</div></div>';
  if(bcProd){
    const p=bcProd,e=evalProduct(p),g=p.lastG||100,k=g/100;
    return `<div class="score" style="margin-bottom:12px"><div class="badge num" style="width:64px;height:64px;font-size:26px;background:${e.color}">${e.score}</div><div style="min-width:0"><div style="font:800 18px/1.15 var(--font-display);overflow-wrap:anywhere">${esc(p.name)}</div><div class="muted small">${esc(p.brand||'')}${p.brand?' · ':''}${e.verdict} · Nutri-Score ${e.letter}</div></div></div>
    <div class="stats" style="grid-template-columns:repeat(4,1fr);margin-bottom:12px"><div class="stat"><b>${nf(p.per.kcal,0)}</b><span>kcal</span></div><div class="stat"><b>${nf(p.per.prot,0)}</b><span>prot. g</span></div><div class="stat"><b>${nf(p.per.carbs,0)}</b><span>gluc. g</span></div><div class="stat"><b>${nf(p.per.fat,0)}</b><span>lip. g</span></div></div>
    <div class="small muted" style="margin:-4px 0 10px">Valeurs pour 100 g${p.src==='estimate'?' (estimées)':''}${p.code?' · code '+esc(p.code):''}</div>
    <div class="field"><label for="bcg">Quantité mangée (g ou ml)</label><input class="inp" id="bcg" inputmode="decimal" data-in="bcg" value="${nf(g,1)}"></div>
    <button class="btn block" data-act="bc-add">Ajouter · ${nf(p.per.kcal*k,0)} kcal</button>
    <div class="grid2" style="margin-top:10px"><button class="btn ghost" data-act="bc-reset">Autre produit</button><button class="btn ghost" data-act="bc-open">Fiche complète</button></div>`;
  }
  if(pendingCode){
    return `<div class="bcbox"><div class="bcnum">${esc(pendingCode)}</div><div class="muted" style="margin:6px 0 14px">Produit pas encore connu. Photographie son tableau nutritionnel : il sera retenu pour les prochains scans.</div>
    ${bcLabelBusy?'<div class="row muted" style="justify-content:center"><span class="spin"></span> Lecture de l’étiquette…</div>':hasVision?cam('Photographier l’étiquette','data-ch="bc-label"'):''}</div>${msg}
    <button class="btn soft block" style="margin-top:10px" data-act="s-manual-code">Saisir les valeurs à la main</button><button class="btn ghost block" style="margin-top:10px" data-act="bc-reset">Annuler</button>`;
  }
  const recent=S.scans.slice(0,5).map(p=>{const e=evalProduct(p);return `<button class="li" data-act="bc-pick" data-id="${p.id}"><span class="badge num" style="width:38px;height:38px;font-size:15px;background:${e.color}">${e.score}</span><div class="grow"><div class="t">${esc(p.name)}</div><div class="small muted">${nf(p.per.kcal,0)} kcal / 100 g</div></div></button>`}).join('');
  return `<div class="bcbox"><p class="muted" style="margin:0 0 14px">Photographie le code-barres du produit. S’il est déjà connu, sa fiche s’affiche aussitôt.</p>${typeof liveBtn==='function'?liveBtn('food',slot):''}${cam(typeof liveBtn==='function'?'Photo d’un code-barres':'Scanner un code-barres','data-ch="bc-file" data-ctx="food" data-slot="'+slot+'"')}</div>${msg}
  ${recent?'<div class="sec" style="margin-top:16px">Produits déjà scannés</div><div class="list">'+recent+'</div>':''}`;
}
async function onBarcodeFile(file,ctx,slot){
  bc={busy:true,msg:''};if(slot)bcSlot=slot;refreshBc(ctx);
  let code=null;try{code=await readBarcode(file)}catch(_){}
  await afterCode(code,ctx,slot);
}
async function afterCode(code,ctx,slot){
  if(slot)bcSlot=slot;
  if(!code){bc.busy=false;bc.msg='Code illisible. Cadre le code-barres de près, bien à plat et bien éclairé, puis réessaie.';refreshBc(ctx);return}
  let p=findByCode(code),fromNet=false;
  if(!p&&typeof offLookup==='function'){
    bc={busy:true,msg:''};refreshBc(ctx);
    try{p=await offLookup(code);if(p){saveScan(p);fromNet=true}}catch(_){}
  }
  bc.busy=false;
  if(ctx==='food'){bcProd=p||null;pendingCode=p?'':code}
  else{scanCur=p||null;pendingCode=p?'':code;if(p)toast(fromNet?'Produit trouvé':'Produit reconnu')}
  refreshBc(ctx);
  if(ctx==='scan'&&scanCur)setTimeout(()=>{const r=$('#sres');if(r)r.scrollIntoView({behavior:'smooth',block:'start'})},80);
}
async function onLabelFiles(fs){
  if(bcLabelBusy)return;bcLabelBusy=true;bc.msg='';redrawScan();
  try{const p=await analyseProduct(fs.slice(0,maxImgs),pendingCode);saveScan(p);bcProd=p;pendingCode=''}
  catch(e){bc.msg=errMsg(e)}
  bcLabelBusy=false;redrawScan();
}
A['bc-reset']=()=>{bcReset();redrawScan()};
A['bc-pick']=b=>{bcProd=S.scans.find(x=>x.id===b.dataset.id)||null;pendingCode='';redrawScan()};
A['bc-add']=()=>{
  const p=bcProd,g=num($('#bcg').value);if(!p||g<=0){toast('Indique une quantité');return}
  const k=g/100;addEntry(bcSlot,{name:p.name+' ('+nf(g,0)+' g)',kcal:p.per.kcal*k,p:p.per.prot*k,c:p.per.carbs*k,f:p.per.fat*k});
  p.lastG=g;persist('scans');closeSheet();toast('Ajouté : '+p.name);render();
};
A['bc-open']=()=>{scanCur=bcProd;closeSheet();tab='scan';S.ui.tab='scan';render();window.scrollTo(0,0)};
I.bcg=t=>{const p=bcProd;if(!p)return;const k=num(t.value)/100,b=$('[data-act="bc-add"]');if(b)b.textContent='Ajouter · '+nf(p.per.kcal*k,0)+' kcal'};
A['s-manual-code']=()=>{manualFrom='food';A['s-manual']()};

VIEWS.scan=()=>{
  if(scanSub==='lib')return libView();
  const thumbs=scanUrls.length?`<div class="thumbs">${scanUrls.map(u=>`<img src="${u}" alt="Photo du produit">`).join('')}</div>`:'';
  const canVision=hasVision;
  const hist=S.scans.slice(0,5).map(s=>{const e=evalProduct(s);return `<button class="li" data-act="s-open" data-id="${s.id}"><span class="badge num" style="width:46px;height:46px;font-size:18px;background:${e.color}">${e.score}</span><div class="grow"><div class="t">${esc(s.name)}</div><div class="small muted">${esc(s.brand||'')}${s.brand?' · ':''}${esc(fmtShort(s.date))}</div></div>${ICON.chev}</button>`}).join('');
  const bcCard=`<div class="card"><h2>Code-barres</h2>
  ${pendingCode?`<div class="bcnum" style="margin-bottom:6px">${esc(pendingCode)}</div><div class="muted small" style="margin-bottom:12px">Produit pas encore connu : photographie son tableau nutritionnel ci-dessous, il sera retenu pour les prochains scans.</div>`:`<p class="muted small" style="margin:0 0 12px">Photographie le code-barres. S’il est déjà connu, la fiche s’affiche tout de suite.</p>`}
  ${bc.busy?'<div class="row muted"><span class="spin"></span> Lecture du code…</div>':`${typeof liveBtn==='function'?liveBtn('scan',''):''}<label class="btn ${typeof liveBtn==='function'?'ghost ':''}block" style="cursor:pointer">${ICON.cam} ${pendingCode?'Scanner un autre code':'Scanner un code-barres'}<input type="file" accept="image/*" capture="environment" data-ch="bc-file" data-ctx="scan" class="hidden"></label>`}
  ${bc.msg?`<div class="pill bad" style="margin-top:10px;white-space:normal">${esc(bc.msg)}</div>`:''}</div>`;
  return scanSeg()+bcCard+`<div class="card"><h2>${pendingCode?'Étiquette du produit':'Analyser un produit'}</h2>
  ${canVision?`<p class="muted small" style="margin:0 0 12px">Photographie le tableau nutritionnel et la liste d’ingrédients (jusqu’à ${maxImgs} photos). La note est calculée à partir du Nutri-Score et des additifs.</p>
  <div class="grid2"><label class="btn" style="cursor:pointer">${ICON.cam} Photo<input type="file" accept="image/*" capture="environment" data-ch="s-files" class="hidden"></label>
  <label class="btn ghost" style="cursor:pointer">Galerie<input type="file" accept="image/*" multiple data-ch="s-files" class="hidden"></label></div>${thumbs}
  ${scanUrls.length?`<div class="row" style="margin-top:6px"><button class="btn block" id="sgo" data-act="s-go" ${scanBusy?'disabled':''}>${scanBusy?'<span class="spin"></span> Analyse…':'Analyser'}</button><button class="btn ghost" data-act="s-clear" aria-label="Effacer les photos">×</button></div>`:''}`
  :`<p class="muted small" style="margin:0 0 12px">L’analyse par photo n’est pas disponible ici. Tu peux saisir les valeurs de l’étiquette à la main.</p>`}
  ${scanErr?`<div class="pill bad" style="margin-top:10px;white-space:normal">${esc(scanErr)}</div>`:''}
  <button class="btn soft block" style="margin-top:12px" data-act="s-manual">Saisir les valeurs à la main</button></div>
  <div id="sres">${scanCur?resultCard(scanCur)+libMove(scanCur):''}</div>
  <div class="card"><h2>Derniers produits scannés</h2>${hist?'<div class="list">'+hist+'</div>'+(S.scans.length>5?`<button class="btn soft block" style="margin-top:10px" data-act="lib-go">Voir toute la bibliothèque (${S.scans.length})</button>`:`<button class="btn soft block" style="margin-top:10px" data-act="lib-go">Ouvrir la bibliothèque</button>`):'<div class="empty">Tes produits analysés seront gardés ici, rangés par catégorie dans la bibliothèque.</div>'}</div>`;
};
function resultCard(p){
  const e=evalProduct(p);
  const code=p.code?`<a class="small" style="color:var(--accent);font-weight:700" href="https://world.openfoodfacts.org/product/${encodeURIComponent(p.code)}" target="_blank" rel="noopener">Fiche Open Food Facts (${esc(p.code)})</a>`:'';
  return `<div class="card"><div class="score"><div class="badge num" style="background:${e.color}">${e.score}</div><div style="min-width:0"><div style="font:800 20px/1.15 var(--font-display);overflow-wrap:anywhere">${esc(p.name)}</div><div class="muted small">${esc(p.brand||'')}</div>
    <div class="row" style="gap:6px;margin-top:6px;flex-wrap:wrap"><span class="pill" style="background:${e.color};color:#fff">${e.verdict}</span><span class="pill neutral">Nutri-Score ${e.letter}</span><span class="pill neutral">${p.src==='label'?'Lu sur l’étiquette':p.src==='manual'?'Saisie manuelle':'Estimation'}</span></div></div></div>
  ${e.estimated?'<div class="small muted" style="margin-top:10px">Valeurs estimées d’après le produit reconnu : vérifie avec l’étiquette si c’est important.</div>':''}
  <div style="margin-top:12px">${e.rows.map(r=>`<div class="nrow"><span class="dot ${r[2]}"></span><span style="flex:1">${r[0]}</span><b class="num">${r[1]}</b></div>`).join('')}<div class="small muted" style="padding-top:6px">Pour 100 g ou 100 ml</div></div>
  ${(p.additives||[]).length?`<div class="sec" style="margin-top:14px">Additifs</div>${p.additives.map(a=>`<div class="nrow"><span class="dot ${a.risk==='high'?'bad':a.risk==='moderate'?'warn':'good'}"></span><span style="flex:1">${esc(a.name)}</span><span class="small muted">${a.risk==='high'?'À risque':a.risk==='moderate'?'Discuté':'Sans risque'}</span></div>`).join('')}`:''}
  ${e.pros.length||e.cons.length?`<div class="sec" style="margin-top:14px">En résumé</div>${e.cons.map(c=>`<div class="nrow"><span class="dot bad"></span>${esc(c)}</div>`).join('')}${e.pros.map(c=>`<div class="nrow"><span class="dot good"></span>${esc(c)}</div>`).join('')}`:''}
  <div class="row" style="margin-top:14px;gap:10px"><button class="btn block" data-act="s-journal" data-id="${p.id}">Ajouter au journal</button></div>
  ${code?'<div style="margin-top:12px">'+code+'</div>':''}
  <div class="small muted" style="margin-top:10px">Note maison : 70 % Nutri-Score simplifié, pénalités selon les additifs. Elle n’est pas celle de Yuka.</div></div>`;
}
I['s-files']=null;
document.addEventListener('change',e=>{
  const t=e.target,k=t.dataset&&t.dataset.ch;if(!k)return;
  if(k==='s-files'){
    const fs=[...t.files];t.value='';if(!fs.length)return;
    scanFiles=scanFiles.concat(fs).slice(0,maxImgs);
    scanUrls.forEach(u=>URL.revokeObjectURL(u));scanUrls=scanFiles.map(f=>URL.createObjectURL(f));
    scanErr='';scanCur=null;render();
  }else if(k==='bc-file'){const f=t.files[0],ctx=t.dataset.ctx,slot=t.dataset.slot;t.value='';if(f)onBarcodeFile(f,ctx,slot)}
  else if(k==='bc-label'){const fs=[...t.files];t.value='';if(fs.length)onLabelFiles(fs)}
});
A['s-clear']=()=>{scanUrls.forEach(u=>URL.revokeObjectURL(u));scanFiles=[];scanUrls=[];scanErr='';render()};
async function detectCode(files){
  try{
    if(!('BarcodeDetector' in window))return null;
    const det=new BarcodeDetector({formats:['ean_13','ean_8','upc_a','upc_e']});
    for(const f of files){const bmp=await createImageBitmap(f);const r=await det.detect(bmp);if(r&&r.length)return r[0].rawValue}
  }catch(_){}
  return null;
}
A['s-go']=async()=>{
  if(scanBusy||!scanFiles.length||!sampleFn)return;
  scanBusy=true;scanErr='';render();
  try{
    const code=pendingCode||await detectCode(scanFiles);
    const p=await analyseProduct(scanFiles,code);
    saveScan(p);scanCur=p;pendingCode='';
  }catch(e){scanErr=errMsg(e)}
  scanBusy=false;render();
  if(scanCur)setTimeout(()=>{const r=$('#sres');if(r)r.scrollIntoView({behavior:'smooth',block:'start'})},80);
};
function saveScan(p){S.scans=[p].concat(S.scans.filter(x=>x.id!==p.id&&!(p.code&&x.code===p.code))).slice(0,400);persist('scans')}
A['s-open']=b=>{scanCur=S.scans.find(x=>x.id===b.dataset.id)||null;render();setTimeout(()=>{const r=$('#sres');if(r)r.scrollIntoView({behavior:'smooth',block:'start'})},60)};
A['s-manual']=()=>{
  const f=(id,l)=>`<div class="field"><label for="${id}">${l}</label><input class="inp" id="${id}" inputmode="decimal"></div>`;
  openSheet(`<h3>Valeurs pour 100 g</h3><div class="field"><label for="pn">Produit</label><input class="inp" id="pn" placeholder="Ex : Céréales croustillantes"></div>
  <div class="grid2">${f('pk','Énergie (kcal)')}${f('pf','Matières grasses (g)')}${f('ps','dont saturées (g)')}${f('pc','Glucides (g)')}${f('pu','dont sucres (g)')}${f('pl','Sel (g)')}${f('pb','Fibres (g)')}${f('pp','Protéines (g)')}</div>
  <button class="btn block" data-act="s-manual-ok">Calculer la note</button>`);
};
A['s-manual-ok']=()=>{
  const g=id=>num($('#'+id).value);const name=$('#pn').value.trim();
  if(!name||!g('pk')){toast('Indique le nom et l’énergie');return}
  const p={id:uid(),date:today(),name,brand:'',code:pendingCode||'',src:'manual',per:{kcal:g('pk'),fat:g('pf'),sat:g('ps'),carbs:g('pc'),sugar:g('pu'),salt:g('pl'),fiber:g('pb'),prot:g('pp'),fv:0},additives:[]};
  saveScan(p);
  if(manualFrom==='food'){manualFrom='';pendingCode='';bcProd=p;addTab='scan';addSheet(bcSlot);return}
  pendingCode='';scanCur=p;closeSheet();render();
};
A['s-journal']=b=>{
  const p=S.scans.find(x=>x.id===b.dataset.id)||scanCur;if(!p)return;
  const h=new Date().getHours(),def=h<10?'bk':h<15?'lu':h<18?'sn':'di';
  openSheet(`<h3>Ajouter au journal</h3><div class="muted" style="margin:-8px 0 12px">${esc(p.name)}</div>
  <div class="field"><label for="jg">Quantité (g ou ml)</label><input class="inp" id="jg" inputmode="decimal" value="100"></div>
  <div class="field"><label for="js">Repas</label><select class="inp" id="js">${SLOTS.map(s=>`<option value="${s[0]}" ${s[0]===def?'selected':''}>${s[1]}</option>`).join('')}</select></div>
  <button class="btn block" data-act="s-journal-ok" data-id="${p.id}">Ajouter aux repas d’aujourd’hui</button>`);
};
A['s-journal-ok']=b=>{
  const p=S.scans.find(x=>x.id===b.dataset.id)||scanCur,g=num($('#jg').value);if(!p||g<=0){toast('Indique une quantité');return}
  const k=g/100;
  addEntry($('#js').value,{name:p.name+' ('+nf(g,0)+' g)',kcal:p.per.kcal*k,p:p.per.prot*k,c:p.per.carbs*k,f:p.per.fat*k},today());
  closeSheet();toast('Ajouté à tes repas');
};

/* ===== SETTINGS & BACKUP ===== */
A.settings=()=>{
  const g=S.settings,f=(id,l,v)=>`<div class="field"><label for="${id}">${l}</label><input class="inp" id="${id}" inputmode="decimal" value="${v==null?'':nf(v)}"></div>`;
  openSheet(`<h3>Réglages</h3><div class="sec">Objectifs du jour</div>
  <div class="field"><label for="gk">Calories visées (kcal)</label><input class="inp" id="gk" inputmode="decimal" data-in="gcalc" value="${nf(g.kcal)}"></div>
  <label class="row" style="min-height:44px;margin-bottom:8px"><input type="checkbox" id="ga" data-ch="gcalc" ${g.auto!==false?'checked':''} style="width:22px;height:22px"> Calculer selon mon poids actuel</label>
  <div class="grid2">${f('gpk','Protéines (g par kg)',g.pkg||2).replace('<input ','<input data-in="gcalc" ')}${f('gfk','Lipides (g par kg)',g.fkg||1).replace('<input ','<input data-in="gcalc" ')}</div>
  <div class="small muted" id="gprev" style="margin:-4px 0 12px"></div>
  <div class="sec" style="margin-top:6px">Objectifs fixes (si le calcul auto est coupé)</div>
  <div class="grid2">${f('gp','Protéines (g)',g.p)}${f('gc','Glucides (g)',g.c)}${f('gf','Lipides (g)',g.f)}</div>
  <div class="grid2">${f('gw','Poids visé (kg)',g.goalW)}${f('gt','Palier du cercle (kg)',g.step)}</div>
  <div class="grid2">${f('gs','Poids de départ (kg)',g.startW)}${f('gr','Repos entre séries (s)',g.rest)}</div>
  <div class="small muted" style="margin:-4px 0 12px">Poids de départ vide : la première pesée est utilisée.</div>
  <div class="sec" style="margin-top:6px">Activité</div>
  <div class="grid2">${f('gst','Objectif de pas / jour',g.steps||10000)}</div>
  <button class="btn block" data-act="set-save">Enregistrer</button>
  <div class="sec" style="margin-top:22px">Sauvegarde</div>
  <p class="small muted" style="margin:0 0 10px">${syncState==='ok'?'Tes données sont enregistrées en privé sur ton compte, en plus de ce téléphone.':'Tes données restent sur cet appareil. Fais une sauvegarde de temps en temps.'}</p>
  <div class="grid2"><button class="btn ghost" data-act="exp">Exporter</button><label class="btn ghost" style="cursor:pointer">Restaurer<input type="file" accept=".json,application/json" data-ch="imp" class="hidden"></label></div>
  <div id="expout"></div>${typeof A.upd==='function'?'<div class="sec" style="margin-top:22px">Application</div><button class="btn ghost block" data-act="upd">Vérifier les mises à jour</button>':''}
  <div class="small muted" style="margin-top:14px">Version ${APP_VER}</div>
  <div class="small muted" style="margin-top:8px">Illustrations des mouvements : Open Exercise Illustrations (CC0, domaine public). Schémas musculaires : tracés de react-body-highlighter, © 2020 GV79, licence MIT. Lecture des codes-barres : ZXing. <a href="THIRD_PARTY.txt" target="_blank" rel="noopener" style="color:var(--accent);font-weight:700">Licences</a></div>`);
  gprev();
};
function gprev(){
  const el=$('#gprev');if(!el)return;
  const a=sortedW(),w=a.length?a[a.length-1].y:null,k=num($('#gk').value),pk=num($('#gpk').value)||2,fk=num($('#gfk').value)||1;
  if(!w){el.textContent='Enregistre une pesée pour voir le calcul.';return}
  const p=Math.round(w*pk),f=Math.round(w*fk),c=Math.round((k-4*p-9*f)/4);
  el.textContent='Pour '+nf(w)+' kg : '+p+' g de protéines, '+f+' g de lipides, '+(c<0?'calories insuffisantes':c+' g de glucides')+'.';
}
I.gcalc=()=>gprev();
A['set-save']=()=>{
  const g=S.settings,v=id=>num($('#'+id).value);
  g.auto=$('#ga').checked;if(v('gst')>0)g.steps=Math.round(v('gst'));if(v('gpk')>0)g.pkg=v('gpk');if(v('gfk')>0)g.fkg=v('gfk');
  if(v('gk')>0)g.kcal=v('gk');if(v('gp')>0)g.p=v('gp');if(v('gc')>0)g.c=v('gc');if(v('gf')>0)g.f=v('gf');
  g.goalW=v('gw')>=20?v('gw'):null;g.step=v('gt')>0?v('gt'):2.5;g.startW=v('gs')>=20?v('gs'):null;if(v('gr')>=10)g.rest=v('gr');
  persist('settings');closeSheet();toast('Réglages enregistrés');render();
};
function exportData(){const o=Object.assign({},S);delete o.ui;delete o._t;return JSON.stringify({app:'forme',v:1,date:today(),data:o})}
A.exp=async()=>{
  const json=exportData();
  try{
    if(!dl)throw{code:'unavailable'};
    await dl.save({filename:'forme-sauvegarde-'+today()+'.json',data:json});toast('Sauvegarde exportée');
  }catch(e){
    if(e&&e.code==='declined')return;
    const o=$('#expout');if(o)o.innerHTML='<div class="small muted" style="margin:12px 0 6px">Copie ce texte et garde-le dans une note :</div><textarea class="inp" readonly id="expta" style="min-height:120px;font-size:12px">'+esc(json)+'</textarea>';
    const ta=$('#expta');if(ta){ta.focus();ta.select()}
  }
};
I.imp=t=>{
  const f=t.files[0];t.value='';if(!f)return;
  const rd=new FileReader();
  rd.onload=()=>{
    try{
      const o=JSON.parse(rd.result);if(!o||o.app!=='forme'||!o.data)throw 0;
      confirmSheet('Restaurer cette sauvegarde ?','Elle remplace les données actuelles de l’appli.','Restaurer',()=>{
        const keep=S.ui,t=S._t;S=Object.assign(defaults(),o.data);S.settings=Object.assign(defaults().settings,o.data.settings||{});S.ui=keep;S._t=t;
        localIds().forEach(id=>{S._t[id]=Date.now();dirty.add(id)});saveLocal();flush();toast('Sauvegarde restaurée');render();
      });
    }catch(_){toast('Fichier non reconnu')}
  };
  rd.readAsText(f);
};

/* ===== boot ===== */
render();
if(migrated)persist('settings');
setInterval(tick,1000);
document.addEventListener('visibilitychange',()=>{if(document.hidden)flush()});
initDb();
(async()=>{
  try{
    if(window.claude&&claude.use){
      dl=await claude.use('downloads');
      sampleFn=await claude.use('sample');hasAI=!!sampleFn;
      if(sampleFn){try{const lim=await sampleFn.limits();if(lim&&lim.images){hasVision=true;maxImgs=Math.min(4,lim.images.maxCount||3)}}catch(_){}}
      if(tab==='scan'&&!sheetOpen())render();
    }
  }catch(e){}
})();
