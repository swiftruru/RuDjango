/**
 * 文章點讚功能
 * 處理點讚按鈕的點擊事件和狀態更新
 */

document.addEventListener('DOMContentLoaded', function() {
    const likeButton = document.getElementById('like-button');

    if (!likeButton) {
        return; // 如果沒有點讚按鈕（例如自己的文章），則不執行
    }

    likeButton.addEventListener('click', function() {
        const articleId = this.dataset.articleId;
        const isLiked = this.dataset.liked === 'true';

        // 禁用按鈕防止重複點擊
        likeButton.disabled = true;

        // 發送 POST 請求
        fetch(`/blog/article/${articleId}/like/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 更新按鈕狀態
                const likeText = likeButton.querySelector('.like-text');
                const likeCount = likeButton.querySelector('.like-count');

                if (data.liked) {
                    // 已點讚狀態
                    likeButton.classList.add('liked');
                    likeText.textContent = '已點讚';
                    likeButton.dataset.liked = 'true';
                } else {
                    // 取消點讚狀態
                    likeButton.classList.remove('liked');
                    likeText.textContent = '點讚';
                    likeButton.dataset.liked = 'false';
                }

                // 更新點讚數量
                likeCount.textContent = data.like_count;

                // 顯示提示訊息（可選）
                showMessage(data.message);
            } else {
                // 顯示錯誤訊息
                showMessage(data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('操作失敗，請稍後再試', 'error');
        })
        .finally(() => {
            // 重新啟用按鈕
            likeButton.disabled = false;
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
 * 顯示提示訊息
 * @param {string} message - 訊息內容
 * @param {string} type - 訊息類型 ('success' 或 'error')
 */
function showMessage(message, type = 'success') {
    // 創建訊息元素
    const messageDiv = document.createElement('div');
    messageDiv.className = `like-message ${type}`;
    messageDiv.textContent = message;

    // 添加到頁面
    document.body.appendChild(messageDiv);

    // 顯示動畫
    setTimeout(() => {
        messageDiv.classList.add('show');
    }, 10);

    // 3秒後自動消失
    setTimeout(() => {
        messageDiv.classList.remove('show');
        setTimeout(() => {
            messageDiv.remove();
        }, 300);
    }, 3000);
}
