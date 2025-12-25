/**
 * 頁面載入動畫控制
 * 管理頁面載入時的動畫效果
 */

(function() {
    'use strict';

    // 配置選項
    const config = {
        minDisplayTime: 500,  // 最小顯示時間（毫秒）
        fadeOutDuration: 500,  // 淡出動畫時長
        showLoader: true,      // 是否顯示載入器
    };

    // 頁面載入開始時間
    const loadStartTime = Date.now();

    /**
     * 隱藏載入器
     */
    function hideLoader() {
        const loader = document.getElementById('page-loader');
        if (!loader) return;

        // 計算已經過的時間
        const elapsedTime = Date.now() - loadStartTime;
        const remainingTime = Math.max(0, config.minDisplayTime - elapsedTime);

        // 確保載入器至少顯示最小時間
        setTimeout(() => {
            loader.classList.add('hidden');

            // 載入器完全隱藏後移除 DOM 元素
            setTimeout(() => {
                if (loader.parentNode) {
                    loader.parentNode.removeChild(loader);
                }
            }, config.fadeOutDuration);
        }, remainingTime);
    }

    /**
     * 顯示載入器
     */
    function showLoader() {
        // 檢查是否已存在載入器
        let loader = document.getElementById('page-loader');
        if (loader) {
            loader.classList.remove('hidden');
            return;
        }

        // 創建載入器元素
        loader = createLoader();
        document.body.insertBefore(loader, document.body.firstChild);
    }

    /**
     * 創建載入器 HTML 結構
     */
    function createLoader() {
        const loader = document.createElement('div');
        loader.id = 'page-loader';
        loader.className = 'page-loader';
        loader.innerHTML = `
            <div class="loader-content">
                <div class="loader-logo">RuDjango</div>
                <div class="loader-spinner"></div>
                <div class="loader-text">載入中...</div>
                <div class="loader-subtext">精彩內容即將呈現</div>
                <div class="loader-progress">
                    <div class="loader-progress-bar"></div>
                </div>
            </div>
        `;
        return loader;
    }

    /**
     * 創建簡約版載入器（頂部進度條）
     */
    function createSimpleLoader() {
        const loader = document.createElement('div');
        loader.id = 'simple-loader';
        loader.className = 'simple-loader';
        loader.innerHTML = '<div class="simple-loader-bar"></div>';
        return loader;
    }

    /**
     * 顯示簡約載入器
     */
    function showSimpleLoader() {
        let loader = document.getElementById('simple-loader');
        if (!loader) {
            loader = createSimpleLoader();
            document.body.insertBefore(loader, document.body.firstChild);
        }
    }

    /**
     * 隱藏簡約載入器
     */
    function hideSimpleLoader() {
        const loader = document.getElementById('simple-loader');
        if (loader && loader.parentNode) {
            loader.parentNode.removeChild(loader);
        }
    }

    /**
     * 監聽頁面載入完成
     */
    function onPageLoad() {
        hideLoader();
    }

    /**
     * 監聽頁面離開（導航到其他頁面）
     */
    function onPageUnload() {
        // 只在內部連結導航時顯示簡約載入器
        if (document.activeElement && document.activeElement.tagName === 'A') {
            const href = document.activeElement.getAttribute('href');
            // 檢查是否為內部連結
            if (href && !href.startsWith('http') && !href.startsWith('//')) {
                showSimpleLoader();
            }
        }
    }

    /**
     * 為所有內部連結添加載入器
     */
    function attachLinkLoaders() {
        const links = document.querySelectorAll('a[href^="/"], a[href^="?"]');
        links.forEach(link => {
            // 跳過 AJAX 連結和特殊連結
            if (link.hasAttribute('data-ajax') ||
                link.getAttribute('target') === '_blank' ||
                link.classList.contains('no-loader')) {
                return;
            }

            link.addEventListener('click', function(e) {
                // 不是命令鍵/控制鍵點擊（新標籤打開）
                if (!e.ctrlKey && !e.metaKey && !e.shiftKey) {
                    showSimpleLoader();
                }
            });
        });
    }

    /**
     * 預載入關鍵資源
     */
    function preloadResources() {
        // 預載入圖片
        const images = document.querySelectorAll('img[data-src]');
        images.forEach(img => {
            const src = img.getAttribute('data-src');
            if (src) {
                img.src = src;
                img.removeAttribute('data-src');
            }
        });
    }

    /**
     * 初始化
     */
    function init() {
        // 頁面載入完成事件
        if (document.readyState === 'complete') {
            onPageLoad();
        } else {
            window.addEventListener('load', onPageLoad);
        }

        // 頁面卸載事件
        window.addEventListener('beforeunload', onPageUnload);

        // DOM 載入完成後執行
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                attachLinkLoaders();
                preloadResources();
            });
        } else {
            attachLinkLoaders();
            preloadResources();
        }

        // 監聽 AJAX 請求（如果使用 fetch）
        if (window.fetch) {
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                // 只在非無限滾動的請求時顯示載入器
                if (!args[1] || !args[1].headers ||
                    !args[1].headers['X-Requested-With']) {
                    // 這是普通請求，不顯示載入器
                }
                return originalFetch.apply(this, args);
            };
        }
    }

    // 導出公共方法
    window.PageLoader = {
        show: showLoader,
        hide: hideLoader,
        showSimple: showSimpleLoader,
        hideSimple: hideSimpleLoader
    };

    // 初始化
    init();
})();
