# 🔔 通知系統說明文檔

## 概述

RuDjango 通知系統是一個完整的即時通知解決方案，支援多種通知類型、個人化設定，以及即時推送功能。

## 功能特點

### 1. 通知類型

系統支援以下通知類型：

- **💬 留言通知**：當有人在您的文章下留言時
- **❤️ 按讚通知**：當有人喜歡您的文章時
- **👥 追蹤通知**：當有人開始追蹤您時
- **✉️ 私訊通知**：當收到新的私人訊息時
- **🔗 分享通知**：當有人分享您的文章時

### 2. 核心功能

#### 通知中心
- **URL**: `/blog/notifications/`
- **功能**：
  - 查看所有通知（已讀/未讀）
  - 按通知類型篩選
  - 標記單一或全部通知為已讀
  - 刪除通知
  - 分頁顯示

#### 即時通知
- 使用輪詢（Polling）技術，每 30 秒檢查一次新通知
- 導航欄即時顯示未讀通知數量
- 新通知到達時顯示 Toast 提示
- 支援瀏覽器原生通知（需用戶授權）

#### 通知設定
- **URL**: `/blog/notifications/preferences/`
- **功能**：
  - 自訂接收哪些類型的通知
  - 獨立控制每種通知類型
  - 未來支援 Email 通知

## 資料模型

### Notification Model

```python
class Notification(models.Model):
    user = models.ForeignKey(User)              # 接收者
    sender = models.ForeignKey(User)            # 發送者
    notification_type = models.CharField()       # 通知類型
    message = models.TextField()                 # 通知內容
    link = models.CharField()                    # 相關連結
    is_read = models.BooleanField()             # 已讀狀態
    created_at = models.DateTimeField()         # 建立時間
    read_at = models.DateTimeField()            # 已讀時間
    content_type = models.ForeignKey()          # 關聯物件類型
    object_id = models.PositiveIntegerField()   # 關聯物件 ID
```

### NotificationPreference Model

```python
class NotificationPreference(models.Model):
    user = models.OneToOneField(User)
    enable_comment_notifications = models.BooleanField(default=True)
    enable_like_notifications = models.BooleanField(default=True)
    enable_follower_notifications = models.BooleanField(default=True)
    enable_message_notifications = models.BooleanField(default=True)
    enable_share_notifications = models.BooleanField(default=True)
    enable_email_notifications = models.BooleanField(default=False)
```

## API 端點

### 1. 通知計數 API

**端點**: `GET /blog/api/notifications/count/`

**回應**:
```json
{
  "success": true,
  "unread_count": 5,
  "recent_notifications": [
    {
      "id": 1,
      "type": "comment",
      "icon": "💬",
      "message": "user123 在您的文章「Django 入門」中留言",
      "link": "/blog/article/1/#comment-5",
      "time_since": "5 分鐘前",
      "created_at": "2025-12-25T10:00:00Z"
    }
  ]
}
```

### 2. 標記為已讀

**端點**: `POST /blog/notifications/<notification_id>/read/`

**回應**:
```json
{
  "success": true,
  "message": "已標記為已讀",
  "unread_count": 4
}
```

### 3. 全部標記為已讀

**端點**: `POST /blog/notifications/mark-all-read/`

**回應**:
```json
{
  "success": true,
  "message": "已將 5 則通知標記為已讀",
  "updated_count": 5,
  "unread_count": 0
}
```

## 程式碼使用範例

### 創建通知

```python
from blog.utils.notifications import (
    notify_comment,
    notify_like,
    notify_follower,
    notify_message,
    notify_share,
    create_notification
)

# 1. 使用專用函數（推薦）
notify_comment(article, comment)
notify_like(article, user)
notify_follower(followed_user, follower)
notify_message(recipient, sender, message_obj)
notify_share(article, user)

# 2. 使用通用函數
create_notification(
    user=target_user,
    notification_type='comment',
    message='有人留言了',
    sender=sender_user,
    link='/blog/article/1/',
    content_object=comment  # 可選
)
```

### 查詢通知

```python
from blog.models import Notification

# 獲取用戶的所有未讀通知
unread = Notification.objects.filter(user=request.user, is_read=False)

# 獲取特定類型的通知
likes = Notification.objects.filter(
    user=request.user,
    notification_type='like'
)

# 標記為已讀
notification.mark_as_read()
```

### 檢查通知偏好

```python
from blog.models import NotificationPreference

# 獲取或創建用戶偏好
preference = NotificationPreference.get_or_create_for_user(user)

# 檢查是否啟用某類型通知
if preference.is_notification_enabled('like'):
    # 發送按讚通知
    pass
```

## 前端整合

### 1. 導航欄通知圖示

在 `base.html` 中已整合通知圖示：

