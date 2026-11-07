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
