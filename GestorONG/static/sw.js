const CACHE_NAME = 'gestorong-cache-v1';
const urlsToCache = [
  '/',
  '/manifest.json'
];

// Instalación
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
      .catch((error) => {
        console.error('Error al guardar recursos en caché:', error);
      })
  );
  self.skipWaiting();
});

// Activación
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Borrando caché antigua:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Interceptar peticiones para funcionamiento offline/caché (Network First / Fallback to Cache)
self.addEventListener('fetch', (event) => {
  // Ignorar peticiones que no sean GET (como solicitudes POST de AJAX)
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Si la petición web es exitosa, se devuelve la respuesta fresca
        return response;
      })
      .catch(() => {
        // Si no hay internet o falla el servidor, responde con la versión en caché
        return caches.match(event.request);
      })
  );
});