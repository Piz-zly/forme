/* Forme : fonctionne hors ligne. Changer VERSION force la mise à jour chez tout le monde. */
const VERSION='forme-2026.10.08-8';
const SHELL=['./','index.html','manifest.webmanifest','icons/icon-192.png','icons/icon-512.png','vendor/zxing.min.js'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(VERSION).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==VERSION).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request,u=new URL(r.url);
  if(r.method!=='GET')return;
  if(u.origin!==location.origin&&!/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname))return; /* Open Food Facts : toujours en direct */
  const page=r.mode==='navigate';
  e.respondWith(
    page?fetch(r).then(x=>{const c=x.clone();caches.open(VERSION).then(k=>k.put('index.html',c));return x}).catch(()=>caches.match('index.html'))
    :caches.match(r).then(h=>h||fetch(r).then(x=>{if(x.ok){const c=x.clone();caches.open(VERSION).then(k=>k.put(r,c))}return x}))
  );
});
