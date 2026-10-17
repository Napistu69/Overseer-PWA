// Service Worker for TekTribe Chronicles
// Cache strategy: precache the whole archive so it reads offline.
const CACHE_VERSION = 'tektribe-v{{VERSION}}';
const CACHE_NAME = CACHE_VERSION;

// Canonical offline URL. Cloudflare Pages 308-redirects `/offline.html` to
// `/offline`, and a response that carries a redirect flag must never be handed
// to a navigation request — the browser answers that with a network error
// (ERR_FAILED), which is exactly the offline failure this avoids.
const OFFLINE_URL = '/offline';

// All pages to precache (generated at build time)
const PRECACHE_URLS = [{{PRECACHE_URLS}}];

// Last-resort page: if the network is down AND no offline page is cached,
// this inline HTML is returned so the app can never surface ERR_FAILED.
const INLINE_OFFLINE_HTML =
  '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">' +
  '<meta name="viewport" content="width=device-width,initial-scale=1">' +
  '<title>Offline - TekTribe Chronicles</title></head>' +
  '<body style="font-family:sans-serif;background:#121212;color:#E0E0E0;' +
  'display:flex;align-items:center;justify-content:center;height:100vh;margin:0">' +
  '<div style="text-align:center;padding:1.5rem">' +
  '<h1 style="color:#4A7C59;margin:0 0 0.5rem">TekTribe Chronicles</h1>' +
  '<p style="margin:0">You are offline. Reconnect to browse the archive.</p>' +
  '</div></body></html>';

// Rebuild any cached response that carries the redirect flag as a clean 200.
// Returning a redirected response to a navigation request yields ERR_FAILED,
// so a cached `/index.html` or `/offline.html` entry must be normalised here.
function withoutRedirect(response) {
  if (!response || !response.redirected) return Promise.resolve(response);
  return response.blob().then(function (body) {
    return new Response(body, {
      status: 200,
      statusText: 'OK',
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'text/html; charset=utf-8'
      }
    });
  });
}

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

// Fetch — cache-first, with a network fallback and a guaranteed offline page.
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  var url = new URL(event.request.url);

  // Skip non-http requests (chrome-extension:, data:, etc.)
  if (!url.protocol.startsWith('http')) return;

  // Navigations: cache, then network, then the offline page — never ERR_FAILED.
  if (event.request.mode === 'navigate') {
    event.respondWith(
      caches.match(event.request).then(function(cached) {
        if (cached) return withoutRedirect(cached);
        return fetch(event.request).then(function(response) {
          // Only store clean 200s. A redirected response would be useless (and
          // harmful) on the next offline navigation.
          if (response && response.status === 200 && !response.redirected) {
            var clone = response.clone();
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, clone);
            });
          }
          return response;
        }).catch(function() {
          // Network failed — serve the offline page. If even that is missing,
          // return inline HTML so the app never shows ERR_FAILED.
          return caches.match(OFFLINE_URL).then(function(offline) {
            if (offline) return withoutRedirect(offline);
            return new Response(INLINE_OFFLINE_HTML, {
              headers: { 'Content-Type': 'text/html; charset=utf-8' }
            });
          });
        });
      })
    );
    return;
  }

  // Sub-resources (CSS, JS, images, JSON): cache-first, fail quietly.
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) return cached;
      return fetch(event.request).then(function(response) {
        if (response && response.status === 200 && !response.redirected) {
          var clone = response.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, clone);
          });
        }
        return response;
      }).catch(function() {
        // A missing sub-resource must not reject respondWith — that surfaces as
        // ERR_FAILED for the resource.
        return new Response('', { status: 504, statusText: 'Offline' });
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
