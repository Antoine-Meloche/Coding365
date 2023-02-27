const staticSchedulesWebsite = "schedules-website-v1"

const queryString = location.search;
const parameters = new URLSearchParams(queryString);
const id = parameters.get('id');

let assets = [
  "/new",
  `/schedules?id=${id}`,
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

self.addEventListener('fetch', fetchEvent => {
  fetchEvent.respondWith(
    caches.match(fetchEvent.request).then(res => {
      return res || fetch(fetchEvent.request)
    })
  )
})
