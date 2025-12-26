# 即時聊天與私人訊息分離

## 📌 需求

將「即時聊天」和「私人訊息」作為兩個獨立的功能系統，使用不同的資料庫表和通知機制。

## ✅ 實作完成

### 1. 創建獨立的資料模型

#### ChatMessage 模型 ([blog/models/chat.py](blog/models/chat.py))

**用途**: 專門儲存即時聊天訊息

**欄位**:
- `sender` - 發送者（ForeignKey to User）
- `recipient` - 接收者（ForeignKey to User）
- `content` - 訊息內容（TextField）
- `created_at` - 發送時間（DateTimeField）
- `is_read` - 是否已讀（BooleanField）
- `read_at` - 已讀時間（DateTimeField, nullable）

**索引**:
- `(sender, recipient, -created_at)` - 快速查詢兩人之間的對話
- `(recipient, is_read)` - 快速查詢未讀訊息

#### ChatRoom 模型 ([blog/models/chat.py](blog/models/chat.py))

**用途**: 追蹤兩個用戶之間的聊天狀態（可選）

**欄位**:
- `user1` - 用戶1（ForeignKey to User）
- `user2` - 用戶2（ForeignKey to User）
- `created_at` - 創建時間
- `last_message_at` - 最後訊息時間

**約束**:
- `unique_chat_room` - 確保兩個用戶之間只有一個聊天室

---

### 2. 與傳統私人訊息（Message）的區別

| 項目 | 私人訊息 (Message) | 即時聊天 (ChatMessage) |
|------|-------------------|----------------------|
| **資料表** | `blog_message` | `blog_chatmessage` |
| **用途** | 類似電子郵件的站內信 | 即時通訊聊天 |
| **介面** | 收件匣/寄件匣頁面 | 浮動聊天視窗（右下角） |
| **訊息形式** | 有主旨和內容 | 僅有內容 |
| **通知鏈接** | `/blog/messages/conversation/{username}/` | `/blog/chat/{username}/` |
| **通知訊息** | "向您發送了訊息" | "向您發送了即時訊息" |
| **撤回功能** | ✅ 有 | ❌ 無 |
| **已讀狀態** | ✅ 有 | ✅ 有 |
| **歷史記錄** | 收件匣/寄件匣 | 聊天視窗載入歷史 |

---

### 3. 修改的檔案

#### 後端

1. **[blog/models/chat.py](blog/models/chat.py)** - 新增
   - 創建 `ChatMessage` 和 `ChatRoom` 模型

2. **[blog/models/__init__.py](blog/models/__init__.py)** - 修改
   - 導入並導出新模型

