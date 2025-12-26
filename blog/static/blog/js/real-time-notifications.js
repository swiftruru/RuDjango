/**
 * 即時通知系統
 * 使用輪詢機制定期檢查新通知
 */

// 防止重複初始化
if (window.realTimeNotificationsInitialized) {
    // 已初始化，跳過
} else {
    window.realTimeNotificationsInitialized = true;

(function() {
    // 配置
    const POLL_INTERVAL = 10000; // 10 秒檢查一次
    const API_URL = '/blog/api/notifications/count/';

    let pollTimer = null;
    let lastNotificationCount = 0;
    let lastMessageCount = 0;
    let isFirstLoad = true;

    /**
     * 初始化
     */
    function init() {
        // 只對已登入用戶啟用
        const notificationBadge = document.getElementById('notification-count');
        if (!notificationBadge) {
            return;
        }

        // 立即檢查一次
        checkNotifications();

        // 開始定期輪詢
        startPolling();

        // 頁面可見性變化時的處理
        document.addEventListener('visibilitychange', handleVisibilityChange);

        // 頁面離開時停止輪詢
        window.addEventListener('beforeunload', stopPolling);
    }

    /**
     * 開始輪詢
     */
    function startPolling() {
        if (pollTimer) return;

        pollTimer = setInterval(() => {
            checkNotifications();
        }, POLL_INTERVAL);
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
     * 頁面可見性變化處理
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
     * 檢查新通知和訊息
     */
    function checkNotifications() {
        fetch(API_URL, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 檢查通知數量是否增加
                const currentNotificationCount = data.unread_count || 0;
                if (!isFirstLoad && currentNotificationCount > lastNotificationCount) {
                    // 有新通知，顯示最新的通知
                    if (data.recent_notifications && data.recent_notifications.length > 0) {
                        showNotificationToast(data.recent_notifications[0]);
                    }
                }
                lastNotificationCount = currentNotificationCount;

                // 更新通知徽章
                updateNotificationBadge(currentNotificationCount);

                // 檢查訊息數量是否增加
                const currentMessageCount = data.unread_messages_count || 0;
                // 訊息只更新徽章，不顯示 Toast（因為通知已經有 Toast 了）
                lastMessageCount = currentMessageCount;

                // 更新訊息徽章
                updateMessageBadge(currentMessageCount);

                isFirstLoad = false;
            }
        })
        .catch(error => {
            console.error('檢查通知失敗:', error);
        });
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
        } else {
            badge.style.display = 'none';
        }
    }

    /**
     * 更新訊息徽章
     */
    function updateMessageBadge(count) {
        const badge = document.getElementById('message-count');
        if (!badge) return;

        if (count > 0) {
            badge.textContent = count > 99 ? '99+' : count;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    /**
     * 顯示通知 Toast
     */
    function showNotificationToast(notification) {
        // 檢查是否已有通知容器
        let container = document.getElementById('notification-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-toast-container';
            container.className = 'notification-toast-container';
            document.body.appendChild(container);
        }

        // 創建通知卡片
        const toast = document.createElement('div');
        toast.className = 'notification-toast';
        toast.innerHTML = `
            <div class="notification-toast-icon">${notification.icon}</div>
            <div class="notification-toast-content">
                <div class="notification-toast-message">${escapeHtml(notification.message)}</div>
                <div class="notification-toast-time">${notification.time_since}</div>
            </div>
            <button class="notification-toast-close" onclick="this.parentElement.remove()">✕</button>
        `;

        // 點擊通知跳轉
        if (notification.link) {
            toast.style.cursor = 'pointer';
            toast.addEventListener('click', (e) => {
                if (e.target.classList.contains('notification-toast-close')) return;
                window.location.href = notification.link;
            });
        }

        // 添加到容器
        container.appendChild(toast);

        // 動畫顯示
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);

        // 5 秒後自動消失
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);

        // 播放通知音效（可選）
        playNotificationSound();
    }

    /**
     * 播放通知音效
     */
    function playNotificationSound() {
        // 可選：添加音效
        // const audio = new Audio('/static/blog/sounds/notification.mp3');
        // audio.play().catch(e => console.log('無法播放音效:', e));
    }

    /**
     * HTML 轉義（防止 XSS）
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 頁面加載完成後初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

} // 結束防止重複初始化的 else 區塊
