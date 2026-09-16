// Service Worker for TekTribe Chronicles
// Cache strategy: Precache ALL pages for full offline access
const CACHE_VERSION = 'tektribe-v{{VERSION}}';
const CACHE_NAME = CACHE_VERSION;
const OFFLINE_URL = '/offline.html';

// All pages to precache (generated at build time)
const PRECACHE_URLS = [{{PRECACHE_URLS}}];

// Install event — precache everything (with error handling per URL)
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[SW] Precaching', PRECACHE_URLS.length, 'assets');
      // Cache each URL individually so one failure doesn't break all
      return Promise.allSettled(
        PRECACHE_URLS.map(function(url) {
          return cache.add(url).catch(function(err) {
            console.warn('[SW] Failed to cache:', url, err);
          });
        })
      );
    }).then(function() {
      return self.skipWaiting();
    })
  );
});

// Activate event — clean old caches
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.filter(function(name) {
          return name !== CACHE_NAME;
        }).map(function(name) {
          console.log('[SW] Deleting old cache:', name);
          return caches.delete(name);
        })
      );
    }).then(function() {
      return self.clients.claim();
    })
  );
});

// Fetch event — cache-first strategy with directory fallback
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // Skip non-http requests
  if (!url.protocol.startsWith('http')) return;

  // Helper: try cache lookup (handles directory → index.html)
  function tryCache(request) {
    return caches.open(CACHE_NAME).then(function(cache) {
      return cache.match(request).then(function(cached) {
        if (cached) return cached;
        // If URL ends with '/', try index.html version
        if (request.url.endsWith('/')) {
          return cache.match(request.url + 'index.html');
        }
        return undefined;
      });
    });
  }

  // Cache-first: check cache, then network, then cache in background
  event.respondWith(
    tryCache(event.request).then(function(cached) {
      var fetchPromise = fetch(event.request).then(function(response) {
        if (response && response.status === 200) {
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, response.clone());
          });
        }
        return response;
      }).catch(function() {
        return cached;
      });

      return cached || fetchPromise;
    })
  );
});

// Handle skip waiting message from registration script
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
