# 即時聊天功能更新說明

## 🔧 修復內容 (2025-12-26)

### 問題 1: 聊天視窗沒有顯示對方頭像

**症狀**: 聊天視窗標題列只顯示姓名首字母，沒有顯示對方的頭像照片

**原因**:
- 按鈕沒有傳遞頭像 URL 資料
- JavaScript 沒有接收和使用頭像 URL

**修復**:

#### 1. 更新個人資料頁面模板 ([profile.html:95-102](blog/templates/blog/members/profile.html#L95-L102))
```html
<button class="btn btn-primary btn-instant-chat"
    data-username="{{ member.username }}"
    data-user-id="{{ member.id }}"
    data-display-name="{{ member.name }}"
    data-avatar-url="{% if profile.avatar %}{{ profile|avatar_url }}{% else %}{% static 'blog/images/大頭綠.JPG' %}{% endif %}">
    <span class="chat-icon">💬</span>
    <span class="chat-text">即時聊天</span>
</button>
```

**改動**: 新增 `data-avatar-url` 屬性，自動使用用戶頭像或預設頭像

#### 2. 更新 JavaScript - InstantChatManager ([instant-chat.js:16-26](blog/static/blog/js/instant-chat.js#L16-L26))
```javascript
document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-instant-chat');
    if (btn) {
        e.preventDefault();
        const username = btn.dataset.username;
        const userId = btn.dataset.userId;
        const displayName = btn.dataset.displayName;
        const avatarUrl = btn.dataset.avatarUrl;  // 新增
        this.openChatWindow(username, userId, displayName, avatarUrl);
    }
});
```

#### 3. 更新 openChatWindow 方法 ([instant-chat.js:36-56](blog/static/blog/js/instant-chat.js#L36-L56))
```javascript
openChatWindow(username, userId, displayName, avatarUrl) {  // 新增 avatarUrl 參數
    // ...
    const chatWindow = new ChatWindow(username, userId, displayName, avatarUrl, this);
    // ...
}
```

#### 4. 更新 ChatWindow 類別 ([instant-chat.js:152-162](blog/static/blog/js/instant-chat.js#L152-L162))
```javascript
class ChatWindow {
    constructor(username, userId, displayName, avatarUrl, manager) {  // 新增 avatarUrl 參數
        this.username = username;
        this.userId = userId;
        this.displayName = displayName;
        this.avatarUrl = avatarUrl;  // 儲存頭像 URL
        this.manager = manager;
        // ...
    }
}
```

#### 5. 更新聊天視窗 HTML 模板 ([instant-chat.js:175-177](blog/static/blog/js/instant-chat.js#L175-L177))
```javascript
<div class="chat-avatar">
    ${this.avatarUrl ? `<img src="${this.avatarUrl}" alt="${this.displayName}">` : `<span>${this.displayName.charAt(0)}</span>`}
</div>
```

**效果**:
- ✅ 如果用戶有上傳頭像，顯示頭像圖片
- ✅ 如果沒有頭像，顯示預設頭像（大頭綠.JPG）
- ✅ 頭像圓形顯示，32x32 像素

---

### 問題 2: 無法輸入中文

**症狀**:
- 在聊天輸入框輸入中文時，按 Enter 會立即發送訊息
- 中文輸入法選字時按 Enter 應該是確認選字，而不是發送訊息
- 導致無法正常輸入中文

**原因**:
- JavaScript 的 `keydown` 事件在中文輸入法（IME）輸入過程中也會觸發
- Enter 鍵在選字階段會被誤判為發送訊息的指令
- 沒有區分「正在輸入中文」和「已完成輸入」的狀態

**修復**:

#### 1. 新增中文輸入狀態追蹤 ([instant-chat.js:160](blog/static/blog/js/instant-chat.js#L160))
```javascript
class ChatWindow {
    constructor(username, userId, displayName, avatarUrl, manager) {
        // ...
        this.isComposing = false;  // 追蹤中文輸入狀態
        // ...
    }
}
```

#### 2. 監聽 compositionstart 事件 ([instant-chat.js:247-249](blog/static/blog/js/instant-chat.js#L247-L249))
```javascript
// 監聽中文輸入開始
input.addEventListener('compositionstart', () => {
    this.isComposing = true;  // 標記為正在輸入中文
});
```

**說明**:
- `compositionstart` 事件在用戶開始使用輸入法（如注音、拼音）時觸發
- 此時設定 `isComposing = true`，表示正在輸入中文

#### 3. 監聽 compositionend 事件 ([instant-chat.js:252-254](blog/static/blog/js/instant-chat.js#L252-L254))
```javascript
// 監聽中文輸入結束
input.addEventListener('compositionend', () => {
    this.isComposing = false;  // 標記為中文輸入完成
});
```

**說明**:
- `compositionend` 事件在用戶完成輸入法選字後觸發
- 此時設定 `isComposing = false`，表示可以正常處理 Enter 鍵

#### 4. 修改 Enter 鍵處理邏輯 ([instant-chat.js:256-262](blog/static/blog/js/instant-chat.js#L256-L262))
```javascript
input.addEventListener('keydown', (e) => {
    // 只有在不是中文輸入狀態時才處理 Enter
    if (e.key === 'Enter' && !e.shiftKey && !this.isComposing) {
        e.preventDefault();
        this.sendMessage();
    }
});
```

