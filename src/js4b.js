
/* ===== BIBLIOTHEQUE : tous les produits scannes, ranges par section et sous-section =====
   Chaque produit a une categorie « section.sous-section » (ex. vpo.poisson).
   - p.cat : choisie explicitement (par lui, ou donnee par Claude a la lecture d'une etiquette) ;
   - sinon libGuess(p) la devine d'apres le nom, la marque et les categories Open Food Facts
     (p.tags). Rien n'est enregistre dans ce cas : les produits deja scannes sont donc
     ranges tout de suite, et un meilleur classement s'applique d'un coup a tous. */
const SLIB=[
  {id:'vpo',s:'VPO',n:'Viandes, poissons, œufs',subs:[['viande','Viandes'],['charcut','Charcuteries'],['poisson','Poissons & fruits de mer'],['oeuf','Œufs']]},
  {id:'lait',s:'Laitiers',n:'Produits laitiers',subs:[['lait','Laits'],['yaourt','Yaourts & fromages blancs'],['fromage','Fromages'],['creme','Crèmes & beurres']]},
  {id:'fl',s:'Fruits & légumes',n:'Fruits & légumes',subs:[['fruits','Fruits & compotes'],['legumes','Légumes & pommes de terre'],['secs','Fruits secs & oléagineux']]},
  {id:'fec',s:'Féculents',n:'Féculents & céréales',subs:[['pain','Pains & viennoiseries'],['pates','Pâtes, riz, semoule & farine'],['cereales','Céréales du petit-déjeuner'],['legumineuses','Légumineuses & protéines végétales']]},
  {id:'sucre',s:'Sucré',n:'Produits sucrés',subs:[['biscuit','Biscuits & gâteaux'],['choco','Chocolat & confiseries'],['tartiner','Pâtes à tartiner, confitures & miel'],['dessert','Desserts & glaces'],['sucre','Sucre & sirops']]},
  {id:'gras',s:'Huiles & sauces',n:'Huiles, sauces & condiments',subs:[['huile','Huiles & vinaigres'],['sauce','Sauces & condiments']]},
  {id:'boisson',s:'Boissons',n:'Boissons',subs:[['eau','Eaux'],['jus','Jus & sodas'],['veg','Boissons végétales'],['cafe','Café, thé & boissons chaudes'],['alcool','Alcools']]},
  {id:'plat',s:'Plats',n:'Plats préparés',subs:[['plat','Plats cuisinés'],['pizza','Pizzas, quiches & tartes salées'],['sandwich','Sandwichs & burgers'],['soupe','Soupes']]},
  {id:'snack',s:'Apéritif',n:'Apéritif & en-cas',subs:[['chips','Chips & biscuits apéritif'],['barre','Barres & en-cas']]},
  {id:'sport',s:'Sport',n:'Sport & compléments',subs:[['whey','Protéines en poudre'],['boisson','Boissons protéinées'],['barre','Barres protéinées']]},
  {id:'autre',s:'Autres',n:'Autres',subs:[['autre','Non classé']]}
];
const SLIB_NAME={};SLIB.forEach(s=>s.subs.forEach(([k,n])=>{SLIB_NAME[s.id+'.'+k]=[s.n,n]}));
const libOk=c=>!!SLIB_NAME[c];

/* Regles de classement : la premiere qui correspond gagne, donc les cas precis passent avant
   les cas generaux. [categorie, mots du nom (sans accents), mots des categories Open Food Facts]. */
