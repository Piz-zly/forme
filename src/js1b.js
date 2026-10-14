/* ===== ANIMATIONS DOUCES : outil maison (remplace AutoAnimate, non retenu) =====
   L'appli redessine l'écran entier à chaque action (render). Cet outil s'intercale autour :
   juste avant, il note la place des lignes marquées ; juste après, il fait glisser celles qui ont
   bougé, apparaître les nouvelles, et s'effacer (150 ms) une copie inerte de celles qui ont disparu.
   - Apparence seulement (opacité, déplacement) : jamais le contenu, jamais les données. Les données
     sont déjà enregistrées et l'écran déjà redessiné quand l'animation commence.
   - Marquage : un conteneur data-ag="portée:nom" et, dans ce conteneur, des lignes data-ak="clé"
     (clé unique dans l'écran). Rien ne s'anime si la portée n'existait pas juste avant (changement
     d'onglet, de jour…), au-delà de ANIM_MAX lignes, ou si le téléphone demande de réduire les animations.
   - En cas d'erreur, ou sans Web Animations, l'appli marche exactement comme avant.
   Endroits marqués : journal du Repas (js2.js), pesées (js2.js), routine (js3b.js), bibliothèque du Scan
   hors recherche (js4b.js). Pour retirer l'outil : enlever ce fichier de build.sh (les marques restent inertes). */
const ANIM_MAX=60,ANIM_MS=200,ANIM_OUT=150;
const animOff=()=>!Element.prototype.animate||!window.matchMedia||matchMedia('(prefers-reduced-motion: reduce)').matches;
const animScope=g=>g.slice(0,g.lastIndexOf(':'));
const animRows=()=>[...document.querySelectorAll('#view [data-ag]>[data-ak]')];
function animSnap(){
  if(animOff())return null;
  const els=animRows();
  if(els.length>ANIM_MAX)return null;
  /* une portée vide compte aussi (historique du Poids replié) : ses lignes pourront apparaître en douceur */
  const m=new Map(),scopes=new Set([...document.querySelectorAll('#view [data-ag]')].map(c=>animScope(c.dataset.ag)));
  if(!scopes.size)return null;
  for(const el of els){
    const c=el.parentElement,g=c.dataset.ag,sib=[...c.children],i=sib.indexOf(el);
    let prev=null,next=null;
    for(let j=i-1;j>=0&&!prev;j--)prev=sib[j].dataset.ak||null;
    for(let j=i+1;j<sib.length&&!next;j++)next=sib[j].dataset.ak||null;
    scopes.add(animScope(g));
    m.set(el.dataset.ak,{el,g,i,prev,next,r:el.getBoundingClientRect()});
  }
  return {m,scopes};
}
/* copie inerte de la ligne disparue, remise à sa place et repliée : aucun clic, aucune donnée */
function animGhost(o){
  const c=[...document.querySelectorAll('#view [data-ag]')].find(x=>x.dataset.ag===o.g);if(!c)return;
  const gh=o.el;
  gh.removeAttribute('data-ak');
  [gh,...gh.querySelectorAll('[data-act],[data-in],[data-ch],[id]')].forEach(x=>{x.removeAttribute('data-act');x.removeAttribute('data-in');x.removeAttribute('data-ch');x.removeAttribute('id')});
  gh.setAttribute('aria-hidden','true');gh.inert=true;gh.style.pointerEvents='none';gh.style.overflow='hidden';
  const by=k=>k&&[...c.children].find(x=>x.dataset.ak===k);
  const n=by(o.next),p=by(o.prev);
  if(n)c.insertBefore(gh,n);else if(p)p.after(gh);else c.insertBefore(gh,c.children[o.i]||null);
  const end=()=>gh.remove();
  const a=gh.animate([{opacity:1,height:o.r.height+'px'},{opacity:0,height:'0px',marginTop:'0px',marginBottom:'0px',paddingTop:'0px',paddingBottom:'0px'}],{duration:ANIM_OUT,easing:'ease-in'});
  a.onfinish=end;a.oncancel=end;setTimeout(end,ANIM_OUT+120);
}
function animPlay(s){
  if(!s)return;
  const els=animRows();
  if(els.length>ANIM_MAX)return;
  const keys=new Set(els.map(e=>e.dataset.ak));
  /* d'abord les lignes disparues : leur copie garde la place, les suivantes remontent en douceur */
  s.m.forEach((o,k)=>{if(!keys.has(k)&&s.scopes.has(animScope(o.g)))animGhost(o)});
  for(const el of els){
    if(!s.scopes.has(animScope(el.parentElement.dataset.ag)))continue;
    const o=s.m.get(el.dataset.ak);
    if(o){
      const r=el.getBoundingClientRect(),dx=o.r.left-r.left,dy=o.r.top-r.top;
      if(Math.abs(dx)>1||Math.abs(dy)>1)el.animate([{transform:`translate(${dx}px,${dy}px)`},{transform:'none'}],{duration:ANIM_MS,easing:'ease-out'});
    }else el.animate([{opacity:0,transform:'translateY(6px)'},{opacity:1,transform:'none'}],{duration:ANIM_MS,easing:'ease-out'});
  }
}
/* branchement autour du dessin : le dessin a toujours lieu, l'animation est un bonus */
{
  const draw=renderBehind;
  renderBehind=function(){
    let s=null;try{s=animSnap()}catch(e){s=null}
    draw();
    try{animPlay(s)}catch(e){}
  };
}