```html
<li><a href="{% url 'notifications_center' %}" class="nav-link nav-notifications">
    <span class="notification-icon">🔔</span>
    通知
    <span class="notification-badge" id="notification-count" style="display: none;"></span>
</a></li>
```

### 2. 即時輪詢

即時通知腳本 `realtime.js` 會自動：
- 每 30 秒檢查一次新通知
- 更新導航欄徽章數量
- 顯示 Toast 提示
- 頁面隱藏時停止輪詢

### 3. 控制即時通知

```javascript
// 停止輪詢
window.NotificationRealtime.stop();

// 開始輪詢
window.NotificationRealtime.start();

// 手動檢查
window.NotificationRealtime.check();

// 請求瀏覽器通知權限
window.NotificationRealtime.requestPermission();
```

## 文件結構

```
blog/
├── models/
│   └── notification.py               # 通知資料模型
├── views/
│   └── notification_views.py         # 通知視圖
├── utils/
│   └── notifications.py              # 通知工具函數
├── templates/
│   └── blog/
│       └── notifications/
│           ├── center.html           # 通知中心頁面
│           └── preferences.html      # 通知設定頁面
├── static/
│   └── blog/
│       ├── css/
│       │   └── notifications/
│       │       ├── center.css        # 通知中心樣式
│       │       └── preferences.css   # 設定頁樣式
│       └── js/
│           └── notifications/
│               ├── center.js         # 通知中心腳本
│               └── realtime.js       # 即時通知腳本
└── migrations/
    └── 0014_notificationpreference_notification.py
```

## 通知觸發時機

### 自動觸發

以下操作會自動創建通知：

1. **留言時** (`article_views.py:148`)
   ```python
   comment.save()
   notify_comment(article, comment)
   ```

2. **按讚時** (`article_views.py:649`)
   ```python
   if not created:
       notify_like(article, request.user)
   ```

3. **分享時** (`article_views.py:819`)
   ```python
   if request.user.is_authenticated:
       notify_share(article, request.user)
   ```

4. **追蹤時** (`member_views.py:562`)
   ```python
   Follow.objects.create(follower=request.user, following=target_user)
   notify_follower(target_user, request.user)
   ```

5. **發送私訊時** (`message_views.py:108`)
   ```python
   message = Message.objects.create(...)
   notify_message(recipient_user, request.user, message)
   ```

## 測試

執行測試腳本：

```bash
python test_notifications.py
```

測試內容包括：
- ✓ 通知偏好設定
- ✓ 創建基本通知
- ✓ 通知數量查詢
- ✓ 標記為已讀
- ✓ 文章相關通知
- ✓ 查詢所有通知
- ✓ 通知偏好管理
- ✓ 停用通知類型

## 進階配置

### 修改輪詢間隔

編輯 `blog/static/blog/js/notifications/realtime.js`:

```javascript
const config = {
    pollInterval: 30000,  // 修改為所需的毫秒數
    // ...
};
```

### 停用即時通知

在 `base.html` 中註釋或移除：

```html
<!-- <script src="{% static 'blog/js/notifications/realtime.js' %}"></script> -->
```

### 自訂通知訊息

編輯 `blog/utils/notifications.py` 中的訊息模板：

```python
def notify_like(article, user):
    message = f"{user.username} 讚了您的文章「{article.title}」"
    # 自訂您的訊息格式
```

## 效能考量

### 資料庫索引

系統已為常用查詢添加索引：

```python
class Meta:
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['user', 'is_read']),
    ]
```

### 查詢優化

- 使用 `select_related()` 優化關聯查詢
- 分頁減少單次查詢數量
- 輪詢僅取最新 5 則通知

### 清理舊通知

建議定期清理已讀且超過 30 天的通知：

```python
from datetime import timedelta
from django.utils import timezone

# 刪除 30 天前的已讀通知
cutoff_date = timezone.now() - timedelta(days=30)
Notification.objects.filter(
    is_read=True,
    read_at__lt=cutoff_date
).delete()
```

## 未來改進

- [ ] WebSocket 即時推送（取代輪詢）
- [ ] Email 通知發送
- [ ] 通知摘要（每日/每週）
- [ ] 通知分組顯示
- [ ] 推送通知（PWA）
- [ ] 通知音效
- [ ] 未讀通知桌面提醒

## 故障排除

### 通知未顯示

1. 檢查用戶通知偏好設定
2. 確認發送者不是接收者本人
3. 查看 Django 日誌

### 即時通知不工作

1. 確認用戶已登入
2. 檢查瀏覽器控制台錯誤
3. 確認 API 端點正常運作：
   ```bash
   curl -s http://localhost:8000/blog/api/notifications/count/
   ```

### 效能問題

1. 檢查資料庫索引
2. 考慮增加輪詢間隔
3. 啟用 Django 快取

## 技術支援

如有問題或建議，請聯繫開發團隊。

---

最後更新：2025-12-25
版本：1.0.0
