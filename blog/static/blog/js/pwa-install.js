/**
 * PWA 安裝和 Service Worker 註冊管理
 */

class PWAManager {
    constructor() {
        this.deferredPrompt = null;
        this.isInstalled = false;
        this.swRegistration = null;
        this.init();
    }

    async init() {
        // 檢查是否已安裝
        this.checkInstallStatus();

        // 註冊 Service Worker
        if ('serviceWorker' in navigator) {
            this.registerServiceWorker();
        }

        // 監聽安裝提示
        this.setupInstallPrompt();

        // 監聽離線/在線狀態
        this.setupOnlineOfflineListeners();

        // 創建安裝橫幅
        this.createInstallBanner();
    }

    /**
     * 檢查 PWA 是否已安裝
     */
    checkInstallStatus() {
        // 檢查是否在獨立模式下運行（已安裝）
        if (window.matchMedia('(display-mode: standalone)').matches ||
            window.navigator.standalone === true) {
            this.isInstalled = true;
            console.log('[PWA] App is installed and running in standalone mode');
        }
    }

    /**
     * 註冊 Service Worker
     */
    async registerServiceWorker() {
        try {
            const registration = await navigator.serviceWorker.register('/static/sw.js', {
                scope: '/'
            });

            this.swRegistration = registration;

            console.log('[PWA] Service Worker registered:', registration.scope);

            // 檢查更新
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                console.log('[PWA] New Service Worker found');

                newWorker.addEventListener('statechange', () => {
                    if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                        // 有新版本可用
                        this.showUpdateAvailable();
                    }
                });
            });

            // 定期檢查更新（每小時）
            setInterval(() => {
                registration.update();
            }, 3600000);

        } catch (error) {
            console.error('[PWA] Service Worker registration failed:', error);
        }
    }

    /**
     * 設置安裝提示監聽
     */
    setupInstallPrompt() {
        window.addEventListener('beforeinstallprompt', (e) => {
            console.log('[PWA] beforeinstallprompt event fired');

            // 防止 Chrome 67 及更早版本自動顯示提示
            e.preventDefault();

            // 保存事件以便稍後觸發
            this.deferredPrompt = e;

            // 顯示安裝橫幅
            this.showInstallBanner();
        });

        // 監聽安裝完成
        window.addEventListener('appinstalled', () => {
            console.log('[PWA] App installed');
            this.isInstalled = true;
            this.hideInstallBanner();
            this.showInstallSuccess();
        });
    }

    /**
     * 創建安裝橫幅
     */
    createInstallBanner() {
        const banner = document.createElement('div');
        banner.id = 'pwa-install-banner';
        banner.className = 'pwa-install-banner';
        banner.style.display = 'none';
        banner.innerHTML = `
            <div class="pwa-banner-content">
                <div class="pwa-banner-icon">📱</div>
                <div class="pwa-banner-text">
                    <div class="pwa-banner-title">安裝 RuDjango App</div>
                    <div class="pwa-banner-subtitle">快速訪問，離線閱讀</div>
                </div>
                <div class="pwa-banner-actions">
                    <button class="pwa-install-btn" id="pwa-install-btn">安裝</button>
                    <button class="pwa-close-btn" id="pwa-close-btn">×</button>
                </div>
            </div>
        `;

        document.body.appendChild(banner);

        // 綁定事件
        document.getElementById('pwa-install-btn').addEventListener('click', () => {
            this.promptInstall();
        });

        document.getElementById('pwa-close-btn').addEventListener('click', () => {
            this.hideInstallBanner();
            // 記住用戶關閉了橫幅，7天內不再顯示
            localStorage.setItem('pwa-banner-dismissed', Date.now());
        });
    }

    /**
     * 顯示安裝橫幅
     */
    showInstallBanner() {
        // 如果已安裝，不顯示
        if (this.isInstalled) return;

        // 如果用戶最近關閉過，不顯示（7天內）
        const dismissedTime = localStorage.getItem('pwa-banner-dismissed');
        if (dismissedTime) {
            const daysSinceDismissed = (Date.now() - parseInt(dismissedTime)) / (1000 * 60 * 60 * 24);
            if (daysSinceDismissed < 7) return;
        }

        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.style.display = 'block';
            setTimeout(() => {
                banner.classList.add('show');
            }, 100);
        }
    }

    /**
     * 隱藏安裝橫幅
     */
    hideInstallBanner() {
        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            banner.classList.remove('show');
            setTimeout(() => {
                banner.style.display = 'none';
            }, 300);
        }
    }

    /**
     * 提示用戶安裝
     */
    async promptInstall() {
        if (!this.deferredPrompt) {
            console.log('[PWA] Install prompt not available');
            return;
        }

        // 顯示安裝提示
        this.deferredPrompt.prompt();

        // 等待用戶響應
        const { outcome } = await this.deferredPrompt.userChoice;

        console.log(`[PWA] User choice: ${outcome}`);

        if (outcome === 'accepted') {
            console.log('[PWA] User accepted the install prompt');
        } else {
            console.log('[PWA] User dismissed the install prompt');
        }

        // 清除 deferredPrompt
        this.deferredPrompt = null;

        // 隱藏橫幅
        this.hideInstallBanner();
    }

    /**
     * 顯示更新可用通知
     */
    showUpdateAvailable() {
        // 創建更新通知
        const notification = document.createElement('div');
        notification.className = 'pwa-update-notification';
        notification.innerHTML = `
            <div class="pwa-update-content">
                <span class="pwa-update-text">有新版本可用</span>
                <button class="pwa-update-btn" id="pwa-update-btn">更新</button>
                <button class="pwa-update-close" id="pwa-update-close">×</button>
            </div>
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // 更新按鈕
        document.getElementById('pwa-update-btn').addEventListener('click', () => {
            this.updateServiceWorker();
        });

        // 關閉按鈕
        document.getElementById('pwa-update-close').addEventListener('click', () => {
            notification.remove();
        });
    }

    /**
     * 更新 Service Worker
     */
    updateServiceWorker() {
        if (this.swRegistration && this.swRegistration.waiting) {
            // 告訴等待中的 SW 跳過等待並啟動
            this.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });

            // 監聽 controlling 事件
            navigator.serviceWorker.addEventListener('controllerchange', () => {
                // 重新載入頁面以使用新的 SW
                window.location.reload();
            });
        }
    }

    /**
     * 顯示安裝成功訊息
     */
    showInstallSuccess() {
        const message = document.createElement('div');
        message.className = 'pwa-success-message';
        message.textContent = '✓ App 安裝成功！';
        document.body.appendChild(message);

        setTimeout(() => {
            message.classList.add('show');
        }, 100);

        setTimeout(() => {
            message.classList.remove('show');
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 3000);
    }

    /**
     * 設置離線/在線監聽器
     */
    setupOnlineOfflineListeners() {
        window.addEventListener('online', () => {
            console.log('[PWA] App is online');
            this.showOnlineStatus();
        });

        window.addEventListener('offline', () => {
            console.log('[PWA] App is offline');
            this.showOfflineStatus();
        });

        // 初始狀態
        if (!navigator.onLine) {
            this.showOfflineStatus();
        }
    }

    /**
     * 顯示離線狀態
     */
    showOfflineStatus() {
        let indicator = document.getElementById('offline-indicator');

        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <span class="offline-icon">📡</span>
                <span class="offline-text">離線模式</span>
            `;
            document.body.appendChild(indicator);
        }

        setTimeout(() => {
            indicator.classList.add('show');
        }, 100);
    }

    /**
     * 顯示在線狀態
     */
    showOnlineStatus() {
        const indicator = document.getElementById('offline-indicator');

        if (indicator) {
            // 先顯示「已連線」訊息
            indicator.innerHTML = `
                <span class="offline-icon">✓</span>
                <span class="offline-text">已連線</span>
            `;
            indicator.classList.add('online');

            // 2秒後移除
            setTimeout(() => {
                indicator.classList.remove('show');
                setTimeout(() => {
                    indicator.remove();
                }, 300);
            }, 2000);
        }
    }

    /**
     * 快取特定 URL（用於離線閱讀）
     */
    cacheUrls(urls) {
        if (this.swRegistration && this.swRegistration.active) {
            this.swRegistration.active.postMessage({
                type: 'CACHE_URLS',
                urls: urls
            });
        }
    }

    /**
     * 訂閱推播通知
     */
    async subscribePushNotifications() {
        if (!this.swRegistration) {
            console.error('[PWA] Service Worker not registered');
            return null;
        }

        try {
            // 請求通知權限
            const permission = await Notification.requestPermission();

            if (permission !== 'granted') {
                console.log('[PWA] Notification permission denied');
                return null;
            }

            // 訂閱推播
            const subscription = await this.swRegistration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY)
            });

            console.log('[PWA] Push subscription successful');

            // 發送訂閱資訊到後端
            await this.sendSubscriptionToServer(subscription);

            return subscription;

        } catch (error) {
            console.error('[PWA] Failed to subscribe to push notifications:', error);
            return null;
        }
    }

    /**
     * 發送訂閱資訊到後端
     */
    async sendSubscriptionToServer(subscription) {
        try {
            const response = await fetch('/blog/api/push/subscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    subscription: subscription.toJSON()
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('[PWA] Subscription sent to server successfully');
                return true;
            } else {
                console.error('[PWA] Failed to save subscription on server:', data.error);
                return false;
            }
        } catch (error) {
            console.error('[PWA] Error sending subscription to server:', error);
            return false;
        }
    }

    /**
     * 取消推播訂閱
     */
    async unsubscribePushNotifications() {
        if (!this.swRegistration) {
            console.error('[PWA] Service Worker not registered');
            return false;
        }

        try {
            const subscription = await this.swRegistration.pushManager.getSubscription();

            if (!subscription) {
                console.log('[PWA] No subscription to unsubscribe');
                return true;
            }

            // 從後端刪除訂閱
            await this.removeSubscriptionFromServer(subscription);

            // 取消本地訂閱
            const successful = await subscription.unsubscribe();

            if (successful) {
                console.log('[PWA] Push unsubscribed successfully');
            }

            return successful;

        } catch (error) {
            console.error('[PWA] Failed to unsubscribe from push notifications:', error);
            return false;
        }
    }

    /**
     * 從後端刪除訂閱
     */
    async removeSubscriptionFromServer(subscription) {
        try {
            const response = await fetch('/blog/api/push/unsubscribe/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    endpoint: subscription.endpoint
                })
            });

            const data = await response.json();

            if (data.success) {
                console.log('[PWA] Subscription removed from server');
                return true;
            } else {
                console.error('[PWA] Failed to remove subscription from server:', data.error);
                return false;
            }
        } catch (error) {
            console.error('[PWA] Error removing subscription from server:', error);
            return false;
        }
    }

    /**
     * 獲取 CSRF Token
     */
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        return '';
    }

    /**
     * 轉換 VAPID key
     */
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/\-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }
}

// 初始化 PWA 管理器
document.addEventListener('DOMContentLoaded', function() {
    window.pwaManager = new PWAManager();
});
