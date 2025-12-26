/**
 * @Mention 自動完成功能
 * 類似 Facebook 的使用者提及功能
 */

class MentionAutocomplete {
    constructor(textareaId, options = {}) {
        this.textarea = document.getElementById(textareaId);
        if (!this.textarea) {
            console.error(`Textarea with id "${textareaId}" not found`);
            return;
        }

        // 防止重複初始化
        if (this.textarea._mentionAutocomplete) {
            console.log(`MentionAutocomplete already initialized for #${textareaId}`);
            return this.textarea._mentionAutocomplete;
        }

        // 設定選項
        this.options = {
            searchUrl: options.searchUrl || '/blog/api/mentions/search-users/',
            minChars: 1,  // 最少輸入幾個字才開始搜尋
            maxResults: 10,  // 最多顯示幾個結果
            ...options
        };

        // 建立下拉選單元素
        this.dropdown = null;
        this.users = [];
        this.selectedIndex = -1;
        this.mentionStartPos = -1;
        this.searchQuery = '';

        this.init();

        // 標記已初始化
        this.textarea._mentionAutocomplete = this;
    }

    init() {
        // 建立下拉選單
        this.createDropdown();

        // 綁定事件
        this.textarea.addEventListener('input', this.handleInput.bind(this));
        this.textarea.addEventListener('keydown', this.handleKeydown.bind(this));

        // 點擊外部關閉下拉選單
        document.addEventListener('click', (e) => {
            if (!this.dropdown.contains(e.target) && e.target !== this.textarea) {
                this.hideDropdown();
            }
        });
    }

