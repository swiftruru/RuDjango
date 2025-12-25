/**
 * 無限滾動功能
 * 當用戶滾動到頁面底部時自動載入更多文章
 */

(function() {
    'use strict';

    // 狀態管理
    let currentPage = 1;
    let isLoading = false;
    let hasMorePages = true;
    let isInfiniteScrollMode = true;

    // DOM 元素
    const articlesContainer = document.getElementById('articles-container');
    const loadMoreContainer = document.getElementById('load-more-container');
    const noMoreArticles = document.getElementById('no-more-articles');
    const traditionalPagination = document.getElementById('traditional-pagination');
    const toggleButton = document.getElementById('toggle-pagination-mode');

    // 獲取 URL 參數
    function getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return {
            q: params.get('q') || '',
            search_type: params.get('search_type') || 'all'
        };
    }

    // 載入更多文章
    async function loadMoreArticles() {
        if (isLoading || !hasMorePages) {
            return;
        }

        isLoading = true;
        loadMoreContainer.style.display = 'block';

        // 添加載入動畫類
        loadMoreContainer.classList.add('loading');

        try {
            const params = getUrlParams();
            const nextPage = currentPage + 1;

            // 構建 URL
            const url = new URL(window.location.href);
            url.searchParams.set('page', nextPage);

            // 創建超時控制器（10秒超時）
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000);

            // 發送 AJAX 請求
            const response = await fetch(url.toString(), {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error('網路請求失敗');
            }

            const data = await response.json();

            if (data.success) {
                // 將新文章添加到容器
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = data.html;

                // 先將所有卡片加入 DOM（確保頁面高度立即更新）
                const cards = tempDiv.querySelectorAll('.article-card');
                cards.forEach((card) => {
                    card.style.opacity = '0';
                    card.style.transform = 'translateY(20px)';
                    articlesContainer.appendChild(card);
                });

                // 強制瀏覽器重新計算佈局
                void articlesContainer.offsetHeight;

                // 然後再執行淡入動畫
                cards.forEach((card, index) => {
                    setTimeout(() => {
                        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
                        card.style.opacity = '1';
                        card.style.transform = 'translateY(0)';
                    }, index * 100);
                });

                // 更新狀態
                currentPage = data.current_page;
                hasMorePages = data.has_next;

                // 移除載入動畫類
                loadMoreContainer.classList.remove('loading');

                // 如果沒有更多頁面，顯示提示
                if (!hasMorePages) {
                    setTimeout(() => {
                        loadMoreContainer.style.display = 'none';
                        noMoreArticles.style.display = 'block';
                    }, 300);
                } else {
                    // 載入完成後立即檢查是否需要繼續載入下一頁
                    // 使用 requestAnimationFrame 確保 DOM 更新完成
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => {
                            checkScrollPosition();
                        });
                    });
                }
            } else {
                // 如果伺服器回應 success: false
                console.error('伺服器回應失敗:', data);
                throw new Error(data.message || '載入失敗');
            }
        } catch (error) {
            console.error('載入文章失敗:', error);
            loadMoreContainer.classList.remove('loading');

            // 區分錯誤類型
            const errorMessage = error.name === 'AbortError'
                ? '⏱️ 載入超時，請檢查網路連線'
                : '❌ 載入失敗，請重新整理頁面';

            loadMoreContainer.innerHTML = `
                <div class="load-error">
                    <p>${errorMessage}</p>
                    <button onclick="location.reload()" class="btn-retry">🔄 重試</button>
                </div>
            `;
        } finally {
            isLoading = false;
        }
    }

    // 檢查是否滾動到底部
    function checkScrollPosition() {
        if (!isInfiniteScrollMode) return;

        const scrollHeight = document.documentElement.scrollHeight;
        const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
        const clientHeight = document.documentElement.clientHeight;

        // 當距離底部 1500px 時開始載入（支援快速滾動）
        const threshold = 1500;
        const distanceToBottom = scrollHeight - (scrollTop + clientHeight);

        if (distanceToBottom < threshold && !isLoading && hasMorePages) {
            loadMoreArticles();
        }
    }

    // 節流函數 - 限制函數執行頻率
    function throttle(func, delay) {
        let lastCall = 0;
        return function(...args) {
            const now = new Date().getTime();
            if (now - lastCall < delay) {
                return;
            }
            lastCall = now;
            return func(...args);
        };
    }

    // 切換分頁模式
    function togglePaginationMode() {
        isInfiniteScrollMode = !isInfiniteScrollMode;

        if (isInfiniteScrollMode) {
            // 切換到無限滾動模式
            traditionalPagination.style.display = 'none';
            if (hasMorePages) {
                loadMoreContainer.style.display = 'block';
            } else {
                noMoreArticles.style.display = 'block';
            }
            toggleButton.querySelector('.toggle-text').textContent = '切換為傳統分頁';

            // 切換後立即檢查是否需要載入更多
            setTimeout(checkScrollPosition, 100);
        } else {
            // 切換到傳統分頁模式
            loadMoreContainer.style.display = 'none';
            noMoreArticles.style.display = 'none';
            traditionalPagination.style.display = 'block';
            toggleButton.querySelector('.toggle-text').textContent = '切換為無限滾動';
        }
    }

    // 初始化
    function init() {
        // 從 URL 獲取當前頁碼
        const params = new URLSearchParams(window.location.search);
        const pageParam = params.get('page');
        if (pageParam) {
            currentPage = parseInt(pageParam) || 1;
        }

        // 檢查是否還有更多頁面（從 DOM 狀態判斷）
        if (loadMoreContainer && loadMoreContainer.style.display === 'none' &&
            noMoreArticles && noMoreArticles.style.display !== 'none') {
            hasMorePages = false;
        }

        // 監聽滾動事件（使用節流優化性能，100ms 更靈敏）
        window.addEventListener('scroll', throttle(checkScrollPosition, 100));

        // 切換按鈕事件
        if (toggleButton) {
            toggleButton.addEventListener('click', togglePaginationMode);
        }

        // 初始檢查（處理頁面載入時已在底部的情況）
        setTimeout(checkScrollPosition, 500);
    }

    // DOM 載入完成後初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
