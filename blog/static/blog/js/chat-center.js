/**
 * 即時聊天中心管理器
 * 類似 Facebook Messenger 的聊天列表功能
 */

class ChatCenterManager {
    constructor() {
        this.chatList = [];
        this.filteredChatList = [];
        this.isOpen = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadChatList();
    }

    setupEventListeners() {
        // 切換聊天中心顯示/隱藏
        const toggleButton = document.getElementById('chat-center-toggle');
        const closeButton = document.getElementById('chat-center-close');
        const dropdown = document.getElementById('chat-center-dropdown');

        if (toggleButton) {
            toggleButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggle();
            });
        }

        if (closeButton) {
            closeButton.addEventListener('click', () => {
                this.close();
            });
        }

        // 點擊外部關閉
        document.addEventListener('click', (e) => {
            if (dropdown && this.isOpen) {
                const isClickInside = dropdown.contains(e.target) ||
                                     (toggleButton && toggleButton.contains(e.target));
                if (!isClickInside) {
                    this.close();
                }
            }
        });

        // 搜尋功能
        const searchInput = document.getElementById('chat-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.filterChats(e.target.value);
            });
        }
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        const dropdown = document.getElementById('chat-center-dropdown');
        if (dropdown) {
            dropdown.classList.add('active');
            this.isOpen = true;
            this.loadChatList(); // 每次開啟時重新載入
        }
    }

    close() {
        const dropdown = document.getElementById('chat-center-dropdown');
        if (dropdown) {
            dropdown.classList.remove('active');
            this.isOpen = false;
        }
    }

    async loadChatList() {
        const listContainer = document.getElementById('chat-center-list');
        if (!listContainer) return;

        // 顯示載入中
        listContainer.innerHTML = '<div class="chat-center-loading">載入中...</div>';

        try {
            const response = await fetch('/blog/api/chat/list/');
            const data = await response.json();

            if (data.success) {
                this.chatList = data.chats;
                this.filteredChatList = [...this.chatList];
                this.renderChatList();
                this.updateChatBadge();
            } else {
                this.showError('無法載入聊天列表');
            }
        } catch (error) {
            console.error('載入聊天列表失敗:', error);
            this.showError('載入失敗，請重試');
        }
    }

    renderChatList() {
        const listContainer = document.getElementById('chat-center-list');
        if (!listContainer) return;

        // 如果沒有聊天記錄
        if (this.filteredChatList.length === 0) {
            if (this.chatList.length === 0) {
                // 完全沒有聊天記錄
                listContainer.innerHTML = `
                    <div class="chat-center-empty">
                        <div class="chat-center-empty-icon">💬</div>
                        <div class="chat-center-empty-text">尚無聊天記錄</div>
                    </div>
                `;
            } else {
                // 有聊天記錄但搜尋結果為空
                listContainer.innerHTML = `
                    <div class="chat-center-empty">
                        <div class="chat-center-empty-icon">🔍</div>
                        <div class="chat-center-empty-text">找不到符合的聊天對象</div>
                    </div>
                `;
            }
            return;
        }

        // 渲染聊天列表
        listContainer.innerHTML = this.filteredChatList.map(chat => {
            const unreadClass = chat.unread_count > 0 ? 'unread' : '';
            const lastMessagePreview = this.formatMessagePreview(chat);
            const timeAgo = this.formatTimeAgo(chat.last_message.timestamp);

            return `
                <div class="chat-item ${unreadClass}" data-username="${chat.username}" data-user-id="${chat.user_id}">
                    <div class="chat-item-avatar">
                        ${chat.avatar_url
                            ? `<img src="${chat.avatar_url}" alt="${chat.display_name}">`
                            : `<span>${chat.display_name.charAt(0)}</span>`
                        }
                    </div>
                    <div class="chat-item-content">
                        <div class="chat-item-header">
                            <span class="chat-item-name">${this.escapeHtml(chat.display_name)}</span>
                            ${timeAgo ? `<span class="chat-item-time">${timeAgo}</span>` : ''}
                        </div>
                        <div class="chat-item-preview">
                            <span class="chat-item-message">${lastMessagePreview}</span>
                            ${chat.unread_count > 0 ? `<span class="chat-item-badge">${chat.unread_count}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        // 綁定點擊事件
        listContainer.querySelectorAll('.chat-item').forEach(item => {
            item.addEventListener('click', () => {
                const username = item.dataset.username;
                const userId = item.dataset.userId;
                const displayName = item.querySelector('.chat-item-name').textContent;
                const avatarImg = item.querySelector('.chat-item-avatar img');
                const avatarUrl = avatarImg ? avatarImg.src : null;

                this.openChatWindow(username, userId, displayName, avatarUrl);
                this.close();
            });
        });
    }

    formatMessagePreview(chat) {
        if (!chat.last_message.content) {
            return '<i>尚無訊息</i>';
        }

        const prefix = chat.last_message.is_from_me ? '你：' : '';
        const content = this.escapeHtml(chat.last_message.content);
        const maxLength = 30;

        if (content.length > maxLength) {
            return `${prefix}${content.substring(0, maxLength)}...`;
        }

        return `${prefix}${content}`;
    }

    formatTimeAgo(timestamp) {
        if (!timestamp) return '';

        const now = new Date();
        const messageTime = new Date(timestamp);
        const diffMs = now - messageTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 1) return '剛剛';
        if (diffMins < 60) return `${diffMins} 分鐘前`;
        if (diffHours < 24) return `${diffHours} 小時前`;
        if (diffDays < 7) return `${diffDays} 天前`;

        // 超過 7 天顯示日期
        const month = messageTime.getMonth() + 1;
        const day = messageTime.getDate();
        return `${month}/${day}`;
    }

    filterChats(query) {
        const lowerQuery = query.toLowerCase().trim();

        if (!lowerQuery) {
            this.filteredChatList = [...this.chatList];
        } else {
            this.filteredChatList = this.chatList.filter(chat => {
                return chat.display_name.toLowerCase().includes(lowerQuery) ||
                       chat.username.toLowerCase().includes(lowerQuery) ||
                       chat.last_message.content.toLowerCase().includes(lowerQuery);
            });
        }

        this.renderChatList();
    }

    updateChatBadge() {
        const badge = document.getElementById('chat-count');
        if (!badge) return;

        const totalUnread = this.chatList.reduce((sum, chat) => sum + chat.unread_count, 0);

        if (totalUnread > 0) {
            badge.textContent = totalUnread > 99 ? '99+' : totalUnread;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    openChatWindow(username, userId, displayName, avatarUrl) {
        // 整合現有的即時聊天視窗系統
        if (window.instantChatManager) {
            window.instantChatManager.openChatWindow(username, userId, displayName, avatarUrl);
        } else {
            console.error('即時聊天管理器未初始化');
        }
    }

    showError(message) {
        const listContainer = document.getElementById('chat-center-list');
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="chat-center-empty">
                    <div class="chat-center-empty-icon">⚠️</div>
                    <div class="chat-center-empty-text">${this.escapeHtml(message)}</div>
                </div>
            `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // 公開方法：供外部更新聊天列表（例如收到新訊息時）
    refresh() {
        if (this.isOpen) {
            this.loadChatList();
        } else {
            // 僅更新未讀數徽章
            this.loadChatList().then(() => {
                this.updateChatBadge();
            });
        }
    }
}

// 初始化聊天中心管理器
document.addEventListener('DOMContentLoaded', function() {
    if (document.body.dataset.userAuthenticated === 'true') {
        window.chatCenterManager = new ChatCenterManager();
    }
});
