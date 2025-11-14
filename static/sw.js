// static/sw.js
// Define um nome e versão para o cache
const CACHE_NAME = 'priceapp-cache-v1';

// Lista de URLs (páginas e recursos) que queremos armazenar em cache
const urlsToCache = [
  '/',
  '/registrar-preco',
  '/produtos',
  '/mercados'
];

// Evento 'install': É disparado quando o Service Worker é instalado
self.addEventListener('install', event => {
  // Espera até que o cache seja aberto e todos os URLs sejam adicionados
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Evento 'fetch': É disparado toda vez que o app faz uma requisição (ex: carregar uma página)
self.addEventListener('fetch', event => {
  event.respondWith(
    // 1. Tenta buscar o recurso da rede (online)
    fetch(event.request)
      .then(networkResponse => {
        // Se conseguir, armazena uma cópia no cache para a próxima vez
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
        // 2. Se a rede falhar (offline), tenta pegar o recurso do cache
        console.log('Rede falhou, buscando do cache:', event.request.url);
        return caches.match(event.request);
      })
  );
});