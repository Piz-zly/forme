/* ===== FLUIDITÉ (2026.11.07-4) : écran mis à jour sans tout refaire, geste Retour, vibrations, glissements au doigt ===== */

/* Remplace le contenu de el par html en gardant les éléments déjà là (Idiomorph, vendor/idiomorph.min.js, 0BSD) : le champ
   en cours de saisie garde focus, curseur, valeur et clavier ; la page ne saute pas. Les lignes data-ak (js1b.js) sont
   appariées par leur clé grâce à un id provisoire, pour que l'animation retrouve les mêmes lignes. Sans Idiomorph ou en
   cas d'erreur : innerHTML, comme avant. */
function morphIn(el,html){
  if(!window.Idiomorph){el.innerHTML=html;return}
  try{
    const t=document.createElement('template');t.innerHTML=html;
    [el,t.content].forEach(r=>r.querySelectorAll('[data-ak]:not([id])').forEach(x=>x.id='ak-'+x.dataset.ak));
    /* seul un champ de saisie actif est laissé tel quel ; un bouton qui vient d'être touché garde le focus mais doit changer */
    const typing=!!document.activeElement&&document.activeElement.matches('input,textarea,select');
    Idiomorph.morph(el,[...t.content.childNodes],{morphStyle:'innerHTML',ignoreActiveValue:typing});
    el.querySelectorAll('[data-ak][id^="ak-"]').forEach(x=>x.removeAttribute('id'));
  }catch(e){el.innerHTML=html}
}

/* geste Retour d'Android : ferme la feuille ouverte, sinon ramène un sous-onglet du Repas au Journal ; sinon rien n'est
   retenu et l'appli peut se fermer. CloseWatcher si Chrome le connaît, sinon une seule entrée d'historique à la fois
   (window.history : « history » est aussi une fonction de js3.js ; jamais de boucle : chaque entrée ajoutée attend un vrai Retour, ou est retirée dès que l'écran n'en a plus besoin). */
let backW=null,backPushed=false,backSkip=false;
const backWant=()=>sheetOpen()||(tab==='food'&&foodSub!=='journal');
function backDo(){
  if(sheetOpen())closeSheet();
  else if(tab==='food'&&foodSub!=='journal'){foodSub='journal';render()}
  else backSync();
}
function backSync(){
  const w=backWant();
  if(window.CloseWatcher){
    if(w&&!backW){try{backW=new CloseWatcher();backW.onclose=()=>{backW=null;backDo()}}catch(e){backW=null}}
    else if(!w&&backW){const x=backW;backW=null;x.destroy()}
    return;
  }
  if(w&&!backPushed){try{window.history.pushState({forme:1},'');backPushed=true}catch(e){}}
  else if(!w&&backPushed){backPushed=false;backSkip=true;window.history.back()}
}
addEventListener('popstate',()=>{if(backSkip){backSkip=false;return}if(backPushed){backPushed=false;backDo()}});

/* vibrations courtes. Durées reprises des motifs de web-haptics (github.com/lochie/web-haptics, MIT), sans leur modulation
   d'intensité : leger = light, succes = success, fort = nudge, avert = warning. repos = fin du repos (motif d'origine). */
const HAPTIC={leger:[15],succes:[30,60,40],fort:[80,80,50],avert:[40,100,40],repos:[200,90,200]};
function haptic(t){if(S.settings.vibre===false||!navigator.vibrate)return;try{navigator.vibrate(HAPTIC[t]||HAPTIC.leger)}catch(e){}}

/* petite suppression déjà faite : « Supprimé · Annuler » pendant 5 s ; back() remet exactement ce qui a été retiré */
function undoable(back){haptic('avert');toast('Supprimé',{label:'Annuler',fn:()=>{back();render()}})}

/* glissements au doigt : TinyGesture (vendor/tinygesture.js, Apache-2.0). Journal du Repas : balayer change de jour ;
   ligne du journal tirée à gauche : bouton « Supprimer ». Feuille tirée vers le bas (poignée, ou contenu en haut) : fermée.
   Jamais sur un champ, le graphique ou une zone qui défile à l'horizontale ; pas de balayage pendant une séance.
   Avec moins d'animations, rien ne suit le doigt : seule l'action a lieu. */
const motionOff=()=>matchMedia('(prefers-reduced-motion: reduce)').matches;
function noSwipe(t){
  if(!t||!t.closest||t.closest('input,textarea,select,#wchart,#gchart,.toast'))return true;
  for(let e=t;e&&e!==document.body;e=e.parentElement)
    if(e.scrollWidth>e.clientWidth+2&&/auto|scroll/.test(getComputedStyle(e).overflowX))return true;
  return false;
}
function closeSwiped(keep){
  document.querySelectorAll('#view .entry.swiped').forEach(r=>{if(r!==keep){r.style.transform='';r.classList.remove('swiped')}});
  document.querySelectorAll('#view .swdel').forEach(b=>b.remove());
}
function openSwiped(row){
  row.classList.add('swiped');row.style.transform='translateX(-104px)';
  const p=row.parentElement;if(getComputedStyle(p).position==='static')p.style.position='relative';
  const b=document.createElement('button');b.className='swdel';b.dataset.act='f-del';b.dataset.id=row.dataset.id;b.textContent='Supprimer';
  b.style.top=row.offsetTop+'px';b.style.height=row.offsetHeight+'px';row.after(b);
}
if(typeof TinyGesture==='function'){
  const journal=()=>tab==='food'&&foodSub==='journal'&&!S.active;
  const V=new TinyGesture($('#view'),{mouseSupport:false});
  let start=null,row=null,onRow=false;
  V.on('panstart',e=>{
    start=noSwipe(e.target)?null:e.target;
    row=start&&journal()?start.closest('.entry[data-act="f-edit"]'):null;onRow=!!row;
    closeSwiped(row);
  });
  V.on('panmove',()=>{if(row&&/horizontal/.test(V.swipingDirection||'')&&!motionOff()){row.style.transition='none';row.style.transform='translateX('+Math.max(-140,Math.min(0,V.touchMoveX))+'px)'}});
  V.on('panend',()=>{
    if(!row)return;
    row.style.transition='';
    if(/horizontal/.test(V.swipingDirection||'')&&V.touchEndX-V.touchStartX<-50)openSwiped(row);else row.style.transform='';
    row=null;
  });
  V.on('swipeleft',()=>{if(start&&!onRow&&journal())dayMove(1)});
  V.on('swiperight',()=>{if(start&&!onRow&&journal())dayMove(-1)});

  const L=new TinyGesture($('#layer'),{mouseSupport:false});
  let sh=null;
  L.on('panstart',e=>{
    const s=$('#layer .sheet');
    sh=s&&s.contains(e.target)&&!e.target.closest('input,textarea,select')&&(e.target.closest('.grab')||s.scrollTop<=0)?s:null;
  });
  L.on('panmove',()=>{
    if(!sh||motionOff()||/horizontal/.test(L.swipingDirection||''))return;
    sh.style.transition='none';sh.style.transform='translateY('+Math.max(0,L.touchMoveY)+'px)';
  });
  L.on('panend',()=>{
    if(!sh)return;
    const s=sh,y=L.touchEndY-L.touchStartY;sh=null;
    if(y>110&&y>Math.abs(L.touchEndX-L.touchStartX))closeSheet();
    else{s.style.transition='transform .2s ease-out';s.style.transform=''}
  });
}
