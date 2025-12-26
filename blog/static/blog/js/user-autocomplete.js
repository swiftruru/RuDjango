/**
 * 使用者自動完成元件
 * 用於輸入框的使用者名稱自動完成功能
 */

class UserAutocomplete {
    constructor(inputElement) {
        this.input = inputElement;
        this.dropdown = null;
        this.users = [];
        this.selectedIndex = -1;
        this.isLoading = false;

        // 防止重複初始化
        if (this.input._userAutocomplete) {
            console.log(`UserAutocomplete already initialized for #${this.input.id}`);
            return this.input._userAutocomplete;
        }

        // 標記為已初始化
        this.input._userAutocomplete = this;

        console.log(`=== Initializing UserAutocomplete for #${this.input.id} ===`);
        this.init();
    }

    init() {
        // 創建下拉選單
        this.createDropdown();

        // 綁定事件
        this.bindEvents();
    }

    createDropdown() {
        this.dropdown = document.createElement('div');
        this.dropdown.className = 'user-autocomplete-dropdown';
        this.dropdown.style.display = 'none';
        document.body.appendChild(this.dropdown);
    }

    bindEvents() {
        // 輸入事件
        this.input.addEventListener('input', () => {
            this.handleInput();
        });

        // 鍵盤事件
        this.input.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });

        // 失去焦點時隱藏下拉選單
        this.input.addEventListener('blur', () => {
            // 延遲隱藏，以便點擊事件能夠觸發
            setTimeout(() => {
                this.hideDropdown();
            }, 200);
        });

        // 獲得焦點時，如果有值則顯示建議
        this.input.addEventListener('focus', () => {
            if (this.input.value.trim()) {
                this.handleInput();
            }
        });

        // 點擊頁面其他地方時隱藏下拉選單
        document.addEventListener('click', (e) => {
            if (e.target !== this.input && !this.dropdown.contains(e.target)) {
                this.hideDropdown();
            }
        });
    }

    async handleInput() {
        const query = this.input.value.trim();

        // 如果輸入為空，隱藏下拉選單
        if (!query) {
            this.hideDropdown();
            return;
        }

        // 搜尋使用者
        await this.searchUsers(query);
    }

    async searchUsers(query) {
        if (this.isLoading) return;

        this.isLoading = true;

        try {
            const response = await fetch(`/blog/api/mentions/search-users/?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.users = data.users || [];
                this.selectedIndex = -1;
                this.updateDropdown();
            }
        } catch (error) {
            console.error('搜尋使用者失敗:', error);
        } finally {
            this.isLoading = false;
        }
    }

    updateDropdown() {
        // 清空下拉選單
        this.dropdown.innerHTML = '';

        if (this.users.length === 0) {
            this.hideDropdown();
            return;
        }

        // 創建使用者列表
        this.users.forEach((user, index) => {
            const item = document.createElement('div');
            item.className = 'user-autocomplete-item';

            // 使用者頭像（如果有的話）
            const avatar = document.createElement('div');
            avatar.className = 'user-autocomplete-avatar';
            avatar.textContent = user.display_name ? user.display_name[0].toUpperCase() : user.username[0].toUpperCase();

            // 使用者資訊
            const info = document.createElement('div');
            info.className = 'user-autocomplete-info';

            const displayName = document.createElement('div');
            displayName.className = 'user-autocomplete-name';
            displayName.textContent = user.display_name || user.username;

            const username = document.createElement('div');
            username.className = 'user-autocomplete-username';
            username.textContent = `@${user.username}`;

            info.appendChild(displayName);
            info.appendChild(username);

            item.appendChild(avatar);
            item.appendChild(info);

            // 點擊選擇使用者
            item.addEventListener('click', () => {
                this.selectUser(user);
            });

            this.dropdown.appendChild(item);
        });

        this.showDropdown();
    }

    showDropdown() {
        const rect = this.input.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

        this.dropdown.style.position = 'absolute';
        this.dropdown.style.left = (rect.left + scrollLeft) + 'px';
        this.dropdown.style.top = (rect.bottom + scrollTop + 5) + 'px';
        this.dropdown.style.width = rect.width + 'px';
        this.dropdown.style.display = 'block';
    }

    hideDropdown() {
        this.dropdown.style.display = 'none';
        this.selectedIndex = -1;
    }

    handleKeydown(e) {
        if (this.dropdown.style.display === 'none') return;

        const items = this.dropdown.querySelectorAll('.user-autocomplete-item');

        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedIndex = Math.min(this.selectedIndex + 1, items.length - 1);
                this.updateSelection(items);
                break;

            case 'ArrowUp':
                e.preventDefault();
                this.selectedIndex = Math.max(this.selectedIndex - 1, 0);
                this.updateSelection(items);
                break;

            case 'Enter':
                e.preventDefault();
                if (this.selectedIndex >= 0 && this.selectedIndex < this.users.length) {
                    this.selectUser(this.users[this.selectedIndex]);
                }
                break;

            case 'Escape':
                e.preventDefault();
                this.hideDropdown();
                break;
        }
    }

    updateSelection(items) {
        items.forEach((item, index) => {
            if (index === this.selectedIndex) {
                item.classList.add('selected');
                item.scrollIntoView({ block: 'nearest' });
            } else {
                item.classList.remove('selected');
            }
        });
    }

    selectUser(user) {
        // 填入使用者名稱
        this.input.value = user.username;

        // 隱藏下拉選單
        this.hideDropdown();

        // 觸發 change 事件
        this.input.dispatchEvent(new Event('change', { bubbles: true }));

        // 顯示提示訊息（如果有顯示名稱）
        if (user.display_name && user.display_name !== user.username) {
            this.showHint(user.display_name);
        }
    }

    showHint(displayName) {
        // 在輸入框下方顯示提示
        let hint = this.input.parentElement.querySelector('.user-autocomplete-hint');

        if (!hint) {
            hint = document.createElement('div');
            hint.className = 'user-autocomplete-hint';
            this.input.parentElement.appendChild(hint);
        }

        hint.textContent = `已選擇：${displayName}`;
        hint.style.display = 'block';

        // 3 秒後隱藏
        setTimeout(() => {
            hint.style.display = 'none';
        }, 3000);
    }

    destroy() {
        // 移除下拉選單
        if (this.dropdown && this.dropdown.parentElement) {
            this.dropdown.parentElement.removeChild(this.dropdown);
        }

        // 移除標記
        delete this.input._userAutocomplete;
    }
}

// 自動初始化帶有 data-user-autocomplete 屬性的輸入框
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('[data-user-autocomplete]');
    inputs.forEach(input => {
        new UserAutocomplete(input);
    });
});

// 導出供外部使用
window.UserAutocomplete = UserAutocomplete;
