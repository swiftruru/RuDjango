/**
 * 搜尋自動完成功能
 * 提供即時搜尋建議和快速搜尋結果
 */

(function() {
    'use strict';

    // 配置
    const config = {
        minLength: 2,           // 最小觸發長度
        debounceDelay: 300,     // 防抖延遲（毫秒）
        maxSuggestions: 10,     // 最多顯示建議數
    };

    // DOM 元素
    let searchInput = null;
    let suggestionsContainer = null;
    let debounceTimer = null;

    /**
     * 初始化搜尋輸入框
     */
    function initSearchInput(inputElement) {
        searchInput = inputElement;

        // 創建建議容器
        createSuggestionsContainer();

        // 監聽輸入事件
        searchInput.addEventListener('input', handleInput);
        searchInput.addEventListener('focus', handleFocus);
        searchInput.addEventListener('keydown', handleKeyDown);

        // 點擊外部關閉建議
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsContainer.contains(e.target)) {
                hideSuggestions();
            }
        });
    }

    /**
     * 創建建議容器
     */
    function createSuggestionsContainer() {
        suggestionsContainer = document.createElement('div');
        suggestionsContainer.className = 'search-suggestions';
        suggestionsContainer.style.display = 'none';

        // 插入到搜尋框後面
        searchInput.parentNode.style.position = 'relative';
        searchInput.parentNode.appendChild(suggestionsContainer);
    }

    /**
     * 處理輸入事件
     */
    function handleInput(e) {
        const query = e.target.value.trim();

        // 清除之前的計時器
        clearTimeout(debounceTimer);

        if (query.length < config.minLength) {
            hideSuggestions();
            return;
        }

        // 顯示載入狀態
        showLoading();

        // 防抖：延遲執行搜尋
        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, config.debounceDelay);
    }

    /**
     * 處理聚焦事件
     */
    function handleFocus(e) {
        const query = e.target.value.trim();
        if (query.length >= config.minLength && suggestionsContainer.children.length > 0) {
            showSuggestions();
        }
    }

    /**
     * 處理鍵盤事件
     */
    function handleKeyDown(e) {
        const items = suggestionsContainer.querySelectorAll('.suggestion-item');
        const activeItem = suggestionsContainer.querySelector('.suggestion-item.active');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                navigateSuggestions(items, activeItem, 1);
                break;
            case 'ArrowUp':
                e.preventDefault();
                navigateSuggestions(items, activeItem, -1);
                break;
            case 'Enter':
                if (activeItem) {
                    e.preventDefault();
                    activeItem.click();
                }
                break;
            case 'Escape':
                hideSuggestions();
                break;
        }
    }

    /**
     * 導航建議項目
     */
    function navigateSuggestions(items, activeItem, direction) {
        if (items.length === 0) return;

        let currentIndex = -1;
        if (activeItem) {
            currentIndex = Array.from(items).indexOf(activeItem);
            activeItem.classList.remove('active');
        }

        let newIndex = currentIndex + direction;
        if (newIndex < 0) newIndex = items.length - 1;
        if (newIndex >= items.length) newIndex = 0;

        items[newIndex].classList.add('active');
        items[newIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    /**
     * 獲取搜尋建議
     */
    async function fetchSuggestions(query) {
        try {
            const response = await fetch(`/blog/api/search/suggestions/?q=${encodeURIComponent(query)}`);

            if (!response.ok) {
                throw new Error('搜尋請求失敗');
            }

            const data = await response.json();

            if (data.success && data.suggestions.length > 0) {
                displaySuggestions(data.suggestions);
            } else {
                showNoResults();
            }
        } catch (error) {
            console.error('搜尋建議錯誤:', error);
            hideLoading();
        }
    }

    /**
     * 顯示建議
     */
    function displaySuggestions(suggestions) {
        suggestionsContainer.innerHTML = '';

        suggestions.slice(0, config.maxSuggestions).forEach((suggestion, index) => {
            const item = createSuggestionItem(suggestion, index);
            suggestionsContainer.appendChild(item);
        });

        showSuggestions();
    }

    /**
     * 創建建議項目
     */
    function createSuggestionItem(suggestion, index) {
        const item = document.createElement('a');
        item.href = suggestion.url;
        item.className = 'suggestion-item';
        item.innerHTML = `
            <span class="suggestion-icon">${suggestion.icon}</span>
            <div class="suggestion-content">
                <div class="suggestion-text">${highlightMatch(suggestion.text, searchInput.value)}</div>
                <div class="suggestion-type">${getTypeLabel(suggestion.type)}</div>
            </div>
        `;

        // 滑鼠移入高亮
        item.addEventListener('mouseenter', function() {
            const items = suggestionsContainer.querySelectorAll('.suggestion-item');
            items.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });

        return item;
    }

    /**
     * 高亮匹配文字
     */
    function highlightMatch(text, query) {
        if (!query) return text;

        const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }

    /**
     * 轉義正則表達式特殊字符
     */
    function escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    /**
     * 取得類型標籤
     */
    function getTypeLabel(type) {
        const labels = {
            'article': '文章',
            'tag': '標籤',
            'author': '作者'
        };
        return labels[type] || type;
    }

    /**
     * 顯示載入狀態
     */
    function showLoading() {
        suggestionsContainer.innerHTML = `
            <div class="suggestion-loading">
                <div class="loading-spinner"></div>
                <span>搜尋中...</span>
            </div>
        `;
        showSuggestions();
    }

    /**
     * 隱藏載入狀態
     */
    function hideLoading() {
        const loading = suggestionsContainer.querySelector('.suggestion-loading');
        if (loading) {
            suggestionsContainer.innerHTML = '';
            hideSuggestions();
        }
    }

    /**
     * 顯示無結果
     */
    function showNoResults() {
        suggestionsContainer.innerHTML = `
            <div class="suggestion-no-results">
                <span class="no-results-icon">🔍</span>
                <p>找不到相關結果</p>
                <a href="/blog/search/?q=${encodeURIComponent(searchInput.value)}" class="btn-advanced-search">
                    進階搜尋
                </a>
            </div>
        `;
        showSuggestions();
    }

    /**
     * 顯示建議容器
     */
    function showSuggestions() {
        suggestionsContainer.style.display = 'block';
        suggestionsContainer.classList.add('show');
    }

    /**
     * 隱藏建議容器
     */
    function hideSuggestions() {
        suggestionsContainer.style.display = 'none';
        suggestionsContainer.classList.remove('show');
    }

    /**
     * 自動初始化所有搜尋框
     */
    function autoInit() {
        const searchInputs = document.querySelectorAll('.search-input[data-autocomplete="true"]');
        searchInputs.forEach(input => {
            initSearchInput(input);
        });
    }

    // 導出公共 API
    window.SearchAutocomplete = {
        init: initSearchInput,
        autoInit: autoInit
    };

    // DOM 載入完成後自動初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        autoInit();
    }
})();