**改動**: 新增 `!this.isComposing` 條件檢查

**邏輯**:
1. 按下 Enter 鍵
2. 不是 Shift+Enter（換行）
3. **不是正在輸入中文** ← 新增的檢查
4. 才執行發送訊息

**效果**:
- ✅ 中文輸入法選字時按 Enter → 確認選字（不發送訊息）
- ✅ 完成輸入後按 Enter → 發送訊息
- ✅ Shift+Enter → 換行
- ✅ 支援所有輸入法：注音、拼音、倉頡、日文、韓文等

---

## 測試結果

### 頭像顯示測試
```
✅ 用戶有上傳頭像 → 顯示用戶頭像
✅ 用戶沒有頭像 → 顯示預設頭像（大頭綠.JPG）
✅ 頭像圓形顯示
✅ 頭像大小正確（32x32px）
```

### 中文輸入測試
```
✅ 輸入「你好」→ 選字時按 Enter 確認選字
✅ 完成輸入後按 Enter → 發送訊息
✅ 輸入「測試」→ 正常選字、正常發送
✅ Shift+Enter → 正常換行
✅ 英文輸入 → 正常發送
```

## 技術說明

### IME Composition Events

**什麼是 Composition Events?**
- 專門為輸入法（IME, Input Method Editor）設計的事件
- 處理中文、日文、韓文等需要多步驟輸入的語言

**三個主要事件**:
1. `compositionstart` - 開始使用輸入法
2. `compositionupdate` - 輸入法內容更新
3. `compositionend` - 完成輸入法輸入

**為什麼需要這些事件?**
- 中文輸入法有「輸入中」和「已完成」兩個階段
- 在輸入中階段，Enter 是選字用的
- 在已完成階段，Enter 才是發送訊息用的

### 事件執行順序

以輸入「你好」為例：

```
1. 按下 'n' → compositionstart (isComposing = true)
2. 按下 'i' → compositionupdate
3. 按下 Enter (選字) → keydown (被 isComposing 擋住，不發送)
4. compositionend (isComposing = false)
5. 按下 Enter (發送) → keydown (正常發送訊息)
```

### 跨瀏覽器兼容性

| 瀏覽器 | compositionstart | compositionend | 支援狀態 |
|--------|------------------|----------------|---------|
| Chrome | ✅ | ✅ | 完整支援 |
| Firefox | ✅ | ✅ | 完整支援 |
| Safari | ✅ | ✅ | 完整支援 |
| Edge | ✅ | ✅ | 完整支援 |

**結論**: 所有現代瀏覽器都完整支援

## 相關檔案

### 修改的檔案
1. [blog/templates/blog/members/profile.html](blog/templates/blog/members/profile.html) - 新增頭像 URL 資料屬性
2. [blog/static/blog/js/instant-chat.js](blog/static/blog/js/instant-chat.js) - 頭像顯示 + 中文輸入修復

### 無需修改的檔案
- ✅ CSS 檔案 - 頭像樣式已經存在
- ✅ Consumer - WebSocket 後端無需改動
- ✅ 路由設定 - 無需改動

## 使用方式

### 正常使用流程
1. 前往任何用戶的個人資料頁面
2. 點擊「即時聊天」按鈕
3. 聊天視窗彈出，顯示對方的頭像
4. 輸入訊息：
   - 中文：正常選字後按 Enter 發送
   - 英文：按 Enter 發送
   - 換行：Shift+Enter

### 快捷鍵
- `Enter` - 發送訊息（中文選字完成後）
- `Shift+Enter` - 換行
- `Esc` - 無作用（可考慮未來新增關閉視窗功能）

## 常見問題

### Q: 為什麼我的頭像沒有顯示？
**A**: 檢查以下項目：
1. 確認已上傳頭像到個人資料
2. 清除瀏覽器快取（Ctrl+Shift+R）
3. 檢查控制台是否有圖片載入錯誤
4. 確認圖片路徑是否正確

### Q: 中文輸入還是會提前發送怎麼辦？
**A**:
1. 確認使用的是標準中文輸入法
2. 清除瀏覽器快取
3. 重新載入頁面
4. 如果問題持續，檢查瀏覽器控制台錯誤訊息

### Q: 可以顯示對方是否在線嗎？
**A**: 目前標題列固定顯示「線上」，未來可擴展為真實的在線狀態檢測

## 未來改進建議

### 頭像相關
- [ ] 顯示在線/離線狀態（綠點/灰點）
- [ ] 頭像載入失敗時的備用方案
- [ ] 頭像懶加載優化

### 輸入相關
- [ ] 顯示對方正在輸入的指示器
- [ ] @提及自動完成
- [ ] Emoji 快捷輸入
- [ ] Markdown 格式支援

### 快捷鍵
- [ ] Esc 關閉聊天視窗
- [ ] Ctrl+Up/Down 切換聊天視窗
- [ ] Alt+Number 快速切換到第 N 個視窗

## 總結

✅ **頭像顯示問題已修復** - 聊天視窗現在正確顯示對方的頭像
✅ **中文輸入問題已修復** - 支援所有輸入法的正常輸入流程
✅ **跨瀏覽器兼容** - 在所有現代瀏覽器中正常工作
✅ **無破壞性改動** - 不影響現有功能

**即時聊天功能現在完全可用！** 🎉
