/* ===== VERSION INSTALLABLE : scan en direct + recherche Open Food Facts ===== */
const ADD_HIGH=/^(e102|e104|e110|e122|e124|e129|e171|e249|e250|e251|e252|e320|e321)$/,ADD_MOD=/^(e150c|e150d|e211|e220|e221|e222|e223|e224|e226|e227|e228|e407|e433|e435|e436|e466|e950|e951|e954|e955|e621)$/;
function offAdd(tags){
  return (tags||[]).map(t=>String(t).replace(/^.*:/,'').toLowerCase()).filter(t=>/^e\d/.test(t)).slice(0,25)
    .map(t=>({name:t.toUpperCase(),risk:ADD_HIGH.test(t)?'high':ADD_MOD.test(t)?'moderate':'low'}));
}
async function offLookup(code){
  const f='product_name,product_name_fr,brands,nutriments,additives_tags,nutrition_data_per,categories_tags';
  const ctl=new AbortController(),to=setTimeout(()=>ctl.abort(),9000);
  try{
    const r=await fetch('https://world.openfoodfacts.org/api/v2/product/'+code+'.json?fields='+f,{signal:ctl.signal});
    if(!r.ok)return null;
    const j=await r.json();if(!j||j.status!==1||!j.product)return null;
    const d=j.product,n=d.nutriments||{},g=k=>num(n[k+'_100g']);
    let kcal=g('energy-kcal');if(!kcal&&n['energy_100g'])kcal=num(n['energy_100g'])/4.184;
    if(!kcal&&!g('fat')&&!g('carbohydrates')&&!g('proteins'))return null;
    const fv=num(n['fruits-vegetables-legumes-estimate-from-ingredients_100g']||n['fruits-vegetables-nuts-estimate-from-ingredients_100g']);
    const salt=n['salt_100g']!=null?g('salt'):g('sodium')*2.5;
    return{id:uid(),date:today(),name:String(d.product_name_fr||d.product_name||'Produit '+code),brand:String(d.brands||'').split(',')[0].trim(),code,src:'off',
      per:{kcal:Math.round(kcal),fat:g('fat'),sat:g('saturated-fat'),carbs:g('carbohydrates'),sugar:g('sugars'),salt,fiber:g('fiber'),prot:g('proteins'),fv},
      additives:offAdd(d.additives_tags),tags:(Array.isArray(d.categories_tags)?d.categories_tags:[]).slice(-12).map(t=>String(t).replace(/^[a-z]{2}:/,''))};
  }catch(_){return null}finally{clearTimeout(to)}
}
function liveBtn(ctx,slot){
  return `<button class="btn block" style="margin-bottom:10px" data-act="live" data-ctx="${ctx}" data-slot="${slot||''}">${ICON.cam} Scanner en direct</button>`;
}
let liveRun=false,liveStream=null;
function stopLive(){
  liveRun=false;
  if(liveStream){liveStream.getTracks().forEach(t=>t.stop());liveStream=null}
  const o=document.getElementById('live');if(o)o.remove();
}
A['live-close']=()=>stopLive();
A.live=async b=>{
  const ctx=b.dataset.ctx,slot=b.dataset.slot;
  if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){toast('Caméra indisponible ici');return}
  stopLive();
  const ov=document.createElement('div');ov.id='live';
  ov.innerHTML='<video id="lv" playsinline muted autoplay></video><div class="lframe"></div><div class="lmsg">Place le code-barres dans le cadre</div><button class="btn lclose" data-act="live-close">Annuler</button>';
  document.body.appendChild(ov);
  try{liveStream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'},width:{ideal:1280},height:{ideal:720}},audio:false})}
  catch(e){stopLive();toast('Accès à la caméra refusé : autorise-la dans les réglages du navigateur');return}
  const v=document.getElementById('lv');if(!v){stopLive();return}
  v.srcObject=liveStream;try{await v.play()}catch(_){}
  let det=null,ZX=null;
  if('BarcodeDetector' in window){try{det=new BarcodeDetector({formats:['ean_13','ean_8','upc_a','upc_e']})}catch(_){det=null}}
  if(!det){try{ZX=await loadZX()}catch(_){stopLive();toast('Lecteur de codes indisponible');return}}
  const cv=document.createElement('canvas'),cx=cv.getContext('2d',{willReadFrequently:true});
  liveRun=true;let code=null;
  while(liveRun){
    await new Promise(r=>setTimeout(r,det?120:170));
    if(!liveRun)break;
    if(v.readyState<2||!v.videoWidth)continue;
    try{
      if(det){const r=await det.detect(v);for(const x of r)if(EAN_OK(x.rawValue)){code=x.rawValue;break}}
      else{
        const W=v.videoWidth,H=v.videoHeight,sc=Math.min(1,900/Math.max(W,H)),w=Math.round(W*sc),h=Math.round(H*sc);
        cv.width=w;cv.height=h;cx.drawImage(v,0,0,w,h);
        const px=cx.getImageData(0,0,w,h).data,lum=new Uint8ClampedArray(w*h);
        for(let i=0,k=0;i<px.length;i+=4,k++)lum[k]=(px[i]*299+px[i+1]*587+px[i+2]*114)/1000;
        const c=decodeLuma(ZX,lum,w,h);if(c&&EAN_OK(c))code=c;
      }
    }catch(_){}
    if(code)break;
  }
  const ok=liveRun&&code;stopLive();
  if(ok){try{navigator.vibrate&&navigator.vibrate(40)}catch(_){}await afterCode(code,ctx,slot)}
};
/* sauvegarde : téléchargement d'un fichier */
dl={save:async({filename,data})=>{
  const u=URL.createObjectURL(new Blob([data],{type:'application/json'})),a=document.createElement('a');
  a.href=u;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(u),4000);return{status:'saved'};
}};
A.upd=async()=>{
  toast('Recherche d’une mise à jour…');
  try{const r=await navigator.serviceWorker.getRegistration();if(r)await r.update()}catch(_){}
  try{const ks=await caches.keys();await Promise.all(ks.map(k=>caches.delete(k)))}catch(_){}
  setTimeout(()=>location.reload(),600);
};
/* installation hors ligne + stockage durable */
if('serviceWorker' in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('sw.js').catch(()=>{}));
try{navigator.storage&&navigator.storage.persist&&navigator.storage.persist()}catch(_){}
window.ZX_URL='vendor/zxing.min.js';

