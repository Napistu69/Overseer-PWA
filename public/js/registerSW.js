// Service Worker Registration
(function() {
  'use strict';

  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] Service workers not supported');
    return;
  }

  // Register service worker
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js')
      .then(function(registration) {
        console.log('[PWA] ServiceWorker registered:', registration.scope);

        // Listen for updates
        registration.addEventListener('updatefound', function() {
          const newWorker = registration.installing;
          console.log('[PWA] New service worker found');

          newWorker.addEventListener('statechange', function() {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // New content available — show update prompt
              console.log('[PWA] New content available');
              showUpdateBanner(newWorker);
            }
          });
        });
      })
      .catch(function(error) {
        console.log('[PWA] ServiceWorker registration failed:', error);
      });
  });

  // Listen for controller change (new SW took control)
  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', function() {
    if (!refreshing) {
      refreshing = true;
      window.location.reload();
    }
  });

  // Show update banner
  function showUpdateBanner(worker) {
    // Check if banner already exists
    if (document.getElementById('pwa-update-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'pwa-update-banner';
    banner.style.cssText = `
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: #4A7C59;
      color: white;
      padding: 16px 20px;
      text-align: center;
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 -2px 12px rgba(0,0,0,0.3);
    `;
    banner.innerHTML = `
      <p style="margin: 0 0 8px 0; font-size: 0.95rem;">New threads available. Refresh to update.</p>
      <button id="pwa-refresh-btn" style="
        background: white;
        color: #4A7C59;
        border: none;
        padding: 8px 24px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
      ">Refresh</button>
    `;
    document.body.appendChild(banner);

    document.getElementById('pwa-refresh-btn').addEventListener('click', function() {
      worker.postMessage({ type: 'SKIP_WAITING' });
    });
  }

  // Install prompt handling
  let deferredPrompt;
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    deferredPrompt = e;
    showInstallBanner();
  });

  function showInstallBanner() {
    // Check if banner already exists
    if (document.getElementById('pwa-install-banner')) return;

    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.style.cssText = `
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      background: #1A1A1A;
      color: white;
      padding: 16px 20px;
      text-align: center;
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      box-shadow: 0 -2px 12px rgba(0,0,0,0.3);
      border-top: 2px solid #4A7C59;
    `;
    banner.innerHTML = `
      <p style="margin: 0 0 8px 0; font-size: 0.95rem;">Install TekTribe Chronicles</p>
      <button id="pwa-install-btn" style="
        background: #4A7C59;
        color: white;
        border: none;
        padding: 8px 24px;
        border-radius: 6px;
        font-weight: 600;
        cursor: pointer;
        margin-right: 8px;
      ">Install</button>
      <button id="pwa-dismiss-btn" style="
        background: transparent;
        color: #B0B0B0;
        border: 1px solid #555;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
      ">Not Now</button>
    `;
    document.body.appendChild(banner);

    document.getElementById('pwa-install-btn').addEventListener('click', function() {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function() {
          banner.remove();
        });
      }
    });

    document.getElementById('pwa-dismiss-btn').addEventListener('click', function() {
      banner.remove();
    });
  }
})();