const SLIB_RULES=[
  ['sport.whey',/\bwhey\b|proteines? (en )?poudre|proteines? [a-z]{3,12} en poudre|poudre de proteines?|\bisolat\b|\bcaseine|protein powder|\bgainer\b/,/protein-powders|whey/],
  ['sport.boisson',/boissons? proteine|shake proteine|protein (shake|drink)|\bbcaa\b/,/protein-drinks/],
  ['sport.barre',/barres?.*protein|protein.*bar|hyperprotein/,/protein-bars/],
  ['boisson.veg',/\b(boisson|lait|drink)s? (a l |de |d |au |aux )?(avoine|amande|soja|riz|noisette|epeautre)|\bboissons? (a la |de |au )?coco/,/plant-based-milks|oat-milks|soy-milks|almond-milks|plant-based-beverages/],
  ['boisson.eau',/\beaux?\b(?! de coco)|perrier|evian|volvic|badoit|vittel|contrex|pellegrino|cristaline|hepar|salvetat|quezac/,/\bwaters\b|mineral-waters|spring-waters/],
  ['boisson.alcool',/\bbieres?\b|\bvins?\b|\bcidre|champagne|whisky|vodka|\brhum\b|\bgin\b|liqueur|aperitif/,/alcoholic-beverages|\bbeers\b|\bwines\b/],
  ['boisson.jus',/\bjus\b|\bsodas?\b|limonade|\bcola\b|^sirop\b(?! d (erable|agave))|\bsirop de\b|\bnectar|smoothie|eau de coco|boisson (gazeuse|energisante|aux fruits)|ice tea|the glace|orangina|fanta|sprite|schweppes|red bull|monster|oasis|capri sun/,/fruit-juices|\bsodas\b|carbonated-drinks|sugar-sweetened-beverages|juices-and-nectars/],
  ['boisson.cafe',/\bcafes?\b|chocolat chaud|\bthes?\b|infusion|tisane|expresso|nescafe|\bcapsules?\b/,/\bcoffees\b|\bteas\b|herbal-teas|tea-bags/],
  ['plat.pizza',/pizza|quiche|tarte sale|tourte|feuillete|flammekueche/,/pizzas|quiches|savory-pies|tarts/],
  ['fec.pain',/pains? a burger|\bbuns?\b/,/(?!)/],
  ['plat.sandwich',/sandwich|burger|kebab|panini|hot dog|bagel|tacos|croque/,/sandwiches|burgers/],
  ['plat.soupe',/\bsoupe|veloute|potage|gaspacho|bouillon/,/\bsoups\b|broths/],
  ['sucre.dessert',/\bglaces?\b|sorbet|creme glacee|cornet|esquimau|\bmousse|\bflan\b|cheesecake|tiramisu|panna cotta|\bdessert|riz au lait|creme dessert|danette|liegeois|\btarte|ile flottante|profiterole|eclair|donut/,/ice-creams|desserts|frozen-desserts|sorbets/],
  ['plat.plat',/\bpanes?\b|nuggets|cordon bleu|gratin|lasagne|hachis|brandade|ravioli|cassoulet|tajine|chili|paella|risotto|bolognaise|carbonara|choucroute|blanquette|bourguignon|parmentier|\bnems?\b|samoussa|sushi|\bmaki|poke|salade (composee|de pates|de riz|piemontaise|cesar|nicoise)|taboule|plat (cuisine|prepare)|\brepas\b|\bwok\b|\bpates (au|aux|a la)\b|\bpoelee (paysanne|campagnarde|de (poulet|boeuf|porc|crevettes))|galettes? (complete|bretonne|saucisse)|riz (cantonais|pilaf|saute)|cantonais/,/prepared-meals|ready-meals|\bmeals\b|composed-salads/],
  ['gras.huile',/^huiles?\b|\bhuiles? d(e)? ?(olive|colza|tournesol|noix|coco|sesame|argan|friture)|\bvinaigres?\b/,/\boils\b|vegetable-oils|olive-oils|vinegars/],
  ['gras.sauce',/^(sauce|coulis|ketchup|mayonnaise|moutarde|vinaigrette|pesto|bechamel|concentre|tapenade|aioli)|\b(ketchup|mayonnaise|moutarde|vinaigrette|pesto|cornichons?|epices?|assaisonnement|olives?)\b/,/\bsauces\b|condiments|dressings|\bspices\b/],
  ['snack.barre',/\bbarres? (de |aux? |a l )?(cereales|fruits|muesli|avoine|energetique|energie)|\bbarres? (cereale|fruit)/,/cereal-bars|snack-bars|granola-bars/],
  ['sucre.sucre',/^sucres?\b|sucre (en poudre|glace|roux|semoule|blanc|de canne)|sirop d (erable|agave)|\bagave\b|edulcorant|stevia/,/\bsugars\b|sweeteners/],
  ['fec.pain',/\bpains?\b|baguette|brioche|croissant|viennoiserie|biscottes?|\btoasts?\b|\bwraps?\b|tortilla|galettes? de ble|galettes? de riz|\bpita\b|fajita|chapelure|pain au lait|petit pain/,/\bbreads\b|viennoiseries|rusks|flatbreads|wraps/],
  ['fec.cereales',/muesli|granola|corn flakes|cereales|flocons d avoine|\bavoine\b|porridge|petales|chocapic|special k|weetabix|cheerios|tresor/,/breakfast-cereals|\bmuesli/],
  ['sucre.tartiner',/pates? a tartiner|nutella|confiture|\bgelee\b|\bmiel\b|puree (de |d )(cacahuete|amande|noisette|sesame)|beurre (de |d )(cacahuete|amande|noisette)|tahin|sirop d erable|creme de marron|pate de (speculoos|noisette)/,/spreads|jams|honeys|sweet-spreads|chocolate-spreads|peanut-butters/],
  ['sucre.choco',/chocolat|\bcacao|bonbon|confiserie|caramel|snickers|\bmars\b|twix|bounty|kinder|nougat|praline|dragee|haribo|guimauve|chewing|pastille|sucette|\bbarre (chocolat|au chocolat)/,/chocolates|candies|confectioneries|cocoa/],
  ['sucre.biscuit',/\bcrepes?\b|pancakes?|gaufres?|waffles?|beignets?|biscuit|gateau|cookie|madeleine|gaufrette|\bcakes?\b|muffin|palmier|sable|speculoos|petit beurre|oreo|brownie|financier|galette des rois|pain d epices|\bbarre patissiere/,/\bbiscuits\b|\bcakes\b|cookies|sweet-snacks|pastries/],
  ['snack.chips',/\bchips\b|tortilla chips|bretzel|crackers?|pop ?corn|souffle|biscuits? aperitif|bugles|curly|vache sauvage|\bpringles|doritos|monster munch/,/chips-and-fries|crisps|salty-snacks|appetizers|crackers/],
  ['snack.barre',/\bbarres?\b|en cas|snack bar/,/cereal-bars|snack-bars|granola-bars/],
  ['fl.secs',/amandes?|\bnoix\b(?! de saint)|noisettes?|cajou|pistaches?|cacahuetes?|\bpecan|raisins? secs?|dattes?|abricots? secs?|pruneaux?|figues? seches?|fruits? secs?|oleagineux|melange (aperitif|de fruits)|cranberr|graines|\bchia\b|sesame|tournesol/,/\bnuts\b|dried-fruits|\bseeds\b|oilseeds|dried-products/],
  ['vpo.charcut',/jambon|saucisson|saucisses?|lardons?|bacon|chorizo|\bpate (de|en)\b|rillettes|terrine|mortadelle|coppa|rosette|bresaola|grisons|knack|merguez|chipolata|boudin|andouille|salami|speck|poitrine (fumee|salee)|\bfoie gras|cervelas|(poulet|dinde) en tranches|tranches? de (poulet|dinde)|\bhot dogs?\b/,/charcuteries|delicatessen|\bhams\b|sausages|cured-meats|cooked-hams|bacons|pates/],
  ['vpo.poisson',/saumon|\bthon\b|cabillaud|colin\b|merlu|sardines?|maquereau|truite|crevettes?|surimi|poissons?|\bcrabes?\b|\bmoules?\b|calamars?|haddock|\blieu\b|dorade|\bbar\b|harengs?|anchois|saint jacques|fruits de mer|langoustines?|\bhuitres?|\bflet\b|\bsole\b|\braie\b|\blotte\b|\bmorue\b|\btarama\b/,/\bfishes\b|seafood|fish-and-seafood|\bfish\b|crustaceans|molluscs/],
  ['vpo.oeuf',/^(\d+ )?(gros |petits )?oeufs?\b|\boeufs? (plein air|bio|frais|durs?|de poule|de caille)|\bomelette|\b(blanc|jaune)s? d oeufs?/,/\beggs\b|\bhen-eggs\b/],
  ['vpo.viande',/boeuf|\bveau\b|\bporc\b|agneau|poulet|dinde|canard|lapin|steaks?|\bhache|escalope|\bcotes?\b|\broti|viande|gigot|cuisses?|filet mignon|magret|\bsaute\b|paleron|bavette|entrecote|volaille|pintade|\bblanc de|\bfilet de (poulet|dinde)|\bsteak\b|cheval|rosbif/,/\bmeats\b|poultries|\bbeef\b|\bpork\b|chicken|turkey|\blambs?\b|\bveal\b|ducks?/],
  ['lait.yaourt',/yaourt|yogourt|yoghourt|skyr|fromage blanc|faisselle|petits? suisses?|kefir|\byop\b|activia|fromage frais|\bgrec\b|cottage/,/yogurts|fermented-milk|fresh-cheeses|fermented-dairy|dairy-desserts/],
  ['lait.fromage',/fromages?|camembert|emmental|\bcomte\b|mozzarella|parmesan|\bbrie\b|chevre|\bfeta\b|roquefort|raclette|gouda|\bedam\b|cheddar|reblochon|boursin|vache qui rit|babybel|gruyere|cantal|munster|maroilles|ricotta|mascarpone|burrata|st moret|philadelphia|\bfourme|bleu d auvergne|\bkiri\b/,/\bcheeses\b/],
  ['lait.creme',/creme (fraiche|liquide|legere|entiere|epaisse|a fouetter|de cuisine)|\bbeurre\b|margarine|chantilly|\bcrema\b|lait de coco|creme de coco/,/\bcreams\b|\bbutters\b|margarines|dairy-spreads/],
  ['lait.lait',/\blait\b|lait (demi|ecreme|entier)|boisson lactee|milkshake|\blactel\b|candia/,/\bmilks\b|dairy-drinks|\bmilk\b/],
  ['fec.legumineuses',/lentilles?|pois chiches?|haricots? (rouges?|blancs?|secs?|noirs?)|\bfeves?\b|flageolets?|\btofu\b|tempeh|seitan|soja textur|houmous|hummus|falafel|steaks? (vegetal|de soja)|edamame|pois casses|proteines? vegetales?/,/\bpulses\b|\btofu\b|meat-alternatives|vegetarian-meat/],
  ['fec.pates',/\bpates\b|spaghetti|tagliatelles?|penne|fusilli|macaroni|coquillettes?|\briz\b|semoule|couscous|boulgour|quinoa|nouilles?|vermicelles?|gnocchi|polenta|\bble\b|farfalle|torti|lasagnes? (seches?|a cuire)|\bfarine/,/\bpastas\b|\brices\b|cereal-grains|semolina|noodles|\bflours\b/],
  ['fl.legumes',/legumes?|haricots? verts?|carottes?|tomates?|courgettes?|epinards?|brocolis?|\bchou|petits pois|\bmais\b|poireaux?|champignons?|\bsalade\b(?! de fruits)|ratatouille|aubergines?|poivrons?|pommes? de terre|puree|\bfrites?\b|\bail\b|oignons?|avocats?|concombres?|betteraves?|potiron|courge|celeri|navet|endives?|radis|artichaut|asperges?|\bpoelee|roquette|fenouil|germes?|mache|laitue|cresson|patates?/,/\bvegetables\b|vegetables-based|potatoes|tomatoes|mushrooms|salads/],
  ['fl.fruits',/\bpommes?\b|\bmures?\b|poires?|bananes?|oranges?|fraises?|framboises?|myrtilles?|peches?|abricots?|cerises?|raisins?|mangues?|ananas|kiwis?|citrons?|\bfruits?\b|compotes?|pamplemousse|clementines?|mirabelles?|prunes?|figues?|melon|pasteque|litchi|grenade/,/\bfruits\b|compotes|fruit-based|fruits-and-vegetables-based/]
];
function libGuess(p){
  if(p.cat&&libOk(p.cat))return p.cat;
  const name=normTxt((p.name||'')+' '+(p.brand||''));
  const tags=(p.tags||[]).map(t=>String(t).replace(/^[a-z]{2}:/,'').toLowerCase()).join(' ');
  for(const [k,rn,rt] of SLIB_RULES){if(rn.test(name)||(tags&&rt.test(tags)))return k}
  return 'autre.autre';
}
/* Demande a Claude (version artefact) de ranger lui-meme le produit qu'il lit sur une etiquette. */
const libPrompt=()=>`\nAjoute aussi la clé "category" : un identifiant choisi UNIQUEMENT dans cette liste (section.sous-section), le plus adapté au produit : ${Object.keys(SLIB_NAME).filter(k=>k!=='autre.autre').join(', ')}, ou "autre.autre" si rien ne convient.`;

