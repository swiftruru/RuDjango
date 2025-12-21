/**
 * 會員個人資料頁面 JavaScript
 * 處理分享功能和互動行為
 */

document.addEventListener('DOMContentLoaded', function () {
    const shareBtn = document.getElementById('share-btn');
    const shareMenu = document.getElementById('share-menu');
    const shareClose = document.getElementById('share-close');
    const shareButtons = document.querySelectorAll('.share-button');

    // 從 DOM 中獲取當前頁面資訊
    const memberUsernameElement = document.querySelector('[data-member-username]');
    const memberNameElement = document.querySelector('[data-member-name]');
    const memberBioElement = document.querySelector('[data-member-bio]');

    // 當前頁面的 URL 和標題
    const currentUrl = memberUsernameElement ?
        window.location.origin + memberUsernameElement.dataset.memberUrl :
        window.location.href;
    const pageTitle = memberNameElement ?
        `${memberNameElement.dataset.memberName} 的個人資料 - RuDjango` :
        'RuDjango 會員資料';
    const pageDescription = memberBioElement ?
        memberBioElement.dataset.memberBio :
        '查看我的個人資料';

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
        shareMenu.style.display = 'none';
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
        closeShareMenu();
    }

    /**
     * Twitter 分享
     */
    function shareTwitter() {
        const twitterUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(currentUrl)}&text=${encodeURIComponent(pageTitle)}`;
        window.open(twitterUrl, '_blank', 'width=600,height=400');
        closeShareMenu();
    }

    /**
     * LINE 分享
     */
    function shareLine() {
        const lineUrl = `https://social-plugins.line.me/lineit/share?url=${encodeURIComponent(currentUrl)}`;
        window.open(lineUrl, '_blank', 'width=600,height=400');
        closeShareMenu();
    }

    /**
     * 複製連結
     */
    function copyLink() {
        // 使用現代的 Clipboard API
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(currentUrl).then(function () {
                showCopySuccess();
            }).catch(function (err) {
                // 降級方案
                fallbackCopyLink();
            });
        } else {
            // 降級方案
            fallbackCopyLink();
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

    // ===== 頭像預覽功能 =====
    initAvatarPreview();
});

/**
 * 初始化頭像預覽功能
 */
function initAvatarPreview() {
    const avatarContainer = document.getElementById('avatar-container');
    const profileAvatar = document.getElementById('profile-avatar');
    const avatarModal = document.getElementById('avatar-modal');
    const avatarModalOverlay = avatarModal ? avatarModal.querySelector('.avatar-modal-overlay') : null;
    const closeAvatarModalBtn = document.getElementById('close-avatar-modal');

    if (!avatarContainer || !avatarModal) return;

    // 點擊頭像打開預覽
    avatarContainer.addEventListener('click', function() {
        openAvatarModal();
    });

    // 點擊關閉按鈕
    if (closeAvatarModalBtn) {
        closeAvatarModalBtn.addEventListener('click', function() {
            closeAvatarModal();
        });
    }

    // 點擊背景關閉
    if (avatarModalOverlay) {
        avatarModalOverlay.addEventListener('click', function() {
            closeAvatarModal();
        });
    }

    // ESC 鍵關閉
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && avatarModal.style.display !== 'none') {
            closeAvatarModal();
        }
    });

    /**
     * 打開頭像預覽模態框
     */
    function openAvatarModal() {
        avatarModal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // 防止背景滾動

        // 添加動畫效果
        setTimeout(() => {
            avatarModal.style.opacity = '1';
        }, 10);
    }

    /**
     * 關閉頭像預覽模態框
     */
    function closeAvatarModal() {
        avatarModal.style.opacity = '0';

        setTimeout(() => {
            avatarModal.style.display = 'none';
            document.body.style.overflow = ''; // 恢復滾動
        }, 300);
    }
}
