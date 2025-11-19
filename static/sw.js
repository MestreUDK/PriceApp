// static/sw.js
const CACHE_NAME = 'priceapp-cache-v9';
const urlsToCache = [
  '/',
  '/registrar-preco',
  '/produtos',
  '/mercados',
  '/leitor-offline' 
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(networkResponse => {
        if (networkResponse && networkResponse.status === 200) {
          const responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
        }
        return networkResponse;
      })
      .catch(() => {
        console.log('Rede falhou, buscando do cache:', event.request.url);
        return caches.match(event.request);
      })
  );
});
