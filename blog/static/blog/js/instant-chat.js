/**
 * 即時聊天功能 (類似 Facebook Messenger)
 * 支援多個聊天視窗、即時訊息推送、最小化功能
 */

class InstantChatManager {
    constructor() {
        this.chatWindows = new Map(); // username -> ChatWindow object
        this.sockets = new Map(); // username -> WebSocket
        this.maxWindows = 3; // 最多同時開啟 3 個聊天視窗
        this.init();
    }

    init() {
        // 監聽即時聊天按鈕點擊
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('.btn-instant-chat');
            if (btn) {
                e.preventDefault();
                const username = btn.dataset.username;
                const userId = btn.dataset.userId;
                const displayName = btn.dataset.displayName;
                const avatarUrl = btn.dataset.avatarUrl;
                this.openChatWindow(username, userId, displayName, avatarUrl);
            }
        });

        // 創建聊天視窗容器
        if (!document.querySelector('.chat-windows-container')) {
            const container = document.createElement('div');
            container.className = 'chat-windows-container';
            document.body.appendChild(container);
        }
    }

    openChatWindow(username, userId, displayName, avatarUrl) {
        // 如果已經開啟，則聚焦該視窗
        if (this.chatWindows.has(username)) {
            const chatWindow = this.chatWindows.get(username);
            chatWindow.focus();
            return;
        }

        // 如果達到最大視窗數，關閉最舊的
        if (this.chatWindows.size >= this.maxWindows) {
            const firstKey = this.chatWindows.keys().next().value;
            this.closeChatWindow(firstKey);
        }

        // 創建新聊天視窗
        const chatWindow = new ChatWindow(username, userId, displayName, avatarUrl, this);
        this.chatWindows.set(username, chatWindow);

        // 建立 WebSocket 連接
        this.connectWebSocket(username, userId);
    }

    closeChatWindow(username) {
        const chatWindow = this.chatWindows.get(username);
        if (chatWindow) {
            chatWindow.remove();
            this.chatWindows.delete(username);
        }

        // 關閉 WebSocket
        const socket = this.sockets.get(username);
        if (socket) {
            socket.close();
            this.sockets.delete(username);
        }
    }

    connectWebSocket(username, userId) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat/${username}/`;

        const socket = new WebSocket(wsUrl);

        socket.onopen = (e) => {
            console.log(`Chat WebSocket connected to ${username}`);
            const chatWindow = this.chatWindows.get(username);
            if (chatWindow) {
                chatWindow.setConnectionStatus('connected');
            }
        };

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(username, data);
        };

        socket.onerror = (error) => {
            console.error(`Chat WebSocket error for ${username}:`, error);
            const chatWindow = this.chatWindows.get(username);
            if (chatWindow) {
                chatWindow.setConnectionStatus('error');
            }
        };

        socket.onclose = (e) => {
            console.log(`Chat WebSocket closed for ${username}`);
            this.sockets.delete(username);
            const chatWindow = this.chatWindows.get(username);
            if (chatWindow) {
                chatWindow.setConnectionStatus('disconnected');
            }
        };

        this.sockets.set(username, socket);
    }

    handleMessage(username, data) {
        const chatWindow = this.chatWindows.get(username);
        if (!chatWindow) return;

        if (data.type === 'chat_history') {
            // 載入歷史訊息
            chatWindow.loadHistory(data.messages);
        } else if (data.type === 'chat_message') {
            // 新訊息
            chatWindow.addMessage(data.message);
        } else if (data.type === 'typing') {
            // 打字指示器
            chatWindow.showTyping(data.is_typing);
        }
    }

    sendMessage(username, message) {
        const socket = this.sockets.get(username);
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'chat_message',
                message: message
            }));
            return true;
        }
        return false;
    }

    sendTyping(username, isTyping) {
        const socket = this.sockets.get(username);
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({
                type: 'typing',
                is_typing: isTyping
            }));
        }
    }
}

class ChatWindow {
    constructor(username, userId, displayName, avatarUrl, manager) {
        this.username = username;
        this.userId = userId;
        this.displayName = displayName;
        this.avatarUrl = avatarUrl;
        this.manager = manager;
        this.isMinimized = false;
        this.typingTimeout = null;
        this.isComposing = false;  // 追蹤中文輸入狀態
        this.create();
    }

    create() {
        // 創建聊天視窗 HTML
        const container = document.querySelector('.chat-windows-container');

        const windowDiv = document.createElement('div');
        windowDiv.className = 'chat-window';
        windowDiv.dataset.username = this.username;

        windowDiv.innerHTML = `
            <div class="chat-window-header">
                <div class="chat-header-left">
                    <div class="chat-avatar">
                        ${this.avatarUrl ? `<img src="${this.avatarUrl}" alt="${this.displayName}">` : `<span>${this.displayName.charAt(0)}</span>`}
                    </div>
                    <div class="chat-user-info">
                        <div class="chat-user-name">${this.displayName}</div>
                        <div class="chat-status">線上</div>
                    </div>
                </div>
                <div class="chat-header-actions">
                    <button class="chat-action-btn minimize-btn" title="最小化">
                        <span>─</span>
                    </button>
                    <button class="chat-action-btn close-btn" title="關閉">
                        <span>✕</span>
                    </button>
                </div>
            </div>
            <div class="chat-messages">
                <div class="chat-loading">載入訊息中...</div>
            </div>
            <div class="chat-input-area">
                <textarea class="chat-input" placeholder="輸入訊息..." rows="1"></textarea>
                <button class="chat-send-btn" title="發送">
                    <span>➤</span>
                </button>
            </div>
        `;

        container.appendChild(windowDiv);
        this.element = windowDiv;

        // 綁定事件
        this.bindEvents();

        // 自動聚焦輸入框
        setTimeout(() => {
            this.element.querySelector('.chat-input').focus();
        }, 300);
    }

    bindEvents() {
        // 標題列點擊 - 最小化/還原
        const header = this.element.querySelector('.chat-window-header');
        header.addEventListener('click', (e) => {
            if (!e.target.closest('.chat-action-btn')) {
                this.toggleMinimize();
            }
        });

        // 最小化按鈕
        const minimizeBtn = this.element.querySelector('.minimize-btn');
        minimizeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleMinimize();
        });

        // 關閉按鈕
        const closeBtn = this.element.querySelector('.close-btn');
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.manager.closeChatWindow(this.username);
        });

        // 發送訊息
        const sendBtn = this.element.querySelector('.chat-send-btn');
        const input = this.element.querySelector('.chat-input');

        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });

        // 監聽中文輸入開始
        input.addEventListener('compositionstart', () => {
            this.isComposing = true;
        });

        // 監聽中文輸入結束
        input.addEventListener('compositionend', () => {
            this.isComposing = false;
        });

        input.addEventListener('keydown', (e) => {
            // 只有在不是中文輸入狀態時才處理 Enter
            if (e.key === 'Enter' && !e.shiftKey && !this.isComposing) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 打字指示器
        input.addEventListener('input', () => {
            this.handleTyping();
        });

        // 自動調整 textarea 高度
        input.addEventListener('input', () => {
            input.style.height = 'auto';
            input.style.height = Math.min(input.scrollHeight, 100) + 'px';
        });
    }

    toggleMinimize() {
        this.isMinimized = !this.isMinimized;
        if (this.isMinimized) {
            this.element.classList.add('minimized');
        } else {
            this.element.classList.remove('minimized');
            this.element.querySelector('.chat-input').focus();
        }
    }

    focus() {
        if (this.isMinimized) {
            this.toggleMinimize();
        }
        this.element.querySelector('.chat-input').focus();

        // 閃爍效果提示用戶
        this.element.style.animation = 'none';
        setTimeout(() => {
            this.element.style.animation = 'pulse 0.5s';
        }, 10);
    }

    sendMessage() {
        const input = this.element.querySelector('.chat-input');
        const message = input.value.trim();

        if (!message) return;

        // 發送訊息
        const success = this.manager.sendMessage(this.username, message);

        if (success) {
            // 清空輸入框
            input.value = '';
            input.style.height = 'auto';

            // 不要立即顯示訊息，等 WebSocket 回應
            // WebSocket 會廣播給房間內所有人（包括自己）
            // 這樣可以避免重複顯示

            // 停止打字指示器
            this.manager.sendTyping(this.username, false);
        } else {
            alert('訊息發送失敗，請檢查網路連接');
        }
    }

    handleTyping() {
        // 發送打字中狀態
        this.manager.sendTyping(this.username, true);

        // 3 秒後自動取消打字狀態
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.manager.sendTyping(this.username, false);
        }, 3000);
    }

    loadHistory(messages) {
        const messagesDiv = this.element.querySelector('.chat-messages');
        messagesDiv.innerHTML = '';

        if (messages.length === 0) {
            messagesDiv.innerHTML = `
                <div class="chat-empty-state">
                    <div class="empty-icon">💬</div>
                    <div class="empty-text">開始對話吧！</div>
                </div>
            `;
            return;
        }

        messages.forEach(msg => {
            this.addMessage(msg, false);
        });

        // 滾動到底部
        this.scrollToBottom();

        // 刷新聊天中心的未讀數（因為剛才標記為已讀）
        if (window.chatCenterManager) {
            window.chatCenterManager.refresh();
        }
    }

    addMessage(message, shouldScroll = true) {
        const messagesDiv = this.element.querySelector('.chat-messages');

        // 移除載入中和空白狀態
        const loading = messagesDiv.querySelector('.chat-loading');
        const emptyState = messagesDiv.querySelector('.chat-empty-state');
        if (loading) loading.remove();
        if (emptyState) emptyState.remove();

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${message.sender === 'me' ? 'sent' : 'received'}`;

        const time = new Date(message.timestamp);
        const timeStr = time.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' });

        messageDiv.innerHTML = `
            <div class="message-bubble">${this.escapeHtml(message.content)}</div>
            <div class="message-time">${timeStr}</div>
        `;

        messagesDiv.appendChild(messageDiv);

        if (shouldScroll) {
            this.scrollToBottom();
        }
    }

    showTyping(isTyping) {
        const messagesDiv = this.element.querySelector('.chat-messages');
        const existingIndicator = messagesDiv.querySelector('.chat-message.typing-indicator-wrapper');

        if (isTyping && !existingIndicator) {
            const indicator = document.createElement('div');
            indicator.className = 'chat-message received typing-indicator-wrapper';
            indicator.innerHTML = `
                <div class="typing-indicator">
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                    <span class="typing-dot"></span>
                </div>
            `;
            messagesDiv.appendChild(indicator);
            this.scrollToBottom();
        } else if (!isTyping && existingIndicator) {
            existingIndicator.remove();
        }
    }

    scrollToBottom() {
        const messagesDiv = this.element.querySelector('.chat-messages');
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    setConnectionStatus(status) {
        const statusDiv = this.element.querySelector('.chat-status');
        const statusText = {
            'connected': '線上',
            'disconnected': '離線',
            'error': '連線錯誤'
        };
        statusDiv.textContent = statusText[status] || '未知';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    remove() {
        this.element.remove();
    }
}

// 初始化即時聊天管理器
document.addEventListener('DOMContentLoaded', () => {
    if (document.body.dataset.userAuthenticated === 'true') {
        window.instantChatManager = new InstantChatManager();
    }
});
