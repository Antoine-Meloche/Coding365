const staticSchedulesWebsite = "schedules-website-v1"

const queryString = location.search;
const parameters = new URLSearchParams(queryString);
const id = parameters.get('id');

let assets = [
  "/new",
  `/schedules?id=${id}`,
  `serviceWorker.js?id=${id}`
]

fetch(`/image-paths?id=${id}`).then(res => res.json()).then(data => {
  assets = assets.concat(data)
})

self.addEventListener('install', installEvent => {
  installEvent.waitUntil(
    caches.open(staticSchedulesWebsite).then(cache => {
      cache.addAll(assets)
        .catch(err => console.log('failed to register service worker'))
    })
  )
})

//self.addEventListener('fetch', fetchEvent => {
//  fetchEvent.respondWith(
//    caches.match(fetchEvent.request).then(res => {
//      return res || fetch(fetchEvent.request)
//    })
//  )
//})

self.addEventListener("fetch", (e) => {
  e.respondWith(
    (async () => {
      const r = await caches.match(e.request);
      console.log(`[Service Worker] Fetching resource: ${e.request.url}`);
      if (r) {
        return r;
      }
      const response = await fetch(e.request);
      const cache = await caches.open(cacheName);
      console.log(`[Service Worker] Caching new resource: ${e.request.url}`);
      cache.put(e.request, response.clone());
      return response;
    })()
  );
});
