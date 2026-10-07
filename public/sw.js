self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open('inversioncore-v1').then((cache) => {
      return cache.addAll(['/', '/llms.txt', '/manifest.webmanifest', '/offline.html']);
    })
  );
});

self.addEventListener('fetch', (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request).catch(() => caches.match('/offline.html'));
    })
  );
});
