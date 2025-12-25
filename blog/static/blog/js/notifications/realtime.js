/**
 * 即時通知功能
 * 使用輪詢（Polling）方式定期檢查新通知
 */

(function() {
    'use strict';

    // 配置
    const config = {
        pollInterval: 30000,        // 輪詢間隔（30秒）
        apiUrl: '/blog/api/notifications/count/',
        enabled: true,
    };

    let pollTimer = null;
    let lastUnreadCount = 0;

    /**
     * 初始化即時通知
     */
    function init() {
        // 檢查用戶是否已登入
        const notificationBadge = document.getElementById('notification-count');
        if (!notificationBadge) {
            return;  // 未登入，不啟用
        }

        // 立即檢查一次
        checkNotifications();

        // 啟動定期輪詢
        if (config.enabled) {
            startPolling();
        }

        // 當頁面可見時恢復輪詢
        document.addEventListener('visibilitychange', handleVisibilityChange);
    }

    /**
     * 開始輪詢
     */
    function startPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
        }

        pollTimer = setInterval(() => {
            checkNotifications();
        }, config.pollInterval);
    }

    /**
     * 停止輪詢
     */
    function stopPolling() {
        if (pollTimer) {
            clearInterval(pollTimer);
            pollTimer = null;
        }
    }

    /**
     * 檢查新通知
     */
    async function checkNotifications() {
        try {
            const response = await fetch(config.apiUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error('API 請求失敗');
            }

            const data = await response.json();

            if (data.success) {
                updateNotificationBadge(data.unread_count);

                // 如果有新通知，顯示通知提示
                if (data.unread_count > lastUnreadCount && lastUnreadCount > 0) {
                    showNewNotificationAlert(data.unread_count - lastUnreadCount);
                }

                lastUnreadCount = data.unread_count;
            }
        } catch (error) {
            console.error('檢查通知失敗:', error);
        }
    }

    /**
     * 更新通知徽章
     */
    function updateNotificationBadge(count) {
        const badge = document.getElementById('notification-count');
        if (!badge) return;

        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
            badge.style.animation = 'pulse 0.5s ease';
        } else {
            badge.style.display = 'none';
        }
    }

    /**
     * 顯示新通知提示
     */
    function showNewNotificationAlert(newCount) {
        // 使用瀏覽器通知 API（如果已授權）
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('RuDjango 新通知', {
                body: `您有 ${newCount} 則新通知`,
                icon: '/static/favicon.ico',
                badge: '/static/favicon.ico'
            });
        }

        // 在頁面上顯示提示（可選）
        showToast(`🔔 您有 ${newCount} 則新通知`);
    }

    /**
     * 顯示 Toast 提示
     */
    function showToast(message) {
        // 檢查是否已有 toast 容器
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }

        // 創建 toast 元素
        const toast = document.createElement('div');
        toast.className = 'toast notification-toast';
        toast.textContent = message;

        toastContainer.appendChild(toast);

        // 顯示動畫
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // 自動隱藏
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);

        // 點擊跳轉到通知中心
        toast.addEventListener('click', () => {
            window.location.href = '/blog/notifications/';
        });
    }

    /**
     * 處理頁面可見性變化
     */
    function handleVisibilityChange() {
        if (document.hidden) {
            // 頁面隱藏時停止輪詢
            stopPolling();
        } else {
            // 頁面顯示時恢復輪詢並立即檢查
            checkNotifications();
            startPolling();
        }
    }

    /**
     * 請求瀏覽器通知權限
     */
    function requestNotificationPermission() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    console.log('通知權限已授予');
                }
            });
        }
    }

    /**
     * 導出公共 API
     */
    window.NotificationRealtime = {
        init: init,
        start: startPolling,
        stop: stopPolling,
        check: checkNotifications,
        requestPermission: requestNotificationPermission,
        setEnabled: function(enabled) {
            config.enabled = enabled;
            if (enabled) {
                startPolling();
            } else {
                stopPolling();
            }
        }
    };

    // DOM 載入完成後自動初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