    createDropdown() {
        // 建立下拉選單容器
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'mention-dropdown';
        this.dropdown.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            max-height: 300px;
            overflow-y: auto;
            display: none;
            z-index: 1000;
            min-width: 250px;
        `;

        // 插入到頁面中
        document.body.appendChild(this.dropdown);
    }

    handleInput(e) {
        const text = this.textarea.value;
        const cursorPos = this.textarea.selectionStart;

        // 檢查是否輸入了 @
        const beforeCursor = text.substring(0, cursorPos);
        const match = beforeCursor.match(/@(\w*)$/);

        console.log('Input event - beforeCursor:', beforeCursor);
        console.log('Match result:', match);

        if (match) {
            // 找到 @ 符號
            this.mentionStartPos = cursorPos - match[0].length;
            this.searchQuery = match[1];

            console.log('Found @ at position:', this.mentionStartPos);
            console.log('Search query:', this.searchQuery);

            if (this.searchQuery.length >= this.options.minChars) {
                // 搜尋使用者
                this.searchUsers(this.searchQuery);
            } else if (this.searchQuery.length === 0) {
                // 顯示所有使用者
                console.log('Showing all users');
                this.searchUsers('');
            } else {
                this.hideDropdown();
            }
        } else {
            // 沒有找到 @，隱藏下拉選單
            this.hideDropdown();
        }
    }

    handleKeydown(e) {
        if (!this.dropdown.style.display || this.dropdown.style.display === 'none') {
            return;
        }

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectNext();
                break;
            case 'ArrowUp':
                e.preventDefault();
                this.selectPrevious();
                break;
            case 'Enter':
            case 'Tab':
                if (this.selectedIndex >= 0) {
                    e.preventDefault();
                    this.insertMention(this.users[this.selectedIndex]);
                }
                break;
            case 'Escape':
                e.preventDefault();
                this.hideDropdown();
                break;
        }
    }

    async searchUsers(query) {
        try {
            console.log('Searching users with query:', query);
            const url = `${this.options.searchUrl}?q=${encodeURIComponent(query)}`;
            console.log('API URL:', url);

            const response = await fetch(url);
            console.log('Response status:', response.status);

            const data = await response.json();
            console.log('Response data:', data);

            this.users = data.users || [];
            console.log('Found users:', this.users.length);

            this.showDropdown();
        } catch (error) {
            console.error('Error searching users:', error);
            this.hideDropdown();
        }
    }

    showDropdown() {
        if (this.users.length === 0) {
            this.hideDropdown();
            return;
        }

        // 清空現有內容
        this.dropdown.innerHTML = '';

        // 建立使用者列表
        this.users.forEach((user, index) => {
            const item = document.createElement('div');
            item.className = 'mention-item';
            item.style.cssText = `
                padding: 10px 15px;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 10px;
                transition: background-color 0.2s;
            `;

            // 使用者資訊
            item.innerHTML = `
                <div class="user-avatar" style="
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                ">
                    ${user.display_name.charAt(0).toUpperCase()}
                </div>
                <div class="user-info" style="flex: 1;">
                    <div style="font-weight: 500; color: #333;">
                        ${user.display_name}
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        @${user.username}
                    </div>
                </div>
            `;

            // 滑鼠懸停效果
            item.addEventListener('mouseenter', () => {
                this.selectedIndex = index;
                this.updateSelection();
            });

            // 點擊選擇
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.insertMention(user);
            });

            this.dropdown.appendChild(item);
        });

        // 定位下拉選單
        this.positionDropdown();

        // 顯示下拉選單
        this.dropdown.style.display = 'block';
        this.selectedIndex = 0;
        this.updateSelection();
    }

    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
        this.users = [];
    }

    positionDropdown() {
        // 獲取 textarea 的位置（相對於視窗）
        const rect = this.textarea.getBoundingClientRect();

        // 獲取頁面滾動位置
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        // 計算絕對位置（加上滾動偏移量）
        const left = rect.left + scrollLeft;
        const top = rect.bottom + scrollTop + 5;

        // 設定下拉選單位置
        this.dropdown.style.left = `${left}px`;
        this.dropdown.style.top = `${top}px`;
    }

    selectNext() {
        if (this.selectedIndex < this.users.length - 1) {
            this.selectedIndex++;
            this.updateSelection();
            this.scrollToSelected();
        }
    }

    selectPrevious() {
        if (this.selectedIndex > 0) {
            this.selectedIndex--;
            this.updateSelection();
            this.scrollToSelected();
        }
    }

    updateSelection() {
        const items = this.dropdown.querySelectorAll('.mention-item');
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.style.backgroundColor = '#f0f0f0';
            } else {
                item.style.backgroundColor = 'white';
            }
        });
    }

    scrollToSelected() {
        const items = this.dropdown.querySelectorAll('.mention-item');
        const selectedItem = items[this.selectedIndex];
        if (selectedItem) {
            selectedItem.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
        }
    }

    insertMention(user) {
        const text = this.textarea.value;
        const mentionText = `@${user.username} `;

        // 插入提及
        const before = text.substring(0, this.mentionStartPos);
        const after = text.substring(this.textarea.selectionStart);
        const newText = before + mentionText + after;

        this.textarea.value = newText;

        // 設定游標位置
        const newCursorPos = this.mentionStartPos + mentionText.length;
        this.textarea.setSelectionRange(newCursorPos, newCursorPos);

        // 觸發 input 事件（讓其他監聽器知道內容改變了）
        this.textarea.dispatchEvent(new Event('input', { bubbles: true }));

        // 隱藏下拉選單
        this.hideDropdown();

        // 聚焦回 textarea
        this.textarea.focus();
    }

    destroy() {
        // 移除事件監聽器和 DOM 元素
        if (this.dropdown && this.dropdown.parentNode) {
            this.dropdown.parentNode.removeChild(this.dropdown);
        }
    }
}

// 自動初始化（可選）
document.addEventListener('DOMContentLoaded', () => {
    // 自動為所有帶有 data-mention-autocomplete 屬性的 textarea 啟用功能
    document.querySelectorAll('textarea[data-mention-autocomplete]').forEach(textarea => {
        const searchUrl = textarea.dataset.searchUrl || '/blog/api/mentions/search-users/';
        new MentionAutocomplete(textarea.id, {
            searchUrl: searchUrl
        });
    });
});

// 匯出供外部使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MentionAutocomplete;
}
