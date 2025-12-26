/**
 * Service Worker for RuDjango PWA
 * 提供離線快取、離線閱讀和推播通知功能
 */

const CACHE_VERSION = 'v1.0.0';
const CACHE_NAME = `rudjango-${CACHE_VERSION}`;

// 需要預先快取的靜態資源
const STATIC_CACHE_URLS = [
    '/',
    '/blog/',
    '/static/css/base.css',
    '/static/blog/css/real-time-notifications.css',
    '/static/blog/css/instant-chat.css',
    '/static/blog/css/chat-center.css',
    '/static/blog/css/mention-autocomplete.css',
    '/static/blog/js/real-time-notifications.js',
    '/static/blog/js/instant-chat.js',
    '/static/blog/js/chat-center.js',
    '/static/blog/js/markdown-preview.js',
    '/static/blog/images/大頭綠.JPG',
    // External libraries (從 CDN)
    'https://cdn.jsdelivr.net/npm/marked@11.1.1/marked.min.js',
    'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js',
    'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js',
    'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css',
    'https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js',
];

// 離線頁面
const OFFLINE_URL = '/offline/';

/**
 * Service Worker 安裝事件
 * 預先快取靜態資源
 */
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_CACHE_URLS);
            })
            .catch((error) => {
                console.error('[Service Worker] Cache installation failed:', error);
            })
    );

    // 強制啟動新的 Service Worker
    self.skipWaiting();
});

/**
 * Service Worker 啟動事件
 * 清理舊快取
 */
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');

    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );

    // 立即接管所有頁面
    return self.clients.claim();
});

/**
 * Fetch 事件處理
 * 實作快取策略
 */
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // 跳過非 GET 請求
    if (request.method !== 'GET') {
        return;
    }

    // 跳過 WebSocket 請求
    if (url.protocol === 'ws:' || url.protocol === 'wss:') {
        return;
    }

    // 跳過 API 請求（除了文章內容）
    if (url.pathname.startsWith('/blog/api/') && !url.pathname.includes('/articles/')) {
        return;
    }

    event.respondWith(
        handleFetch(request)
    );
});

/**
 * 處理 Fetch 請求的快取策略
 */
async function handleFetch(request) {
    const url = new URL(request.url);

    // 1. 靜態資源：Cache First（優先使用快取）
    if (isStaticAsset(url)) {
        return cacheFirst(request);
    }

    // 2. 文章內容：Network First（優先使用網路，失敗時使用快取）
    if (isArticlePage(url)) {
        return networkFirst(request);
    }

    // 3. 文章列表：Stale While Revalidate（使用快取同時更新）
    if (isArticleList(url)) {
        return staleWhileRevalidate(request);
    }

    // 4. 其他頁面：Network First
    return networkFirst(request);
}

/**
 * 判斷是否為靜態資源
 */
function isStaticAsset(url) {
    const staticExtensions = ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot'];
    return staticExtensions.some(ext => url.pathname.endsWith(ext)) ||
           url.pathname.startsWith('/static/') ||
           url.pathname.startsWith('/media/');
}

/**
 * 判斷是否為文章頁面
 */
function isArticlePage(url) {
    return url.pathname.match(/\/blog\/articles\/\d+\//);
}

/**
 * 判斷是否為文章列表
 */
function isArticleList(url) {
    return url.pathname === '/blog/' || url.pathname === '/';
}

/**
 * Cache First 策略
 * 優先使用快取，快取不存在時從網路獲取
 */
async function cacheFirst(request) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
        return cachedResponse;
    }

    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Fetch failed for:', request.url);
        return new Response('Network error', { status: 408, statusText: 'Request Timeout' });
    }
}

/**
 * Network First 策略
 * 優先從網路獲取，失敗時使用快取
 */
async function networkFirst(request) {
    try {
        const networkResponse = await fetch(request);
        if (networkResponse && networkResponse.status === 200) {
            const cache = await caches.open(CACHE_NAME);
            cache.put(request, networkResponse.clone());
        }
        return networkResponse;
    } catch (error) {
        console.log('[Service Worker] Network failed, trying cache for:', request.url);
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // 如果是 HTML 頁面且沒有快取，返回離線頁面
        if (request.headers.get('accept').includes('text/html')) {
            const offlineResponse = await caches.match(OFFLINE_URL);
            if (offlineResponse) {
                return offlineResponse;
            }
        }

        return new Response('Offline and no cache available', { status: 503, statusText: 'Service Unavailable' });
    }
}

/**
 * Stale While Revalidate 策略
 * 立即返回快取，同時在背景更新
 */
async function staleWhileRevalidate(request) {
    const cachedResponse = await caches.match(request);

    const fetchPromise = fetch(request).then((networkResponse) => {
        if (networkResponse && networkResponse.status === 200) {
            const cache = caches.open(CACHE_NAME);
            cache.then(c => c.put(request, networkResponse.clone()));
        }
        return networkResponse;
    }).catch(() => {
        // 網路失敗，不做任何事
    });

    return cachedResponse || fetchPromise;
}

/**
 * 推播通知點擊事件
 */
self.addEventListener('notificationclick', (event) => {
    console.log('[Service Worker] Notification clicked:', event.notification.tag);

    event.notification.close();

    const urlToOpen = event.notification.data?.url || '/blog/notifications/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then((clientList) => {
                // 尋找已開啟的視窗
                for (const client of clientList) {
                    if (client.url === urlToOpen && 'focus' in client) {
                        return client.focus();
                    }
                }
                // 沒有找到，開啟新視窗
                if (clients.openWindow) {
                    return clients.openWindow(urlToOpen);
                }
            })
    );
});

/**
 * 推播通知接收事件
 */
self.addEventListener('push', (event) => {
    console.log('[Service Worker] Push received');

    let notificationData = {
        title: 'RuDjango',
        body: '您有新的通知',
        icon: '/static/blog/images/icons/icon-192x192.png',
        badge: '/static/blog/images/icons/badge-72x72.png',
        data: {
            url: '/blog/notifications/'
        }
    };

    if (event.data) {
        try {
            const data = event.data.json();
            notificationData = {
                title: data.title || notificationData.title,
                body: data.body || data.message || notificationData.body,
                icon: data.icon || notificationData.icon,
                badge: data.badge || notificationData.badge,
                tag: data.tag || 'notification',
                requireInteraction: data.requireInteraction || false,
                data: {
                    url: data.url || notificationData.data.url
                }
            };
        } catch (e) {
            console.error('[Service Worker] Failed to parse push data:', e);
        }
    }

    event.waitUntil(
        self.registration.showNotification(notificationData.title, notificationData)
    );
});

/**
 * 背景同步事件（未來功能）
 */
self.addEventListener('sync', (event) => {
    console.log('[Service Worker] Background sync:', event.tag);

    if (event.tag === 'sync-messages') {
        event.waitUntil(syncMessages());
    }
});

/**
 * 同步離線訊息（未來功能）
 */
async function syncMessages() {
    // TODO: 實作離線訊息同步
    console.log('[Service Worker] Syncing offline messages...');
}

/**
 * 訊息處理（來自主執行緒）
 */
self.addEventListener('message', (event) => {
    console.log('[Service Worker] Message received:', event.data);

    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'CACHE_URLS') {
        const urls = event.data.urls || [];
        event.waitUntil(
            caches.open(CACHE_NAME).then((cache) => {
                return cache.addAll(urls);
            })
        );
    }
});

console.log('[Service Worker] Loaded');