/* ===== PARTAGE ENTRANT : pas et calories envoyés depuis l’application de podomètre ===== */
function parseShared(txt){
  const t=' '+String(txt||'').replace(/[    ]/g,' ').toLowerCase()+' ';
  const grab=re=>{
    const m=t.match(re);if(!m)return 0;
    let r=String(m[1]).trim().replace(/[ ']/g,'').replace(/[.,](?=\d{3}(\D|$))/g,'').replace(',','.');
    const n=parseFloat(r);return isFinite(n)&&n>0?Math.round(n):0;
  };
  const steps=grab(/([\d][\d .,']*)\s*(?:pas|steps|schritte|passi|pasos|krok)/)||grab(/(?:pas|steps|pasos)\s*[:=]?\s*([\d][\d .,']*)/);
  const kcal =grab(/([\d][\d .,']*)\s*(?:kcal|calories|calorie|cal\b)/)||grab(/(?:kcal|calories|cal)\s*[:=]?\s*([\d][\d .,']*)/);
  return {steps,kcal};
}
A['share-open']=()=>{};
function shareSheet(raw,s,k){
  const d=today(),found=s||k;
  openSheet(`<h3>Reçu de ton podomètre</h3>
  <p class="muted small" style="margin:-8px 0 14px">${found?'Vérifie les deux chiffres, corrige-les si besoin, puis enregistre la journée du '+esc(fmtShort(d))+'.':'Je n’ai pas reconnu de chiffres dans ce partage. Recopie-les à la main pour la journée du '+esc(fmtShort(d))+'.'}</p>
  <div class="field"><label for="apas">Pas</label><input class="inp" id="apas" inputmode="numeric" value="${s||''}" placeholder="Ex : 8 400"></div>
  <div class="field"><label for="akcal">Calories dépensées (kcal)</label><input class="inp" id="akcal" inputmode="numeric" value="${k||''}" placeholder="Ex : 2 450"></div>
  <button class="btn block" data-act="act-save" data-d="${d}">Enregistrer la journée</button>
  <button class="btn ghost block" style="margin-top:10px" data-act="close">Annuler</button>
  ${raw?`<div class="sec" style="margin-top:18px">Texte reçu</div><div class="small muted" style="overflow-wrap:anywhere">${esc(raw).slice(0,400)}</div>`:''}`);
}
(function(){
  const q=new URLSearchParams(location.search);
  if(!q.has('shared')&&!q.has('text')&&!q.has('title')&&!q.has('url'))return;
  const raw=[q.get('title'),q.get('text'),q.get('url')].filter(Boolean).join(' · ');
  try{window.history.replaceState(null,'',location.pathname)}catch(_){}
  const {steps,kcal}=parseShared(raw);
  tab='weight';S.ui.tab='weight';saveLocal();render();
  setTimeout(()=>shareSheet(raw,steps,kcal),250);
})();