/* ---- vue ---- */
let scanSub='scan',libQ='',libOpen=new Set();
const SCAN_SUBS=[['scan','Scanner'],['lib','Bibliothèque']];
const scanSeg=()=>'<div class="seg" role="tablist">'+SCAN_SUBS.map(([k,n])=>`<button role="tab" data-act="scan-sub" data-s="${k}" aria-selected="${scanSub===k}">${n}${k==='lib'&&S.scans.length?` <span class="small" style="opacity:.7">${libDistinct()}</span>`:''}</button>`).join('')+'</div>';
A['scan-sub']=b=>{scanSub=b.dataset.s;render();window.scrollTo(0,0)};
A['lib-go']=()=>{scanSub='lib';render();window.scrollTo(0,0)};

/* Un meme produit scanne sous plusieurs marques ne compte qu'une fois : meme rangement, memes
   apports (calories, proteines, glucides, lipides) et noms proches (hors marque).
   Rien n'est supprime dans l'etat : c'est un regroupement a l'affichage. */
const LIB_STOP=new Set(['des','les','aux','avec','sans','pour','sur','par','bio','extra','nature']);
const libSig=p=>{const q=p.per||{};return Math.round(q.kcal||0)+'|'+['prot','carbs','fat'].map(k=>Math.round((q[k]||0)*10)/10).join('|')};
const libEmpty=p=>{const q=p.per||{};return !(q.kcal||q.prot||q.carbs||q.fat)};
function libWords(p){
  const brand=normTxt(p.brand||'').split(/\s+/);
  return new Set(normTxt(p.name||'').split(/\s+/).filter(w=>w.length>2&&!LIB_STOP.has(w)&&!brand.includes(w)).map(w=>w.replace(/[sx]$/,'')));
}
function libSame(a,b){
  if(a.sig!==b.sig||a.empty)return false;
  const A_=a.words,B_=b.words,m=Math.min(A_.size,B_.size);
  if(!m)return false;
  let n=0;A_.forEach(w=>{if(B_.has(w))n++});
  return n/m>=0.6;
}
/* -> { 'vpo.charcut': [ {p: fiche representative (la plus recente), all: [fiches]} ... ] } */
function libBuild(list){
  const out={};
  for(const p of list){
    const cat=libGuess(p),g=out[cat]=out[cat]||[];
    const x={p,all:[p],sig:libSig(p),words:libWords(p),empty:libEmpty(p)};
    const hit=g.find(y=>libSame(y,x));
    if(hit)hit.all.push(p);else g.push(x);
  }
  for(const k in out)out[k].sort((a,b)=>a.p.name.localeCompare(b.p.name,'fr'));
  return out;
}
function libGroups(){
  const q=normTxt(libQ).trim();
  const g=libBuild(S.scans);
  if(!q)return g;
  for(const k in g){g[k]=g[k].filter(x=>x.all.some(p=>normTxt(p.name+' '+(p.brand||'')).includes(q)));if(!g[k].length)delete g[k]}
  return g;
}
const libGroupOf=p=>{const g=libBuild(S.scans)[libGuess(p)]||[];return g.find(x=>x.all.some(y=>y.id===p.id))||{p,all:[p]}};
const libDistinct=()=>Object.values(libBuild(S.scans)).reduce((a,l)=>a+l.length,0);
function libRow(x){
  const p=x.p,e=evalProduct(p),brands=[...new Set(x.all.map(y=>(y.brand||'').trim()).filter(Boolean))];
  return `<button class="li" data-act="lib-open" data-id="${p.id}"><span class="badge num" style="width:40px;height:40px;font-size:16px;background:${e.color}">${e.score}</span><div class="grow"><div class="t">${esc(p.name)}${x.all.length>1?` <span class="pill neutral" style="margin-left:4px">×${x.all.length}</span>`:''}</div><div class="small muted">${esc(brands.join(' · '))}${brands.length?' · ':''}${nf(p.per.kcal,0)} kcal / 100 g</div></div>${ICON.chev}</button>`;
}
function libSections(){
  const g=libGroups(),searching=!!libQ.trim();
  const out=SLIB.map(s=>{
    const subs=s.subs.map(([k,n])=>[k,n,g[s.id+'.'+k]||[]]).filter(x=>x[2].length);
    const total=subs.reduce((a,x)=>a+x[2].length,0);
    if(searching&&!total)return '';
    const open=total&&(searching||libOpen.has(s.id));
    return `<div class="libsec${total?'':' libempty'}"><button class="libh" data-act="lib-sec" data-s="${s.id}" aria-expanded="${!!open}" ${total?'':'disabled'}><span class="grow">${esc(s.n)}</span><span class="pill neutral">${total}</span><span class="libchev">${ICON.chev}</span></button>${open?`<div class="libbody">${subs.map(([k,n,list])=>`<div class="sec libsub">${esc(n)} <span class="muted">· ${list.length}</span></div><div class="list">${list.map(libRow).join('')}</div>`).join('')}</div>`:''}</div>`;
  }).join('');
  return out||'<div class="empty">Aucun produit ne correspond.</div>';
}
function libView(){
  const n=S.scans.length;
  if(!n)return scanSeg()+'<div class="card empty"><b>Ta bibliothèque est vide.</b><br>Chaque produit que tu scannes ou analyses est rangé ici automatiquement, par section et sous-section.</div>';
  return scanSeg()+`<div class="card"><div class="field" style="margin-bottom:10px"><input class="inp" type="search" id="libq" data-in="libq" placeholder="Chercher un produit…" value="${esc(libQ)}" aria-label="Chercher dans la bibliothèque" autocomplete="off"></div>
  <div class="row" style="justify-content:space-between"><span class="muted small" id="libcount">${libCount()}</span><button class="btn ghost" style="min-height:44px" data-act="lib-all">${libOpen.size?'Tout fermer':'Tout ouvrir'}</button></div></div>
  <div class="card libcard" id="libres">${libSections()}</div>`;
}
function libCount(){
  const g=libGroups(),n=Object.values(g).reduce((a,l)=>a+l.length,0),sec=SLIB.filter(s=>s.subs.some(([k])=>(g[s.id+'.'+k]||[]).length)).length;
  return n+' produit'+(n>1?'s':'')+' · '+sec+' section'+(sec>1?'s':'');
}
function libRefresh(){const r=$('#libres');if(r)r.innerHTML=libSections();const c=$('#libcount');if(c)c.textContent=libCount()}
I.libq=t=>{libQ=t.value;libRefresh()};
A['lib-sec']=b=>{const s=b.dataset.s;libOpen.has(s)?libOpen.delete(s):libOpen.add(s);render()};
A['lib-all']=()=>{if(libOpen.size)libOpen.clear();else{const g=libGroups();SLIB.forEach(s=>{if(s.subs.some(([k])=>(g[s.id+'.'+k]||[]).length))libOpen.add(s.id)})}render()};

