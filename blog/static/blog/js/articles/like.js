/**
 * 文章點讚功能
 * 處理點讚按鈕的點擊事件和狀態更新
 */

document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('like-button');
    const ownArticleButton = document.getElementById('like-button-own');

    // 處理自己文章的點讚按鈕
    if (ownArticleButton) {
        ownArticleButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // 顯示提示訊息，不發送請求
            showMessage('不能對自己的文章點讚', 'info');
        });
    }

    if (!likeButton) {
        return; // 如果沒有點讚按鈕（例如自己的文章），則不執行
    }

    // 檢查是否已經綁定過事件（防止 DOMContentLoaded 多次觸發）
    if (likeButton.dataset.listenerAttached === 'true') {
        return;
    }

    likeButton.dataset.listenerAttached = 'true';

    // 防止重複請求的標誌
    let isProcessing = false;

    likeButton.addEventListener('click', function(e) {
        // 防止事件冒泡和預設行為
        e.preventDefault();
        e.stopPropagation();

        // 如果正在處理中，直接返回
        if (isProcessing) {
            return;
        }

        const articleId = this.dataset.articleId;

        // 設置處理標誌和禁用按鈕
        isProcessing = true;
        likeButton.disabled = true;

        // 發送 POST 請求
        fetch(`/blog/article/${articleId}/like/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // 更新按鈕狀態
                const likeIcon = likeButton.querySelector('.like-icon');
                let likeCount = likeButton.querySelector('.like-count');

                if (data.liked) {
                    // 已點讚狀態
                    likeButton.classList.add('liked');
                    likeButton.dataset.liked = 'true';
                    likeIcon.textContent = '❤️';
                } else {
                    // 取消點讚狀態
                    likeButton.classList.remove('liked');
                    likeButton.dataset.liked = 'false';
                    likeIcon.textContent = '🤍';
                }

                // 更新點讚數量
                if (data.like_count > 0) {
                    if (!likeCount) {
                        // 如果 like-count 不存在，創建它
                        likeCount = document.createElement('span');
                        likeCount.className = 'like-count';
                        likeButton.appendChild(likeCount);
                    }
                    likeCount.textContent = `· ${data.like_count}`;
                } else {
                    // 如果點讚數為 0，移除計數顯示
                    if (likeCount) {
                        likeCount.remove();
                    }
                }

                // 顯示提示訊息
                showMessage(data.message);
            } else {
                // 顯示錯誤訊息
                showMessage(data.error || '操作失敗', 'error');
            }
        })
        .catch(() => {
            showMessage('操作失敗，請稍後再試', 'error');
        })
        .finally(() => {
            // 重新啟用按鈕和清除處理標誌
            likeButton.disabled = false;
            isProcessing = false;
        });
    });
});

/**
 * 獲取 Cookie 值
 * @param {string} name - Cookie 名稱
 * @returns {string|null} Cookie 值
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * 顯示提示訊息 (Facebook 風格浮動提示)
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 ('success' 或 'error')
 */
function showMessage(message, type = 'success') {
    // 移除舊的提示訊息（如果存在）
    const existingMessage = document.querySelector('.like-message');
    if (existingMessage) {
        existingMessage.remove();
    }

    // 創建訊息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `like-message ${type}`;
    messageDiv.textContent = message;

    // 直接添加到 body，使用固定定位
    document.body.appendChild(messageDiv);

    // 計算按鈕位置 (優先使用普通按鈕，否則使用自己文章按鈕)
    const likeButton = document.getElementById('like-button') || document.getElementById('like-button-own');
    if (likeButton) {
        const buttonRect = likeButton.getBoundingClientRect();
        messageDiv.style.position = 'fixed';
        messageDiv.style.left = `${buttonRect.left + buttonRect.width / 2}px`;
        messageDiv.style.top = `${buttonRect.top - 50}px`;
        messageDiv.style.transform = 'translateX(-50%) scale(0.9)';
    }

    // 顯示動畫
    setTimeout(() => {
        messageDiv.classList.add('show');
    }, 10);

    // 1.5秒後自動消失（比較短，更低調）
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => {
            messageDiv.remove();
        }, 200);
    }, 1500);
}
