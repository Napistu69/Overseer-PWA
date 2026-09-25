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

// Fetch event — cache-first with offline fallback
// Critical: navigation requests that miss cache AND fail network must get offline page
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);

  // Skip non-http requests (chrome-extension:, data:, etc.)
  if (!url.protocol.startsWith('http')) return;

  // Navigation requests: cache-first, then network, then offline page
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        return fetch(event.request).then(function(response) {
          if (response && response.status === 200) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        }).catch(function() {
          // Network failed — serve offline page. If even that isn't cached,
          // return a minimal inline HTML so the app never shows ERR_FAILED.
          return caches.match(OFFLINE_URL).then(function(offline) {
            if (offline) return offline;
            return new Response(
              '<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Offline</title></head><body style="font-family:sans-serif;background:#121212;color:#E0E0E0;display:flex;align-items:center;justify-content:center;height:100vh;margin:0"><div style="text-align:center"><h1 style="color:#4A7C59">TekTribe Chronicles</h1><p>You are offline. Reconnect to browse the archive.</p></div></body></html>',
              { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
            );
          });
        });
      })
    );
    return;
  }

  // Non-navigation requests (CSS, JS, images, JSON): cache-first
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        if (response && response.status === 200) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      });
    })
  );
});

// Handle skip waiting message from registration script
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
