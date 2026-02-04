/* Programma del Service Worker */

const CACHE_NAME = 'briacerbe-dental-v1';

/* file statici da mettere in cache */
const filesToCache = [

    /* HTML */
    /*'/',
    'templates/appuntamento.html',
    'templates/components/bottom.html',
    'templates/dentist.html',
    'templates/hygienist.html',
    'templates/index.html',
    'templates/info.html',
    'templates/login.html',
    'templates/prenotazioni.html',
    'templates/register.html',
    'templates/surgeon.html',*/

    /* HTML via route Flask */
    '/',             // corrisponde a @app.route("/")
    '/info',         // corrisponde a @app.route("/info")
    '/prenotazioni',
    '/servizi',
    '/login',
    '/appuntamento',
    '/register',
    '/dentist',
    '/surgeon',
    '/hygienist',


    /* CSS */
    '/static/appuntamento.css',
    '/static/bottom.css',
    '/static/index.css',
    '/static/login.css',
    '/static/piece.css',
    '/static/register.css',


    /* JAVASCRIPT */
    '/static/main.js',

    /* IMMAGINI */
    '/static/icone_tab_bar/home_no_bg.png',
    '/static/icone_tab_bar/info_no_bg.png',
    '/static/icone_tab_bar/prenotazioni_no_bg.png',


    '/static/icone/chirurgo.png',
    '/static/icone/dentista.png',
    '/static/icone/igienista.png',
    '/static/icone/logo.png',
    '/static/icone/sfondo-logo.png',
    '/static/icone/sfondo_appuntamento.png',

    /* PWA */
    '/static/manifest.json'
];

/* installa la cache */
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('[SW] Cache aperta');
                return cache.addAll(filesToCache);
            })
    );
});

/* attiva la pulizia della vecchia cache */
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cache => {
                    if (cache !== CACHE_NAME) {
                        console.log('[SW] Cancello cache vecchia:', cache);
                        return caches.delete(cache);
                    }
                })
            );
        })
    );
});

/* fetcha la cache */
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // se esiste in cache, usa quella
                if (response) {
                    return response;
                }
                // altrimenti vai in rete
                return fetch(event.request);
            })
    );
});
