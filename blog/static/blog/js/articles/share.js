/**
 * 文章分享功能 JavaScript
 * 處理文章分享到社群平台的功能
 */

// 防止重複初始化
if (window.shareModuleInitialized) {
    // 已初始化，跳過
} else {
    window.shareModuleInitialized = true;

document.addEventListener('DOMContentLoaded', function () {
    const shareBtn = document.getElementById('share-article-btn');
    const shareMenu = document.getElementById('share-article-menu');
    const shareClose = document.getElementById('share-article-close');
    const shareButtons = document.querySelectorAll('.share-button');

    // 從 DOM 中獲取文章資訊
    const articleWrapper = document.querySelector('[data-article-url]');

    // 當前頁面的 URL 和標題
    const currentUrl = articleWrapper ?
        window.location.origin + articleWrapper.dataset.articleUrl :
        window.location.href;
    const pageTitle = articleWrapper ?
        `${articleWrapper.dataset.articleTitle} - RuDjango` :
        document.title;
    const pageDescription = articleWrapper ?
        articleWrapper.dataset.articleExcerpt :
        '閱讀這篇精彩的文章';

    /**
     * 開啟分享選單
     */
    if (shareBtn) {
        shareBtn.addEventListener('click', function () {
            shareMenu.style.display = 'flex';
        });
    }

    /**
     * 關閉分享選單
     */
    function closeShareMenu() {
        if (shareMenu) {
            shareMenu.style.display = 'none';
        }
    }

    if (shareClose) {
        shareClose.addEventListener('click', closeShareMenu);
    }

    // 點擊背景關閉
    if (shareMenu) {
        shareMenu.addEventListener('click', function (e) {
            if (e.target === shareMenu) {
                closeShareMenu();
            }
        });
    }

    // ESC 鍵關閉
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && shareMenu && shareMenu.style.display === 'flex') {
            closeShareMenu();
        }
    });

    // 處理分享按鈕
    shareButtons.forEach(button => {
        button.addEventListener('click', function () {
            const platform = this.dataset.platform;

            switch (platform) {
                case 'facebook':
                    shareFacebook();
                    break;
                case 'twitter':
                    shareTwitter();
                    break;
                case 'line':
                    shareLine();
                    break;
                case 'copy':
                    copyLink();
                    break;
            }
        });
    });

    /**
     * Facebook 分享
     */
    function shareFacebook() {
        const fbUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`;
        window.open(fbUrl, '_blank', 'width=600,height=400');
        recordShare('facebook');
        closeShareMenu();
    }

    /**
     * Twitter 分享
     */
    function shareTwitter() {
        const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(pageTitle)}`;
        window.open(twitterUrl, '_blank', 'width=600,height=400');
        recordShare('twitter');
        closeShareMenu();
    }

    /**
     * LINE 分享
     */
    function shareLine() {
        const lineUrl = `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(currentUrl)}`;
        window.open(lineUrl, '_blank', 'width=600,height=400');
        recordShare('line');
        closeShareMenu();
    }

    /**
     * 複製連結
     */
    function copyLink() {
        // 使用現代的 Clipboard API
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(currentUrl).then(function () {
                recordShare('copy');
                showCopySuccess();
            }).catch(function (err) {
                // 降級方案（Clipboard API 失敗時）
                fallbackCopyLink();
            });
        } else {
            // 降級方案（不支援 Clipboard API）
            fallbackCopyLink();
        }
    }

    /**
     * 記錄分享統計
     * 使用防抖機制避免重複提交
     */
    let lastShareTime = 0;
    const shareDebounceDelay = 1000; // 1秒內不重複提交

    function recordShare(platform) {
        const articleWrapper = document.querySelector('[data-article-id]');
        if (!articleWrapper) return;

        // 防抖檢查：避免短時間內重複提交相同平台的分享
        const now = Date.now();
        if (now - lastShareTime < shareDebounceDelay) {
            return;
        }
        lastShareTime = now;

        const articleId = articleWrapper.dataset.articleId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

        if (!csrfToken) return;

        fetch(`/blog/article/${articleId}/share/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            credentials: 'same-origin',
            body: `platform=${platform}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 更新頁面上的分享數量
                updateShareCount(data.share_count);
            }
        })
        .catch(error => {
            console.error('記錄分享失敗:', error);
        });
    }

    /**
     * 更新分享數量顯示
     */
    function updateShareCount(count) {
        const shareStats = document.querySelector('.article-share-stats .share-count');
        if (shareStats) {
            shareStats.textContent = `🔗 ${count} 次分享`;
        } else if (count > 0) {
            // 如果不存在，創建分享統計顯示
            const actionsSection = document.querySelector('.article-actions-section');
            if (actionsSection) {
                const shareStatsDiv = document.createElement('div');
                shareStatsDiv.className = 'article-share-stats';
                shareStatsDiv.innerHTML = `<span class="share-count">🔗 ${count} 次分享</span>`;
                actionsSection.appendChild(shareStatsDiv);
            }
        }
    }

    /**
     * 降級的複製方案（for 舊瀏覽器）
     */
    function fallbackCopyLink() {
        const textArea = document.createElement('textarea');
        textArea.value = currentUrl;
        textArea.style.position = 'fixed';
        textArea.style.left = '-9999px';
        document.body.appendChild(textArea);
        textArea.select();

        try {
            document.execCommand('copy');
            recordShare('copy');
            showCopySuccess();
        } catch (err) {
            alert('複製失敗，請手動複製：' + currentUrl);
        }

        document.body.removeChild(textArea);
    }

    /**
     * 顯示複製成功提示
     */
    function showCopySuccess() {
        const copyButton = document.querySelector('.share-button.copy-link');
        if (!copyButton) return;

        const originalText = copyButton.innerHTML;

        copyButton.innerHTML = '<span class="share-icon" style="background: #10b981;">✓</span>已複製！';
        copyButton.style.borderColor = '#10b981';
        copyButton.style.color = '#10b981';

        setTimeout(function () {
            copyButton.innerHTML = originalText;
            copyButton.style.borderColor = '';
            copyButton.style.color = '';
            closeShareMenu();
        }, 1500);
    }
});

} // 結束防止重複初始化的 else 區塊
