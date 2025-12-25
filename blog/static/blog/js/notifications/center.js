/**
 * 通知中心 JavaScript
 * 處理通知的互動功能
 */

(function() {
    'use strict';

    // 初始化
    document.addEventListener('DOMContentLoaded', function() {
        initMarkReadForms();
        initDeleteForms();
    });

    /**
     * 初始化標記為已讀表單
     */
    function initMarkReadForms() {
        const markReadForms = document.querySelectorAll('.mark-read-form');
        markReadForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                handleMarkAsRead(this);
            });
        });
    }

    /**
     * 處理標記為已讀
     */
    async function handleMarkAsRead(form) {
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(form)
            });

            const data = await response.json();

            if (data.success) {
                // 找到通知項目並移除 unread 類別
                const notificationItem = form.closest('.notification-item');
                if (notificationItem) {
                    notificationItem.classList.remove('unread');
                    // 移除標記為已讀按鈕
                    form.remove();
                }

                // 更新未讀數量（如果有的話）
                updateUnreadCount(data.unread_count);
            }
        } catch (error) {
            console.error('標記為已讀失敗:', error);
        }
    }

    /**
     * 初始化刪除表單
     */
    function initDeleteForms() {
        const deleteForms = document.querySelectorAll('.delete-form');
        deleteForms.forEach(form => {
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                if (confirm('確定要刪除此通知嗎？')) {
                    handleDelete(this);
                }
            });
        });
    }

    /**
     * 處理刪除通知
     */
    async function handleDelete(form) {
        try {
            const response = await fetch(form.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: new FormData(form)
            });

            const data = await response.json();

            if (data.success) {
                // 找到通知項目並添加淡出動畫
                const notificationItem = form.closest('.notification-item');
                if (notificationItem) {
                    notificationItem.style.opacity = '0';
                    notificationItem.style.transform = 'translateX(-20px)';

                    setTimeout(() => {
                        notificationItem.remove();

                        // 檢查是否還有通知
                        const remainingItems = document.querySelectorAll('.notification-item');
                        if (remainingItems.length === 0) {
                            showNoNotifications();
                        }
                    }, 300);
                }

                // 更新未讀數量
                updateUnreadCount(data.unread_count);
            }
        } catch (error) {
            console.error('刪除通知失敗:', error);
        }
    }

    /**
     * 更新未讀數量
     */
    function updateUnreadCount(count) {
        // 更新導航欄的通知數量（如果有的話）
        const badges = document.querySelectorAll('.notification-badge');
        badges.forEach(badge => {
            if (count > 0) {
                badge.textContent = count;
                badge.style.display = 'block';
            } else {
                badge.style.display = 'none';
            }
        });

        // 更新篩選器標籤中的數量
        const allTab = document.querySelector('.filter-tab[href*="filter=all"]');
        if (allTab && count !== undefined) {
            const text = allTab.textContent.replace(/\(\d+\)/, `(${count})`);
            allTab.textContent = text;
        }
    }

    /**
     * 顯示無通知狀態
     */
    function showNoNotifications() {
        const notificationsList = document.querySelector('.notifications-list');
        if (notificationsList) {
            notificationsList.innerHTML = `
                <div class="no-notifications">
                    <div class="no-notifications-icon">🔔</div>
                    <p>沒有通知</p>
                </div>
            `;
        }
    }

    /**
     * 導出公共 API
     */
    window.NotificationCenter = {
        updateUnreadCount: updateUnreadCount
    };
})();
