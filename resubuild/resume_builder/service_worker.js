
"use strict";

const CACHE_NAME = "bxb-resume-builder-v1";

const OFFLINE_URL =
    "/static/resume_builder/pwa/offline.html";

const STATIC_ASSETS = [
    "/static/resume_builder/manifest.json",
    "/static/resume_builder/js/ats_analyzer.js",
    "/static/resume_builder/js/pwa-install.js",
    OFFLINE_URL,
];

/*
 * Install:
 * Cache essential static resources when available.
 * Missing resources do not prevent the service worker from installing;
 * add the remaining PWA files before testing offline support.
 */
self.addEventListener("install", (event) => {
    event.waitUntil(
        (async () => {
            const cache = await caches.open(CACHE_NAME);

            await Promise.all(
                STATIC_ASSETS.map(async (assetUrl) => {
                    try {
                        const response = await fetch(assetUrl, {
                            cache: "reload",
                        });

                        if (response.ok) {
                            await cache.put(assetUrl, response);
                        }
                    } catch (error) {
                        // The asset may not exist yet or the network may
                        // be unavailable. Installation can still complete.
                        console.warn(
                            "BxB PWA: Could not precache:",
                            assetUrl
                        );
                    }
                })
            );

            await self.skipWaiting();
        })()
    );
});

/*
 * Activate:
 * Remove old versions of this app's cache when deploying an update.
 */
self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            const cacheNames = await caches.keys();

            await Promise.all(
                cacheNames.map(async (cacheName) => {
                    if (
                        cacheName.startsWith("bxb-resume-builder-") &&
                        cacheName !== CACHE_NAME
                    ) {
                        await caches.delete(cacheName);
                    }
                })
            );

            await self.clients.claim();
        })()
    );
});

/*
 * Fetch:
 * - Navigation: network first, with a cached page as fallback.
 * - Static resources: network first, with cached assets as fallback.
 * - POST/API requests: never cache; send them to Django normally.
 * - Other cross-origin requests: leave them to the browser.
 */
self.addEventListener("fetch", (event) => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const requestUrl = new URL(request.url);

    if (requestUrl.origin !== self.location.origin) {
        return;
    }

    // Never cache Resume Intelligence API traffic or other API responses.
    if (
        requestUrl.pathname.includes("/api/") ||
        requestUrl.pathname.endsWith("/service-worker.js")
    ) {
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(handleNavigation(request));
        return;
    }

    if (requestUrl.pathname.startsWith("/static/")) {
        event.respondWith(handleStaticAsset(request));
    }
});

/*
 * Navigation strategy:
 * Prefer the live Django page. If offline, use the previously cached page,
 * then show the offline fallback page.
 */
async function handleNavigation(request) {
    try {
        const response = await fetch(request);

        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);

            // Cache only successful same-origin pages, not redirects or errors.
            await cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        const cachedPage = await caches.match(request);

        if (cachedPage) {
            return cachedPage;
        }

        const offlinePage = await caches.match(OFFLINE_URL);

        if (offlinePage) {
            return offlinePage;
        }

        return new Response(
            [
                "<!doctype html>",
                '<html lang="en">',
                "<head>",
                '<meta charset="utf-8">',
                '<meta name="viewport" content="width=device-width, initial-scale=1">',
                "<title>BxB Resume Builder — Offline</title>",
                "</head>",
                "<body>",
                "<h1>You are offline</h1>",
                "<p>Reconnect to the internet and reopen BxB Resume Builder.</p>",
                "</body>",
                "</html>",
            ].join(""),
            {
                status: 503,
                headers: {
                    "Content-Type": "text/html; charset=utf-8",
                    "Cache-Control": "no-store",
                },
            }
        );
    }
}

/*
 * Static resource strategy:
 * Prefer the latest resource from the server, while retaining a cached
 * copy for when the device is offline.
 */
async function handleStaticAsset(request) {
    try {
        const response = await fetch(request);

        if (response.ok) {
            const cache = await caches.open(CACHE_NAME);
            await cache.put(request, response.clone());
        }

        return response;
    } catch (error) {
        const cachedAsset = await caches.match(request);

        if (cachedAsset) {
            return cachedAsset;
        }

        return new Response("Asset unavailable offline.", {
            status: 503,
            headers: {
                "Content-Type": "text/plain; charset=utf-8",
                "Cache-Control": "no-store",
            },
        });
    }
}
