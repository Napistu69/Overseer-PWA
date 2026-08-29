// Service Worker for TekTribe Chronicles
// Cache strategy: Precache ALL pages for full offline access
const CACHE_VERSION = 'tektribe-vtektribe-v20260828-210259';
const CACHE_NAME = CACHE_VERSION;
const OFFLINE_URL = '/offline.html';

// All pages to precache (generated at build time)
const PRECACHE_URLS = ['/', '/about/index.html', '/akashic-index.json', '/css/editor.css', '/css/nav.css', '/css/style.css', '/fonts/Jokerman-Regular.ttf', '/icons/apple-touch-icon.png', '/icons/icon-192.png', '/icons/icon-512.png', '/images/DOH - Coming Soon [HD-1x1].png', '/images/Napištu [Upscale].PNG', '/images/Overseer [JM Transparent].png', '/images/Overseer [JM].png', '/images/Overseer [OG Transparent].png', '/images/TekTribe - Awakening [HD-1x1].PNG', '/images/TekTribe Chronicles Logo [1080].png', '/images/TekTribe Chronicles Logo.png', '/images/tektribe-awakening-banner.jpg', '/images/tektribe-awakening-hd.jpg', '/index.json', '/js/editor.js', '/js/registerSW.js', '/js/sw.js', '/manifest.json', '/offline.html', '/oracle/index.html', '/part1/aether_and_the_mesh/index.html', '/part1/geometry_of_choice/index.html', '/part1/index.html', '/part1/the_continuum/index.html', '/part1/the_continuum_clock/index.html', '/part1/the_minds_eye_and_the_supraliminal_library/index.html', '/part2/dollar_devaluation/index.html', '/part2/hemp_and_the_pyramids_puzzle/index.html', '/part2/index.html', '/part2/inverted_money_tree/index.html', '/part2/linguistic_corruption/index.html', '/part2/natural_material_severance/index.html', '/part2/pharma_cartel_origins/index.html', '/part2/the_petro_goliath/index.html', '/part3/animal_partners_in_the_alliance/index.html', '/part3/fungal_intelligence_and_the_living_network/index.html', '/part3/gsm_delta_emotional_mastery/index.html', '/part3/hive_mind_and_the_suppressed_receiver/index.html', '/part3/index.html', '/part3/operational_protocols/index.html', '/part3/the_avatar_operating_system/index.html', '/part3/the_mycelial_guardian/index.html', '/part3/the_unified_field/index.html', '/part4/algorithmic_manipulation_era/index.html', '/part4/check-ins_to_location_fusion/index.html', '/part4/data_collection_vectors/index.html', '/part4/index.html', '/part4/lifelog_to_facebook_evolution/index.html', '/part4/plan-demic_manipulation/index.html', '/part4/project_monarch_and_the_smartphone_era/index.html', '/part4/recommendation_engine_apotheosis/index.html', '/part4/snowdens_revelation_the_huxleyan_absorption/index.html', '/part4/the_complete_architecture_synthesis_and_transition/index.html', '/part4/the_cookie_at_the_turn_of_century/index.html', '/part4/the_meta_web_when_every_platform_feeds_the_cloud/index.html', '/part4/the_ritual_sacrifice_and_the_patriot_act/index.html', '/part5/celestial__geopolitical_convergence/index.html', '/part5/consent_manufacturing-the_atlas-3_instrument/index.html', '/part5/division_and_conquer-identity_weaponization/index.html', '/part5/financial_nervous_system-the_1913_structural_transfer/index.html', '/part5/foundational_blueprint-the_six-point_architecture/index.html', '/part5/index.html', '/part5/military-industrial_migration-third_reich_transplant/index.html', '/part5/petrodollar_engine-financial_blood_supply/index.html', '/part5/science_as_religion-epistemological_capture/index.html', '/part5/structural_continuity-the_corporate_collegia/index.html', '/part5/the_black_lotus-pharma_control_apparatus/index.html', '/part5/the_hydra_anatomy-adversary_synthesis/index.html', '/part5/the_petro-military_genesis/index.html', '/part5/the_surveillance_escalation/index.html', '/part6/index.html', '/part7/index.html', '/part8/index.html', '/part9/index.html', '/preamble/index.html'];

// Install event — precache everything
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[SW] Precaching', PRECACHE_URLS.length, 'assets');
      return cache.addAll(PRECACHE_URLS);
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

// Fetch event — cache-first strategy
self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  
  // Skip non-http requests
  if (!url.protocol.startsWith('http')) return;

  // Cache-first: check cache, then network, then cache in background
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
});

// Handle skip waiting message from registration script
self.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
