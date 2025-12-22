/**
 * 追蹤列表頁面功能
 * 處理追蹤列表中的追蹤/取消追蹤操作
 */

document.addEventListener('DOMContentLoaded', function() {
    // 獲取所有追蹤按鈕
    const followButtons = document.querySelectorAll('.btn-follow');

    followButtons.forEach(button => {
        // 跳過連結形式的追蹤按鈕（未登入用戶）
        if (button.tagName === 'A') {
            return;
        }

        button.addEventListener('click', function() {
            const username = this.dataset.username;
            const isFollowing = this.dataset.following === 'true';

            // 禁用按鈕防止重複點擊
            this.disabled = true;

            // 發送 POST 請求
            fetch(`/blog/member/${username}/follow/`, {
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
                    const followIcon = this.querySelector('.follow-icon');
                    const followText = this.querySelector('.follow-text');

                    if (data.is_following) {
                        // 已追蹤狀態
                        this.classList.add('following');
                        followIcon.textContent = '✓';
                        followText.textContent = '已追蹤';
                        this.dataset.following = 'true';
                    } else {
                        // 取消追蹤狀態
                        this.classList.remove('following');
                        followIcon.textContent = '+';
                        followText.textContent = '追蹤';
                        this.dataset.following = 'false';
                    }

                    // 顯示提示訊息
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
                this.disabled = false;
            });
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
    messageDiv.className = `follow-message ${type}`;
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
