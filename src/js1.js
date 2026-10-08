/* ===== utils ===== */
const APP_VER='2026.10.08-12';
const $=(s,r=document)=>r.querySelector(s);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const uid=()=>Math.random().toString(36).slice(2,9)+Date.now().toString(36).slice(-4);
const pad=n=>String(n).padStart(2,'0');
const ymd=d=>d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());
const parseD=s=>{const [y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d)};
const addDays=(s,n)=>{const d=parseD(s);d.setDate(d.getDate()+n);return ymd(d)};
const today=()=>ymd(new Date());
const dn=s=>{const [y,m,d]=s.split('-').map(Number);return Math.round(Date.UTC(y,m-1,d)/864e5)};
const fmtLong=s=>parseD(s).toLocaleDateString('fr-FR',{weekday:'long',day:'numeric',month:'long'});
const fmtShort=s=>parseD(s).toLocaleDateString('fr-FR',{day:'numeric',month:'short'});
const fmtDay=s=>parseD(s).toLocaleDateString('fr-FR',{weekday:'short',day:'numeric',month:'short'});
const nf=(n,d=1)=>Number(n).toLocaleString('fr-FR',{minimumFractionDigits:0,maximumFractionDigits:d});
const num=v=>{const n=parseFloat(String(v??'').replace(',','.'));return isFinite(n)?n:0};
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const ICON={
  check:'<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
  plus:'<svg viewBox="0 0 24 24" width="20" height="20" style="stroke:currentColor;fill:none;stroke-width:2.4;stroke-linecap:round"><path d="M12 5v14M5 12h14"/></svg>',
  chev:'<svg viewBox="0 0 24 24" width="22" height="22" style="stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round"><path d="M9 5l7 7-7 7"/></svg>',
  chevL:'<svg viewBox="0 0 24 24" width="22" height="22" style="stroke:currentColor;fill:none;stroke-width:2.2;stroke-linecap:round;stroke-linejoin:round"><path d="M15 5l-7 7 7 7"/></svg>',
  cam:'<svg viewBox="0 0 24 24" width="22" height="22" style="stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round"><path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/></svg>'
};

/* ===== state & storage ===== */
const LS='forme.v1';
const defaults=()=>({settings:{kcal:2200,p:150,c:250,f:70,goalW:80,startW:null,step:2.5,rest:90,auto:true,pkg:2,fkg:1,steps:10000},weights:{},foods:[],meals:{},routines:[],sessions:[],exercises:[],scans:[],act:{},recipes:{done:{},notes:{},mine:[]},active:null,ui:{tab:'weight'},_t:{}});
let S=defaults();
try{const raw=localStorage.getItem(LS);if(raw){const o=JSON.parse(raw);S=Object.assign(defaults(),o);S.settings=Object.assign(defaults().settings,o.settings||{})}}catch(e){}
function migrateSettings(){const g=S.settings;if(!g.v2){g.v2=1;if(g.goalW==null)g.goalW=80;if(!g.step)g.step=2.5;return true}return false}
const migrated=migrateSettings();
const SLICES=['settings','weights','foods','routines','exercises','scans','act','recipes','active'];
const docOf=(slice,key)=>slice==='meals'?'meals_'+String(key).slice(0,7):slice==='sessions'?'sessions_'+String(key).slice(0,4):slice;
function docValue(id){
  if(id.startsWith('meals_')){const p=id.slice(6),o={};for(const k in S.meals)if(k.startsWith(p)&&S.meals[k].length)o[k]=S.meals[k];return o}
  if(id.startsWith('sessions_')){const y=id.slice(9);return S.sessions.filter(x=>x.date.startsWith(y))}
  return S[id]===undefined?null:S[id];
}
function applyDoc(id,v){
  if(id.startsWith('meals_')){const p=id.slice(6);for(const k of Object.keys(S.meals))if(k.startsWith(p))delete S.meals[k];Object.assign(S.meals,v||{})}
  else if(id.startsWith('sessions_')){const y=id.slice(9);S.sessions=S.sessions.filter(x=>!x.date.startsWith(y)).concat(v||[])}
  else if(SLICES.includes(id)){S[id]=v===null&&id!=='active'?defaults()[id]:v;if(id==='settings'){S.settings=Object.assign(defaults().settings,S.settings);if(migrateSettings())dirty.add('settings')}}
}
function localIds(){
  const ids=new Set(SLICES);
  for(const k in S.meals)if(S.meals[k].length)ids.add(docOf('meals',k));
  for(const s of S.sessions)ids.add(docOf('sessions',s.date));
  return ids;
}
let dbc=null,syncState='local',dirty=new Set(),saveTimer=null;
function saveLocal(){try{localStorage.setItem(LS,JSON.stringify(S))}catch(e){}}
function persist(slice,key){
  const id=docOf(slice,key);dirty.add(id);S._t[id]=Date.now();saveLocal();
  clearTimeout(saveTimer);saveTimer=setTimeout(flush,900);
}
async function flush(){
  if(!dbc||!dirty.size)return;
  const ids=[...dirty];dirty.clear();
  for(const id of ids){
    try{await dbc.doc(id).set({t:S._t[id]||Date.now(),v:docValue(id)});syncState='ok'}
    catch(e){dirty.add(id);syncState='error'}
  }
}
async function initDb(){
  try{
    if(!window.claude||!claude.use)return;
    const [db,user]=await Promise.all([claude.use('db'),claude.use('user')]);
    if(!db||!user)return;
    const id=await user.id();if(!id)return;
    dbc=db.collection('data/users/'+id);
    const snap=await dbc.get();
    const remote=new Map();
    snap.docs.forEach(d=>{const x=d.data();if(x)remote.set(d.id,x)});
    let changed=false;
    for(const [rid,x] of remote){
      const lt=S._t[rid]||0;
      if((x.t||0)>lt){applyDoc(rid,x.v);S._t[rid]=x.t;changed=true}
      else if(lt>(x.t||0))dirty.add(rid);
    }
    for(const lid of localIds()){
      if(remote.has(lid))continue;
      const v=docValue(lid);
      const empty=v===null||(Array.isArray(v)&&!v.length)||(typeof v==='object'&&!Array.isArray(v)&&!Object.keys(v).length);
      if(!empty){if(!S._t[lid])S._t[lid]=Date.now();dirty.add(lid)}
    }
    syncState='ok';saveLocal();
    if(changed)render();
    flush();
  }catch(e){dbc=null;syncState='local'}
}

