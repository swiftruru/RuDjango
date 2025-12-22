/**
 * 會員追蹤功能
 * 處理追蹤按鈕的點擊事件和狀態更新
 */

document.addEventListener('DOMContentLoaded', function() {
    const followBtn = document.getElementById('follow-btn');

    if (!followBtn) {
        return; // 如果沒有追蹤按鈕，則不執行
    }

    followBtn.addEventListener('click', function() {
        const username = this.dataset.username;
        const isFollowing = this.dataset.following === 'true';

        // 禁用按鈕防止重複點擊
        followBtn.disabled = true;

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
                const followIcon = followBtn.querySelector('.follow-icon');
                const followText = followBtn.querySelector('.follow-text');

                if (data.is_following) {
                    // 已追蹤狀態
                    followBtn.classList.remove('btn-primary');
                    followBtn.classList.add('btn-secondary');
                    followIcon.textContent = '✓';
                    followText.textContent = '已追蹤';
                    followBtn.dataset.following = 'true';
                } else {
                    // 取消追蹤狀態
                    followBtn.classList.remove('btn-secondary');
                    followBtn.classList.add('btn-primary');
                    followIcon.textContent = '+';
                    followText.textContent = '追蹤';
                    followBtn.dataset.following = 'false';
                }

                // 更新追蹤者和追蹤中的數量
                updateFollowCounts(data.followers_count, data.following_count);

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
            followBtn.disabled = false;
        });
    });
});

/**
 * 更新追蹤者和追蹤中的數量
 * @param {number} followersCount - 追蹤者數量
 * @param {number} followingCount - 追蹤中數量
 */
function updateFollowCounts(followersCount, followingCount) {
    // 查找所有統計卡片
    const statCards = document.querySelectorAll('.stat-card');

    statCards.forEach(card => {
        const label = card.querySelector('.stat-label');
        const number = card.querySelector('.stat-number');

        if (label && number) {
            if (label.textContent.includes('追蹤者')) {
                number.textContent = followersCount;
            } else if (label.textContent.includes('追蹤中')) {
                number.textContent = followingCount;
            }
        }
    });
}

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
