/**
 * 搜尋建議和搜尋歷史功能
 *
 * 功能：
 * - 即時搜尋建議
 * - 搜尋歷史記錄
 * - 熱門搜尋
 * - 清除搜尋歷史
 */

class SearchSuggestionsManager {
    constructor(inputSelector, suggestionsContainerSelector) {
        this.input = document.querySelector(inputSelector);
        this.suggestionsContainer = document.querySelector(suggestionsContainerSelector);
        this.debounceTimer = null;
        this.currentFocus = -1;

        if (!this.input || !this.suggestionsContainer) {
            console.error('Search input or suggestions container not found');
            return;
        }

        this.init();
    }

    init() {
        // 輸入事件 - 使用 debounce 減少 API 呼叫
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.fetchSuggestions(e.target.value.trim());
            }, 300);
        });

        // 焦點事件 - 顯示搜尋歷史
        this.input.addEventListener('focus', () => {
            if (!this.input.value.trim()) {
                this.fetchSuggestions('');
            } else {
                this.fetchSuggestions(this.input.value.trim());
            }
        });

        // 鍵盤導航
        this.input.addEventListener('keydown', (e) => {
            const items = this.suggestionsContainer.querySelectorAll('.suggestion-item');

            if (e.key === 'ArrowDown') {
                e.preventDefault();
                this.currentFocus++;
                this.setActive(items);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                this.currentFocus--;
                this.setActive(items);
            } else if (e.key === 'Enter') {
                if (this.currentFocus > -1 && items[this.currentFocus]) {
                    e.preventDefault();
                    items[this.currentFocus].click();
                }
                // 如果沒有選中建議項目，讓表單正常提交（不阻止預設行為）
            } else if (e.key === 'Escape') {
                this.hideSuggestions();
            }
        });

        // 點擊外部關閉建議
        document.addEventListener('click', (e) => {
            if (!this.input.contains(e.target) && !this.suggestionsContainer.contains(e.target)) {
                this.hideSuggestions();
            }
        });
    }

    async fetchSuggestions(query) {
        try {
            const response = await fetch(`/blog/api/search/suggestions/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.renderSuggestions(data.suggestions, data.show_history || false);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    }

    renderSuggestions(suggestions, showHistory = false) {
        let html = '';

        // 如果是顯示歷史模式，加入標題和清除按鈕
        if (showHistory) {
            const hasHistory = suggestions.some(s => s.type === 'history');
            const hasPopular = suggestions.some(s => s.type === 'popular');

            if (hasHistory) {
                html += `
                    <div class="suggestions-header">
                        <span class="suggestions-title">🕐 最近搜尋</span>
                        <button class="clear-history-btn" onclick="searchManager.clearHistory()">清除</button>
                    </div>
                `;

                suggestions.filter(s => s.type === 'history').forEach(suggestion => {
                    html += this.createSuggestionItem({...suggestion, icon: ''}, true);
                });
            }

            if (hasPopular) {
                html += `
                    <div class="suggestions-header">
                        <span class="suggestions-title">🔥 熱門搜尋</span>
                    </div>
                `;

                suggestions.filter(s => s.type === 'popular').forEach(suggestion => {
                    html += this.createSuggestionItem({...suggestion, icon: ''}, false);
                });
            }

            // 如果沒有任何記錄，顯示提示
            if (!hasHistory && !hasPopular) {
                html += `
                    <div class="suggestions-empty">
                        💡 尚無搜尋記錄，開始搜尋以建立歷史
                    </div>
                `;
            }
        } else {
            // 一般搜尋建議
            if (suggestions.length === 0) {
                this.hideSuggestions();
                return;
            }

            suggestions.forEach(suggestion => {
                html += this.createSuggestionItem(suggestion, false);
            });
        }

        this.suggestionsContainer.innerHTML = html;
        this.suggestionsContainer.style.display = 'block';
        this.currentFocus = -1;
    }

    createSuggestionItem(suggestion, showDeleteBtn = false) {
        const deleteBtn = showDeleteBtn
            ? `<button class="delete-item-btn" onclick="searchManager.deleteHistoryItem('${this.escapeHtml(suggestion.text)}', event)">×</button>`
            : '';

        const countBadge = suggestion.count
            ? `<span class="search-count">${suggestion.count}</span>`
            : '';

        return `
            <div class="suggestion-item" data-type="${suggestion.type}" data-url="${suggestion.url}" onclick="searchManager.selectSuggestion('${this.escapeHtml(suggestion.text)}', '${suggestion.url}')">
                <span class="suggestion-icon">${suggestion.icon}</span>
                <span class="suggestion-text">${this.highlightMatch(suggestion.text)}</span>
                ${countBadge}
                ${deleteBtn}
            </div>
        `;
    }

    highlightMatch(text) {
        const query = this.input.value.trim();
        if (!query) return this.escapeHtml(text);

        const regex = new RegExp(`(${this.escapeRegex(query)})`, 'gi');
        return this.escapeHtml(text).replace(regex, '<strong>$1</strong>');
    }

    selectSuggestion(text, url) {
        if (url.startsWith('/blog/article/') || url.startsWith('/blog/tag/') || url.startsWith('/blog/member/')) {
            // 直接導航到文章、標籤或作者頁面
            window.location.href = url;
        } else {
            // 執行搜尋
            this.input.value = text;
            this.submitSearch(text);
        }
    }

    submitSearch(query) {
        if (!query) return;
        window.location.href = `/blog/search/?q=${encodeURIComponent(query)}`;
    }

    setActive(items) {
        if (!items.length) return;

        // 移除所有 active 類別
        items.forEach(item => item.classList.remove('active'));

        // 調整索引範圍
        if (this.currentFocus >= items.length) this.currentFocus = 0;
        if (this.currentFocus < 0) this.currentFocus = items.length - 1;

        // 添加 active 類別
        items[this.currentFocus].classList.add('active');
        items[this.currentFocus].scrollIntoView({ block: 'nearest' });
    }

    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
        this.suggestionsContainer.innerHTML = '';
        this.currentFocus = -1;
    }

    async clearHistory() {
        if (!confirm('確定要清除所有搜尋歷史嗎？')) {
            return;
        }

        try {
            const response = await fetch('/blog/api/search/history/clear/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (data.success) {
                this.fetchSuggestions('');
                this.showMessage('已清除搜尋歷史', 'success');
            } else {
                this.showMessage(data.error || '清除失敗', 'error');
            }
        } catch (error) {
            console.error('Error clearing history:', error);
            this.showMessage('清除失敗', 'error');
        }
    }

    async deleteHistoryItem(query, event) {
        event.stopPropagation();

        try {
            const formData = new FormData();
            formData.append('query', query);

            const response = await fetch('/blog/api/search/history/delete/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                this.fetchSuggestions('');
            } else {
                this.showMessage(data.error || '刪除失敗', 'error');
            }
        } catch (error) {
            console.error('Error deleting history item:', error);
            this.showMessage('刪除失敗', 'error');
        }
    }

    showMessage(message, type = 'info') {
        // 簡單的訊息提示（可以改用更好的 toast 通知）
        const messageEl = document.createElement('div');
        messageEl.className = `search-message search-message-${type}`;
        messageEl.textContent = message;
        messageEl.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            background: ${type === 'success' ? '#4CAF50' : '#f44336'};
            color: white;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(messageEl);

        setTimeout(() => {
            messageEl.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => messageEl.remove(), 300);
        }, 3000);
    }

    getCookie(name) {
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

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    escapeRegex(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
}

// 全域變數以供 onclick 使用
let searchManager;

// DOM 載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
    searchManager = new SearchSuggestionsManager(
        '#search-input',
        '#search-suggestions'
    );
});