/* ===== ui helpers ===== */
const A={},I={};
function toast(msg){
  document.querySelectorAll('.toast').forEach(t=>t.remove());
  const t=document.createElement('div');t.className='toast';t.setAttribute('role','status');t.textContent=msg;document.body.appendChild(t);
  setTimeout(()=>t.remove(),2200);
}
function openSheet(html){
  $('#layer').innerHTML='<div class="scrim"><div class="sheet" role="dialog" aria-modal="true"><div class="grab"></div>'+html+'</div></div>';
}
function closeSheet(){$('#layer').innerHTML=''}
const sheetOpen=()=>!!$('#layer .scrim');
function confirmSheet(title,text,okLabel,onOk){
  openSheet('<h3>'+esc(title)+'</h3><p class="muted" style="margin:0 0 16px">'+esc(text)+'</p><div class="grid2"><button class="btn ghost" data-act="close">Annuler</button><button class="btn danger" data-act="confirm-ok">'+esc(okLabel)+'</button></div>');
  A['confirm-ok']=()=>{closeSheet();onOk()};
}
A.close=()=>closeSheet();
document.addEventListener('click',e=>{
  if(e.target.classList&&e.target.classList.contains('scrim')){closeSheet();return}
  const b=e.target.closest('[data-act]');if(!b)return;
  const f=A[b.dataset.act];if(f)f(b,e);
});
document.addEventListener('input',e=>{const k=e.target.dataset&&e.target.dataset.in;if(k&&I[k])I[k](e.target,e)});
document.addEventListener('change',e=>{const k=e.target.dataset&&e.target.dataset.ch;if(k&&I[k])I[k](e.target,e)});
document.addEventListener('focusin',e=>{if(e.target.matches&&e.target.matches('input,textarea,select'))setTimeout(()=>{try{e.target.scrollIntoView({block:'center',behavior:'smooth'})}catch(_){}},320)});

