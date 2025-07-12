/**
 * Service Worker para GovBR Roleplay
 * Funcionalidades básicas de cache e offline
 */

const CACHE_NAME = 'govbr-roleplay-v1';
const urlsToCache = [
    '/',
    '/static/css/main.css',
    '/static/js/main.js',
    '/static/images/default-avatar.svg'
];

// Instalação do Service Worker
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Cache aberto');
                return cache.addAll(urlsToCache);
            })
    );
});

// Interceptar requisições
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - retorna resposta
                if (response) {
                    return response;
                }
                return fetch(event.request);
            }
        )
    );
});

// Atualização do Service Worker
self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
}); 