/* ---- fiche d'un produit de la bibliotheque (feuille) + rangement ---- */
function libMove(p){
  const cur=libGuess(p);
  return `<div class="card" style="margin-top:12px"><label class="sec" for="libset" style="display:block">Rangé dans</label><select class="inp" id="libset" data-ch="lib-set" data-id="${p.id}">${SLIB.map(s=>`<optgroup label="${esc(s.n)}">${s.subs.map(([k,n])=>`<option value="${s.id}.${k}" ${s.id+'.'+k===cur?'selected':''}>${esc(n)}</option>`).join('')}</optgroup>`).join('')}</select>${p.cat?'':'<div class="small muted" style="margin-top:8px">Classement automatique : change-le si ce n’est pas le bon.</div>'}</div>`;
}
I['lib-set']=t=>{
  const p=S.scans.find(x=>x.id===t.dataset.id);if(!p||!libOk(t.value))return;
  libGroupOf(p).all.forEach(y=>{y.cat=t.value});   /* tout le groupe suit : meme produit, meme rangement */
  persist('scans');
  toast('Rangé : '+SLIB_NAME[t.value][1]);render();
};
A['lib-open']=b=>{
  const p=S.scans.find(x=>x.id===b.dataset.id);if(!p)return;
  const x=libGroupOf(p),n=x.all.length;
  const others=n>1?`<div class="card" style="margin-top:12px"><div class="sec">Même produit, ${n} fiches</div><div class="small muted" style="margin-bottom:6px">Mêmes apports : elles sont regroupées ici pour éviter les doublons.</div>${x.all.map(y=>`<div class="nrow"><span style="flex:1;min-width:0;overflow-wrap:anywhere">${esc(y.name)}${y.brand?' · '+esc(y.brand):''}</span><span class="small muted">${esc(fmtShort(y.date))}</span></div>`).join('')}</div>`:'';
  openSheet(`<div class="sc">${libMove(p).replace('margin-top:12px','margin-top:0')}${resultCard(p)}${others}<button class="btn danger block" style="margin-top:12px" data-act="lib-del" data-id="${p.id}">${n>1?'Retirer ces '+n+' fiches':'Retirer de la bibliothèque'}</button></div>`);
};
A['lib-del']=b=>{
  const p=S.scans.find(x=>x.id===b.dataset.id);if(!p)return;
  const x=libGroupOf(p),ids=new Set(x.all.map(y=>y.id));
  confirmSheet(ids.size>1?'Retirer ces '+ids.size+' fiches ?':'Retirer ce produit ?',p.name+(ids.size>1?' (même produit, plusieurs marques) ne sera plus':' ne sera plus')+' dans ta bibliothèque. Les repas déjà saisis ne changent pas.','Retirer',()=>{
    S.scans=S.scans.filter(y=>!ids.has(y.id));persist('scans');
    if(scanCur&&ids.has(scanCur.id))scanCur=null;
    toast('Retiré');render();
  });
};
