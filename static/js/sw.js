// Service Worker for TekTribe Chronicles
// Cache strategy: Precache essentials, runtime cache for content
const CACHE_VERSION = 'tektribe-v20260828-204054';
const CACHE_NAME = CACHE_VERSION;
const OFFLINE_URL = '/offline.html';

// Precache essential assets (small, always needed)
const PRECACHE_ASSETS = [
  '/',
  '/manifest.json',
  '/css/nav.css',
  '/js/registerSW.js',
  '/icons/icon-192.png',
  '/icons/icon-512.png',
  '/offline.html',
  '/akashic-index.json'
];

// Runtime cache patterns
const RUNTIME_CACHE_PATTERNS = [
  /^\/part[1-9]\//,
  /^\/about\//,
  /^\/preamble\//,
  /^\/oracle\//,
  /\.html$/,
  /\.css$/,
  /\.png$/,
  /\.jpg$/,
  /\.ttf$/,
  /\.woff2?$/,
  /\.json$/
];

// Install event — precache essentials
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[SW] Precaching essential assets');
      return cache.addAll(PRECACHE_ASSETS);
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

// Fetch event — cache-first for precached, stale-while-revalidate for runtime
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // Skip non-http requests
  if (!url.protocol.startsWith('http')) return;

  // Check if this URL should be runtime cached
  const shouldCache = RUNTIME_CACHE_PATTERNS.some(function(pattern) {
    return pattern.test(url.pathname);
  });

  // For precached assets — cache-first
  if (PRECACHE_ASSETS.includes(url.pathname)) {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        return cached || fetch(event.request);
      })
    );
    return;
  }

  // For runtime-cacheable content — stale-while-revalidate
  if (shouldCache) {
    event.respondWith(
      caches.open(CACHE_NAME).then(function(cache) {
        return cache.match(event.request).then(function(cached) {
          var fetchPromise = fetch(event.request).then(function(response) {
            if (response && response.status === 200) {
              cache.put(event.request, response.clone());
            }
            return response;
          }).catch(function() {
            return cached;
          });

          return cached || fetchPromise;
        });
      })
    );
    return;
  }

  // For everything else — network-first, fallback to cache
  event.respondWith(
    fetch(event.request).then(function(response) {
      if (response && response.status === 200) {
        caches.open(CACHE_NAME).then(function(cache) {
          cache.put(event.request, response.clone());
        });
      }
      return response;
    }).catch(function() {
      return caches.match(event.request).then(function(cached) {
        if (cached) return cached;
        if (event.request.mode === 'navigate') {
          return caches.match(OFFLINE_URL);
        }
        return new Response('Offline', { status: 503 });
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
