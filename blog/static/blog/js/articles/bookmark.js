/**
 * 文章收藏功能
 * 處理文章收藏/取消收藏的互動
 */

document.addEventListener('DOMContentLoaded', function() {
    const bookmarkButton = document.getElementById('bookmark-button');

    if (!bookmarkButton) {
        return; // 沒有收藏按鈕，直接返回
    }

    bookmarkButton.addEventListener('click', function() {
        const articleId = this.dataset.articleId;
        const isBookmarked = this.dataset.bookmarked === 'true';

        // 防止重複點擊
        if (this.disabled) return;
        this.disabled = true;

        // 獲取CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // 發送請求
        fetch(`/blog/article/${articleId}/bookmark/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 更新按鈕狀態
                const bookmarkIcon = this.querySelector('.bookmark-icon');
                const newBookmarked = data.bookmarked;

                this.dataset.bookmarked = newBookmarked;

                if (newBookmarked) {
                    this.classList.add('bookmarked');
                    bookmarkIcon.textContent = '🔖';
                    showMessage('收藏成功', 'success');
                } else {
                    this.classList.remove('bookmarked');
                    bookmarkIcon.textContent = '📑';
                    showMessage('已取消收藏', 'info');
                }

                // 更新收藏數量
                updateBookmarkCount(data.bookmark_count);
            } else {
                showMessage(data.error || '操作失敗', 'error');
            }
        })
        .catch(error => {
            console.error('收藏失敗:', error);
            showMessage('網路錯誤，請稍後再試', 'error');
        })
        .finally(() => {
            this.disabled = false;
        });
    });
});

/**
 * 更新收藏數量顯示
 */
function updateBookmarkCount(count) {
    let countDisplay = document.getElementById('bookmark-count');

    if (count > 0) {
        if (!countDisplay) {
            // 創建數量顯示元素
            countDisplay = document.createElement('span');
            countDisplay.id = 'bookmark-count';
            countDisplay.className = 'bookmark-count-display';

            const bookmarkSection = document.querySelector('.article-bookmark-section');
            bookmarkSection.appendChild(countDisplay);
        }
        countDisplay.textContent = `· ${count}`;
    } else {
        // 如果數量為0，移除顯示
        if (countDisplay) {
            countDisplay.remove();
        }
    }
}

/**
 * 顯示提示訊息
 */
function showMessage(message, type = 'info') {
    // 移除現有訊息
    const existingMessage = document.querySelector('.bookmark-message');
    if (existingMessage) {
        existingMessage.remove();
    }

    // 創建新訊息
    const messageDiv = document.createElement('div');
    messageDiv.className = `bookmark-message bookmark-message-${type}`;
    messageDiv.textContent = message;

    // 插入到頁面
    const actionsSection = document.querySelector('.article-actions-section');
    actionsSection.appendChild(messageDiv);

    // 3秒後自動消失
    setTimeout(() => {
        messageDiv.classList.add('fade-out');
        setTimeout(() => messageDiv.remove(), 300);
    }, 3000);
}
