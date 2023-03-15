const staticSchedulesWebsite = "schedules-website-v5"

let assets = [
  `/new`,
  `/serviceWorker.js`,
  'favicon.svg',
  'manifest.json'
]

self.addEventListener('install', installEvent => {
  installEvent.waitUntil(
    caches.open(staticSchedulesWebsite).then(cache => {
      cache.addAll(assets)
        .catch(_err => console.log('failed to register service worker'))
    })
  )
})

self.addEventListener('fetch', (event) => {
  event.respondWith(
    (async () => {
      const cache = await caches.open(staticSchedulesWebsite);
      const cachedResponse = await cache.match(event.request);

      if (cachedResponse) {
        event.waitUntil(cache.add(event.request));
        return cachedResponse;
      }

      const netResponse = await fetch(event.request);
      await cache.put(event.request, netResponse);

      return netResponse;
    })()
  );
});
