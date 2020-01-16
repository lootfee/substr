self.addEventListener('install', function(e) {
 e.waitUntil(
   caches.open('substr').then(function(cache) {
     return cache.addAll([
       '/',
       '../templates/index.html',
       '../templates/index.html?homescreen=1',
       '../templates/?homescreen=1',
     ]);
   })
 );
});


self.addEventListener('fetch', function(event) {
 console.log(event.request.url);

 event.respondWith(
   caches.match(event.request).then(function(response) {
     return response || fetch(event.request);
   })
 );
});