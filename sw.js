const C = 'notes-v1', F = ['./', 'index.html', 'style.css', 'app.js', 'firebase-config.js', 'manifest.webmanifest'];
self.addEventListener('install', e => e.waitUntil(caches.open(C).then(c => c.addAll(F))));
self.addEventListener('fetch', e => {
  if (e.request.url.includes('gstatic') || e.request.url.includes('googleapis')) return;
  e.respondWith(fetch(e.request).catch(() => caches.match(e.request)));
});