3. **[blog/consumers.py:273-311](blog/consumers.py#L273-L311)** - 修改
   - `get_chat_history()` 使用 `ChatMessage` 而非 `Message`
   - `save_message()` 使用 `ChatMessage` 而非 `Message`

4. **[blog/consumers.py:314-329](blog/consumers.py#L314-L329)** - 修改
   - `send_chat_notification()` 使用 `/blog/chat/` 鏈接
   - 通知訊息改為「向您發送了即時訊息」

5. **資料庫遷移** - 新增
   - `blog/migrations/0017_chatmessage_chatroom.py`

#### 前端

6. **[blog/static/blog/js/real-time-notifications.js:147-163](blog/static/blog/js/real-time-notifications.js#L147-L163)** - 修改
   - 檢測即時聊天通知（`/chat/` 鏈接）
   - 只有即時聊天通知會自動彈出聊天視窗

7. **[blog/static/blog/js/real-time-notifications.js:187-208](blog/static/blog/js/real-time-notifications.js#L187-L208)** - 修改
   - 點擊即時聊天通知開啟聊天視窗
   - 點擊私人訊息通知跳轉到訊息頁面

---

### 4. 工作流程對比

#### 私人訊息流程（不變）

```
用戶 A 發送私人訊息
    ↓
訊息儲存到 Message 表
    ↓
通知用戶 B: "向您發送了訊息"
    ↓
通知鏈接: /blog/messages/conversation/A/
    ↓
用戶 B 點擊通知
    ↓
跳轉到訊息對話頁面
    ↓
查看完整的訊息（主旨、內容、時間）
```

#### 即時聊天流程（新）

```
用戶 A 在聊天視窗發送訊息
    ↓
訊息儲存到 ChatMessage 表（新）
    ↓
WebSocket 即時推送給用戶 B
    ↓
用戶 B 的聊天視窗即時顯示訊息
    ↓
同時發送通知: "向您發送了即時訊息"
    ↓
通知鏈接: /blog/chat/A/（新）
    ↓
用戶 B 的聊天視窗自動彈出（如果還沒開啟）
    ↓
可以直接在聊天視窗中回覆
```

---

### 5. 通知識別機制

#### 前端判斷邏輯

```javascript
// 檢查是否為即時聊天通知
const isChatNotification = notification.link && notification.link.includes('/chat/');

if (isChatNotification && window.instantChatManager) {
    // 自動開啟聊天視窗
    openChatWindowFromNotification(username);
} else {
    // 傳統訊息或其他通知，正常跳轉
    window.location.href = notification.link;
}
```

#### 通知鏈接格式

- **即時聊天**: `/blog/chat/{username}/`
- **私人訊息**: `/blog/messages/conversation/{username}/`
- **其他通知**: `/blog/articles/{id}/` 等

---

### 6. 資料庫結構

#### 即時聊天訊息表 (blog_chatmessage)

```sql
CREATE TABLE blog_chatmessage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL REFERENCES auth_user(id),
    recipient_id INTEGER NOT NULL REFERENCES auth_user(id),
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    read_at DATETIME NULL
);

CREATE INDEX idx_chat_sender_recipient ON blog_chatmessage(sender_id, recipient_id, created_at DESC);
CREATE INDEX idx_chat_unread ON blog_chatmessage(recipient_id, is_read);
```

#### 私人訊息表 (blog_message) - 保持不變

```sql
CREATE TABLE blog_message (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER NOT NULL REFERENCES auth_user(id),
    recipient_id INTEGER NOT NULL REFERENCES auth_user(id),
    subject VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME NOT NULL,
    is_read BOOLEAN NOT NULL DEFAULT 0,
    read_at DATETIME NULL,
    is_sender_deleted BOOLEAN NOT NULL DEFAULT 0,
    is_recipient_deleted BOOLEAN NOT NULL DEFAULT 0,
    recalled_at DATETIME NULL
);
```

---

### 7. API 和 WebSocket

#### WebSocket Consumer

**路由**: `ws/chat/{username}/`

**使用的模型**: `ChatMessage`

**功能**:
- 載入歷史聊天記錄（ChatMessage）
- 儲存新訊息到 ChatMessage 表
- 即時推送給雙方
- 發送通知給對方（如果對方不在聊天視窗）

---

### 8. 未來擴展

#### 可能的功能增強

1. **已讀回條**
   - 顯示對方是否已讀訊息
   - 雙勾勾標記

2. **訊息撤回**（即時聊天）
   - 允許在一定時間內撤回訊息
   - 顯示「已撤回一則訊息」

3. **聊天室列表**
   - 使用 ChatRoom 模型
   - 顯示所有聊天對話
   - 顯示未讀數量

4. **訊息搜尋**
   - 在 ChatMessage 中搜尋歷史訊息
   - 關鍵字高亮

5. **檔案傳送**
   - 在即時聊天中傳送圖片、文件
   - 獨立的 ChatAttachment 模型

6. **訊息統計**
   - 兩人之間的訊息總數
   - 最常聊天的對象

---

### 9. 測試結果

#### 即時聊天測試

```
✅ 發送訊息儲存到 ChatMessage 表
✅ 即時推送給對方
✅ 通知訊息: "向您發送了即時訊息"
✅ 通知鏈接: /blog/chat/username/
✅ 聊天視窗自動彈出
✅ 歷史訊息正確載入
✅ 訊息不會出現在收件匣/寄件匣
```

#### 私人訊息測試

```
✅ 發送訊息儲存到 Message 表
✅ 通知訊息: "向您發送了訊息"
✅ 通知鏈接: /blog/messages/conversation/username/
✅ 點擊通知跳轉到訊息頁面
✅ 訊息不會出現在聊天視窗
✅ 撤回功能仍然正常運作
```

#### 資料分離測試

```
✅ ChatMessage 表和 Message 表完全獨立
✅ 即時聊天訊息不會出現在收件匣
✅ 私人訊息不會出現在聊天視窗
✅ 兩種通知可以正確區分
```

---

### 10. 使用方式

#### 發送即時聊天訊息

1. 前往用戶個人資料頁面
2. 點擊「即時聊天」按鈕
3. 在右下角的聊天視窗輸入訊息
4. 按 Enter 發送
5. 訊息儲存到 `ChatMessage` 表

#### 發送私人訊息

1. 前往「訊息」→「發送訊息」
2. 選擇收件人
3. 填寫主旨和內容
4. 點擊發送
5. 訊息儲存到 `Message` 表

#### 接收訊息

**即時聊天訊息**:
- 收到通知：「{用戶} 向您發送了即時訊息」
- 聊天視窗自動彈出
- 直接在視窗中查看和回覆

**私人訊息**:
- 收到通知：「{用戶} 向您發送了訊息」
- 點擊通知跳轉到訊息頁面
- 在收件匣中查看完整訊息

---

### 11. 資料查詢範例

#### 查詢即時聊天歷史

```python
from blog.models import ChatMessage
from django.db.models import Q

# 查詢與某用戶的聊天記錄
chat_history = ChatMessage.objects.filter(
    Q(sender=user1, recipient=user2) |
    Q(sender=user2, recipient=user1)
).order_by('created_at')
```

#### 查詢私人訊息

```python
from blog.models import Message

# 查詢收件匣
inbox = Message.objects.filter(
    recipient=user,
    is_recipient_deleted=False
).order_by('-created_at')
```

#### 查詢未讀即時訊息數

```python
unread_chat = ChatMessage.objects.filter(
    recipient=user,
    is_read=False
).count()
```

---

### 12. 遷移指令

```bash
# 創建遷移
python manage.py makemigrations

# 查看遷移 SQL
python manage.py sqlmigrate blog 0017

# 應用遷移
python manage.py migrate

# 輸出
Operations to perform:
  Apply all migrations: admin, auth, blog, contenttypes, sessions
Running migrations:
  Applying blog.0017_chatmessage_chatroom... OK
```

---

## 總結

✅ **完全分離** - ChatMessage 和 Message 是兩個獨立的資料表
✅ **不同通知** - 即時訊息和私人訊息有不同的通知鏈接和訊息
✅ **智能識別** - 前端可以自動識別通知類型並做出相應處理
✅ **向下兼容** - 不影響現有的私人訊息功能
✅ **資料庫遷移** - 已創建並應用遷移

**兩個系統現在完全獨立運作！** 🎉

### 系統架構圖

```
┌─────────────────────┐         ┌─────────────────────┐
│   即時聊天系統      │         │   私人訊息系統      │
├─────────────────────┤         ├─────────────────────┤
│ ChatMessage 表      │         │ Message 表          │
│ ChatRoom 表         │         │                     │
│ /ws/chat/          │         │                     │
│ 聊天視窗 UI         │         │ 收件匣/寄件匣 UI    │
│ /blog/chat/        │         │ /blog/messages/     │
│ 即時訊息通知        │         │ 訊息通知            │
└─────────────────────┘         └─────────────────────┘
```

**現在用戶可以同時使用兩種不同的訊息系統，互不干擾！** 🚀
