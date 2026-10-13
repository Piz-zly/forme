/* ===== ACTIVITÉ DU JOUR : pas, dépense, apport ===== */
const actOf=d=>S.act[d]||{s:0,k:0};
function setAct(d,s,k){
  if(!s&&!k)delete S.act[d];else S.act[d]={s:Math.round(s)||0,k:Math.round(k)||0};
  persist('act');
}
const eatenOn=d=>Math.round(totals(dayEntries(d)).kcal);
function actCard(){
  const d=actDate||today(),a=actOf(d),eaten=eatenOn(d),goalS=S.settings.steps||10000;
  const bal=a.k-eaten,hasK=a.k>0,hasE=eaten>0;
  const days=[];for(let i=6;i>=0;i--)days.push(addDays(d,-i));
  const mx=Math.max(goalS,...days.map(x=>actOf(x).s))||1;
  const bars=days.map(x=>{
    const v=actOf(x).s,h=Math.max(v?6:2,Math.round(v/mx*52));
    return `<div class="abar"><i style="height:${h}px;background:${v?'var(--accent)':'var(--line)'}"></i><span>${parseD(x).toLocaleDateString('fr-FR',{weekday:'narrow'})}</span></div>`;
  }).join('');
  const sPct=clamp(a.s/goalS*100,0,100);
  const full=hasK&&hasE;
  const balTxt=full?`<div style="text-align:right;white-space:nowrap"><div class="small muted">Balance</div><b class="num" style="font:800 20px/1.1 var(--font-display)">${bal>0?'−':bal<0?'+':''}${nf(Math.abs(bal),0)} kcal</b></div>`:'';
  const balHint=full?`<div class="small muted" style="margin-top:10px">${bal>0?'Tu as dépensé '+nf(bal,0)+' kcal de plus que ce que tu as mangé.':bal<0?'Tu as mangé '+nf(-bal,0)+' kcal de plus que ta dépense affichée.':'Apport et dépense à l’équilibre.'}</div>`
    :`<div class="small muted" style="margin-top:10px">${hasK?'Note tes repas dans l’onglet Repas pour voir la balance du jour.':'Saisis ta dépense pour voir la balance du jour.'}</div>`;
  return `<div class="card">
  <div class="row sb" style="margin-bottom:12px"><h2 style="margin:0">Journée</h2>
    <label class="chip" style="position:relative">${d===today()?'Aujourd’hui':esc(fmtShort(d))}
      <input type="date" data-ch="actdate" value="${d}" max="${today()}" aria-label="Jour affiché" style="position:absolute;inset:0;opacity:0;width:100%;height:100%">
    </label></div>
  <button class="actgrid" data-act="act-edit" aria-label="Modifier les pas et la dépense du jour">
    <div class="stat"><span>Pas</span><b>${a.s?nf(a.s,0):'—'}</b><span>sur ${nf(goalS,0)}</span></div>
    <div class="stat"><span>Dépensées</span><b>${hasK?nf(a.k,0):'—'}</b><span>kcal</span></div>
    <div class="stat"><span>Mangées</span><b>${hasE?nf(eaten,0):'—'}</b><span>kcal</span></div>
  </button>
  <div class="bar" style="margin:12px 0 4px"><i style="width:${sPct}%"></i></div>
  <div class="small muted" style="margin-bottom:14px">${a.s?nf(sPct,0)+' % de ton objectif de pas':'Saisis tes pas depuis Step Counter Pedometer.'}</div>
  <div class="row sb" style="align-items:flex-end;gap:12px;margin-bottom:14px"><div class="abars">${bars}</div>${balTxt}</div>
  <button class="btn soft block" data-act="act-edit">${a.s||a.k?'Modifier la journée':'Saisir mes pas'}</button>
  ${balHint}</div>`;
}
let actDate=null;
I.actdate=t=>{actDate=t.value||today();render()};
A['act-edit']=()=>{
  const d=actDate||today(),a=actOf(d);
  openSheet(`<h3>Journée du ${esc(fmtShort(d))}</h3>
  <div class="field"><label for="apas">Pas (Step Counter Pedometer)</label><input class="inp" id="apas" inputmode="numeric" value="${a.s||''}" placeholder="Ex : 8 400"></div>
  <div class="field"><label for="akcal">Calories dépensées (kcal)</label><input class="inp" id="akcal" inputmode="numeric" value="${a.k||''}" placeholder="Ex : 2 450"></div>
  <div class="small muted" style="margin:-4px 0 14px">Recopie les deux chiffres affichés par ton application de podomètre pour ce jour.</div>
  <button class="btn block" data-act="act-save" data-d="${d}">Enregistrer</button>
  ${a.s||a.k?'<button class="btn ghost block" style="margin-top:10px" data-act="act-clear" data-d="'+d+'">Effacer la journée</button>':''}`);
};
A['act-save']=b=>{setAct(b.dataset.d,num($('#apas').value),num($('#akcal').value));closeSheet();render();toast('Journée enregistrée')};
A['act-clear']=b=>{setAct(b.dataset.d,0,0);closeSheet();render()};