/* ===== chart ===== */
function niceStep(raw){const p=Math.pow(10,Math.floor(Math.log10(raw)));const f=raw/p;return (f<=1?1:f<=2?2:f<=2.5?2.5:f<=5?5:10)*p}
function chart(el,o){
  const W=Math.max(260,el.clientWidth||340),H=o.h||210,m={l:40,r:12,t:12,b:26};
  const pts=o.pts||[],line=o.line||[];
  const all=pts.concat(line);
  if(!all.length){el.innerHTML='';return}
  let xs=all.map(p=>p.x),x0=Math.min(...xs),x1=Math.max(...xs);
  if(x1-x0<6){const c=(x0+x1)/2;x0=c-3;x1=c+3}
  let ys=all.map(p=>p.y);if(o.goal!=null)ys.push(o.goal);
  let y0=Math.min(...ys),y1=Math.max(...ys);if(y1-y0<(o.minSpan||1)){const c=(y0+y1)/2;y0=c-(o.minSpan||1)/2;y1=c+(o.minSpan||1)/2}
  const step=niceStep((y1-y0)/3.5);
  y0=Math.floor((y0-(y1-y0)*.06)/step)*step;y1=Math.ceil((y1+(y1-y0)*.06)/step)*step;
  const X=x=>m.l+(x-x0)/(x1-x0)*(W-m.l-m.r),Y=y=>m.t+(1-(y-y0)/(y1-y0))*(H-m.t-m.b);
  let g='';
  for(let v=y0;v<=y1+1e-9;v+=step){const yy=Y(v);g+='<line x1="'+m.l+'" x2="'+(W-m.r)+'" y1="'+yy+'" y2="'+yy+'" stroke="var(--line)" stroke-width="1"/><text x="'+(m.l-8)+'" y="'+(yy+4)+'" text-anchor="end" font-size="11" fill="var(--muted)">'+nf(v,step<1?1:0)+'</text>'}
  const xl=[[x0,'start'],[(x0+x1)/2,'middle'],[x1,'end']];
  const dstr=x=>{const d=new Date(x*864e5);return fmtShort(d.getUTCFullYear()+'-'+pad(d.getUTCMonth()+1)+'-'+pad(d.getUTCDate()))};
  xl.forEach(([x,a])=>{g+='<text x="'+(a==='start'?m.l:a==='end'?W-m.r:X(x))+'" y="'+(H-6)+'" text-anchor="'+a+'" font-size="11" fill="var(--muted)">'+dstr(Math.round(x))+'</text>'});
  if(o.goal!=null)g+='<line x1="'+m.l+'" x2="'+(W-m.r)+'" y1="'+Y(o.goal)+'" y2="'+Y(o.goal)+'" stroke="var(--muted)" stroke-width="1.5" stroke-dasharray="5 5"/><text x="'+(W-m.r)+'" y="'+(Y(o.goal)-5)+'" text-anchor="end" font-size="11" fill="var(--muted)">objectif</text>';
  const R=o.dot||3;
  if(o.lineRaw&&pts.length>1)g+='<path d="'+pts.map((p,i)=>(i?'L':'M')+X(p.x).toFixed(1)+' '+Y(p.y).toFixed(1)).join('')+'" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>';
  pts.forEach(p=>{g+='<circle cx="'+X(p.x).toFixed(1)+'" cy="'+Y(p.y).toFixed(1)+'" r="'+R+'" fill="var(--accent)" fill-opacity="'+(o.lineRaw?1:.35)+'" '+(o.lineRaw?'stroke="var(--surface)" stroke-width="2"':'')+'/>'});
  if(line.length>1)g+='<path d="'+line.map((p,i)=>(i?'L':'M')+X(p.x).toFixed(1)+' '+Y(p.y).toFixed(1)).join('')+'" fill="none" stroke="var(--accent)" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>';
  const last=(line.length?line:pts).slice(-1)[0];
  g+='<circle cx="'+X(last.x).toFixed(1)+'" cy="'+Y(last.y).toFixed(1)+'" r="5.5" fill="var(--accent)" stroke="var(--surface)" stroke-width="2.5"/>';
  g+='<g id="xh" visibility="hidden"><line y1="'+m.t+'" y2="'+(H-m.b)+'" stroke="var(--muted)" stroke-width="1"/><circle r="6" fill="var(--surface)" stroke="var(--accent)" stroke-width="3"/></g>';
  el.innerHTML='<svg viewBox="0 0 '+W+' '+H+'" role="img" aria-label="'+esc(o.label||'Graphique')+'">'+g+'<rect x="'+m.l+'" y="0" width="'+(W-m.l-m.r)+'" height="'+H+'" fill="transparent" id="hit"/></svg>';
  const svg=el.firstChild,xh=svg.querySelector('#xh'),hit=svg.querySelector('#hit');
  const src=pts.length?pts:line;
  const pick=ev=>{
    const r=svg.getBoundingClientRect(),px=(ev.clientX-r.left)/r.width*W;
    let best=null,bd=1e9;for(const p of src){const d=Math.abs(X(p.x)-px);if(d<bd){bd=d;best=p}}
    if(!best)return;
    const ref=(line.find(l=>l.x===best.x))||best;
    xh.setAttribute('visibility','visible');
    xh.firstChild.setAttribute('x1',X(best.x));xh.firstChild.setAttribute('x2',X(best.x));
    xh.lastChild.setAttribute('cx',X(best.x));xh.lastChild.setAttribute('cy',Y(best.y));
    if(o.onPick)o.onPick(best,ref);
  };
  hit.addEventListener('pointerdown',pick);hit.addEventListener('pointermove',ev=>{if(ev.buttons||ev.pointerType==='mouse')pick(ev)});
}
const xToDate=x=>{const d=new Date(x*864e5);return d.getUTCFullYear()+'-'+pad(d.getUTCMonth()+1)+'-'+pad(d.getUTCDate())};

/* ===== navigation ===== */
const TITLES={weight:'Poids',food:'Repas',gym:'Muscu',scan:'Scan'};
const VIEWS={};
let tab=S.ui&&TITLES[S.ui.tab]?S.ui.tab:'weight';
function render(){
  const app=$('#app');app.dataset.tab=tab;
  $('#title').innerHTML=esc(TITLES[tab])+'<span>.</span>';
  document.querySelectorAll('.tab').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.t===tab)));
  renderBehind();
  if(typeof syncRestBar==='function')syncRestBar();
}
function renderBehind(){const f=VIEWS[tab];if(f){const st=window.scrollY;$('#view').innerHTML=f();VIEWS[tab+'_after']&&VIEWS[tab+'_after']();}}
document.querySelector('.tabbar').addEventListener('click',e=>{
  const b=e.target.closest('.tab');if(!b)return;
  if(tab===b.dataset.t){window.scrollTo({top:0,behavior:'smooth'});return}
  tab=b.dataset.t;S.ui.tab=tab;saveLocal();closeSheet();render();window.scrollTo(0,0);
});
