/**
 * 即時通知系統
 * 使用 WebSocket 實現真正的即時推送
 */

// 防止重複初始化
if (window.realTimeNotificationsInitialized) {
    // 已初始化，跳過
} else {
    window.realTimeNotificationsInitialized = true;

(function() {
    let socket = null;
    let reconnectAttempts = 0;
    const MAX_RECONNECT_ATTEMPTS = 5;
    const RECONNECT_DELAY = 3000; // 3 seconds

    /**
     * 初始化
     */
    function init() {
        // 只對已登入用戶啟用
        const notificationBadge = document.getElementById('notification-count');
        if (!notificationBadge) {
            return;
        }

        // 連接 WebSocket
        connectWebSocket();

        // 頁面離開時關閉連接
        window.addEventListener('beforeunload', () => {
            if (socket) {
                socket.close();
            }
        });
    }

    /**
     * 連接 WebSocket
     */
    function connectWebSocket() {
        // 確定 WebSocket URL
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/notifications/`;

        try {
            socket = new WebSocket(wsUrl);

            socket.onopen = function(e) {
                console.log('WebSocket connected');
                reconnectAttempts = 0; // Reset reconnect attempts on successful connection
            };

            socket.onmessage = function(event) {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            };

            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };

            socket.onclose = function(event) {
                console.log('WebSocket closed:', event.code, event.reason);

                // Attempt to reconnect
                if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                    reconnectAttempts++;
                    console.log(`Attempting to reconnect (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})...`);
                    setTimeout(connectWebSocket, RECONNECT_DELAY);
                } else {
                    console.error('Max reconnection attempts reached. Please refresh the page.');
                }
            };
        } catch (error) {
            console.error('Failed to create WebSocket:', error);
        }
    }

    /**
     * 處理 WebSocket 訊息
     */
    function handleWebSocketMessage(data) {
        const messageType = data.type;

        switch (messageType) {
            case 'initial':
                // 初始數據：更新徽章
                updateNotificationBadge(data.unread_count);
                updateMessageBadge(data.unread_messages_count);
                break;

            case 'notification':
                // 新通知：顯示 Toast
                showNotificationToast(data.notification);
                break;

            case 'count_update':
                // 更新計數
                updateNotificationBadge(data.unread_count);
                updateMessageBadge(data.unread_messages_count);
                break;

            case 'pong':
                // 心跳回應
                break;

            default:
                console.log('Unknown message type:', messageType);
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
        // 檢查是否為即時聊天通知（link 包含 /chat/）
        const isChatNotification = notification.link && notification.link.includes('/chat/');

        // 如果是即時聊天通知且有即時聊天管理器，自動開啟聊天視窗
        if (isChatNotification && window.instantChatManager) {
            // 從 link 提取用戶名: /blog/chat/{username}/
            const match = notification.link.match(/\/chat\/([^\/]+)\//);
            if (match) {
                const username = match[1];
                // 延遲一點點以確保 DOM 已準備好
                setTimeout(() => {
                    // 需要獲取用戶資料來開啟聊天視窗
                    openChatWindowFromNotification(username);
                }, 100);
            }
        }

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

        // 點擊通知跳轉或打開聊天
        if (notification.link) {
            const isChatNotification = notification.link.includes('/chat/');

            toast.style.cursor = 'pointer';
            toast.addEventListener('click', (e) => {
                if (e.target.classList.contains('notification-toast-close')) return;

                // 如果是即時聊天通知且有即時聊天管理器，打開聊天視窗而不是跳轉
                if (isChatNotification && window.instantChatManager) {
                    const match = notification.link.match(/\/chat\/([^\/]+)\//);
                    if (match) {
                        const username = match[1];
                        openChatWindowFromNotification(username);
                        toast.remove();
                        return;
                    }
                }

                // 其他通知（包括傳統私人訊息）正常跳轉
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

        // 播放通知音效
        playNotificationSound();
    }

    /**
     * 從通知打開聊天視窗
     */
    function openChatWindowFromNotification(username) {
        // 獲取用戶資料
        fetch(`/blog/api/user/${username}/`)
            .then(response => response.json())
            .then(data => {
                if (data.success && window.instantChatManager) {
                    window.instantChatManager.openChatWindow(
                        data.user.username,
                        data.user.id,
                        data.user.display_name,
                        data.user.avatar_url
                    );
                }
            })
            .catch(error => {
                console.error('無法獲取用戶資料:', error);
            });
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

    // Keep connection alive with periodic ping
    setInterval(() => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ action: 'ping' }));
        }
    }, 30000); // Ping every 30 seconds

    // 頁面加載完成後初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();

} // 結束防止重複初始化的 else 區塊
