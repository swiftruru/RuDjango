# 即時聊天功能問題修復

## 🐛 問題修復 (2025-12-26)

### 問題 1: 第二次發送訊息失敗

**症狀**:
- 第一次發送訊息成功
- 第二次及之後發送訊息時出現「訊息發送失敗，請檢查網路連接」錯誤
- WebSocket 連接斷開

**錯誤訊息**:
```
AttributeError: 'User' object has no attribute 'name'
```

**原因**:
在 [consumers.py:321](blog/consumers.py#L321) 中，`send_chat_notification()` 方法嘗試訪問 `self.user.name`，但 Django 的預設 User 模型沒有 `name` 屬性。

**修復**:
修改 `send_chat_notification()` 方法使用正確的屬性：

```python
# 修復前
message=f'{self.user.name} 向您發送了訊息',

# 修復後
# Get display name (first_name or username)
display_name = self.user.first_name if self.user.first_name else self.user.username

create_notification(
    user=self.other_user,
    notification_type='message',
    message=f'{display_name} 向您發送了訊息',
    link=f'/blog/messages/conversation/{self.user.username}/'
)
```

**修改檔案**: [blog/consumers.py:318-326](blog/consumers.py#L318-L326)

**結果**: ✅ 訊息可以連續發送，WebSocket 不會斷開

---

### 問題 2: 對方沒有自動彈出聊天視窗

**症狀**:
- 用戶 A 向用戶 B 發送訊息
- 用戶 B 收到通知
- 但用戶 B 的畫面沒有自動彈出聊天視窗
- 必須手動點擊對方個人資料頁面的「即時聊天」按鈕

**原因**:
1. 通知系統沒有偵測訊息通知類型
2. 沒有自動開啟聊天視窗的機制
3. 缺少用戶資料 API 端點

**修復**:

#### 1. 修改通知處理邏輯 ([real-time-notifications.js:147-244](blog/static/blog/js/real-time-notifications.js#L147-L244))

新增自動開啟聊天視窗功能：

```javascript
function showNotificationToast(notification) {
    // 如果是訊息通知且有即時聊天管理器，自動開啟聊天視窗
    if (notification.notification_type === 'message' && window.instantChatManager && notification.link) {
        // 從 link 提取用戶名: /blog/messages/conversation/{username}/
        const match = notification.link.match(/\/conversation\/([^\/]+)\//);
        if (match) {
            const username = match[1];
            // 延遲一點點以確保 DOM 已準備好
            setTimeout(() => {
                openChatWindowFromNotification(username);
            }, 100);
        }
    }

    // ... 其他通知顯示邏輯
}
```

新增 `openChatWindowFromNotification()` 函數：

```javascript
function openChatWindowFromNotification(username) {
    // 獲取用戶資料
    fetch(`/blog/api/user/${username}/`)
        .then(response => response.json())
        .then(data => {
            if (data.success && window.instantChatManager) {
                window.instantChatManager.openChatWindow(
                    data.user.username,
                    data.user.id,
                    data.user.display_name,
                    data.user.avatar_url
                );
            }
        })
        .catch(error => {
            console.error('無法獲取用戶資料:', error);
        });
}
```

#### 2. 創建用戶資料 API ([member_views.py:643-676](blog/views/member_views.py#L643-L676))

新增 API 端點返回用戶基本資訊：

```python
def get_user_api(request, username):
    """
    API: 獲取用戶基本資訊（用於即時聊天）
    """
    from django.http import JsonResponse

    try:
        user = User.objects.get(username=username)
        profile = user.profile

        # 獲取顯示名稱
        display_name = user.first_name if user.first_name else user.username

        # 獲取頭像 URL
        if profile.avatar:
            avatar_url = profile.get_avatar_url()
        else:
            from django.templatetags.static import static
            avatar_url = static('blog/images/大頭綠.JPG')

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': display_name,
                'avatar_url': request.build_absolute_uri(avatar_url) if avatar_url else None
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '用戶不存在'
        }, status=404)
```

#### 3. 新增 URL 路由 ([urls.py:98](blog/urls.py#L98))

```python
# 用戶 API
path('api/user/<str:username>/', views.get_user_api, name='get_user_api'),
```

#### 4. 導出 API 函數 ([views/__init__.py:48,144](blog/views/__init__.py#L48,L144))

```python
# 導入
from .member_views import (
    # ...
    get_user_api
)

# 導出
__all__ = [
    # ...
    'get_user_api',
]
```

**結果**: ✅ 當收到訊息通知時，會自動彈出聊天視窗

---

## 工作流程

### 修復後的完整流程：

```
用戶 A 發送訊息給用戶 B
    ↓
1. JavaScript 發送 WebSocket 訊息
    ↓
2. ChatConsumer.receive() 接收訊息
    ↓
3. save_message() 儲存到資料庫
    ↓
4. group_send() 廣播給房間（雙方都在的話會即時收到）
    ↓
5. send_chat_notification() 發送通知給用戶 B
    ├─ 使用 first_name 或 username 作為顯示名稱 ✅
    ├─ 創建 Notification 記錄
    └─ 透過 WebSocket 推送通知
    ↓
6. 用戶 B 的瀏覽器收到通知
    ↓
7. showNotificationToast() 處理通知
    ├─ 檢測到 notification_type === 'message'
    ├─ 從 link 提取發送者 username
    └─ 呼叫 openChatWindowFromNotification()
    ↓
8. 向 /blog/api/user/{username}/ 發送請求
    ↓
9. get_user_api() 返回用戶資料
    ├─ username
    ├─ user_id
    ├─ display_name (first_name 或 username)
    └─ avatar_url (頭像或預設圖片)
    ↓
10. instantChatManager.openChatWindow() 自動開啟聊天視窗
    ↓
11. 用戶 B 看到聊天視窗自動彈出，顯示用戶 A 的訊息 ✅
```

---

## 修改的檔案

### 後端
1. [blog/consumers.py](blog/consumers.py) - 修復 User 屬性錯誤
2. [blog/views/member_views.py](blog/views/member_views.py) - 新增用戶資料 API
3. [blog/views/__init__.py](blog/views/__init__.py) - 導出 API 函數
4. [blog/urls.py](blog/urls.py) - 新增 API 路由

### 前端
5. [blog/static/blog/js/real-time-notifications.js](blog/static/blog/js/real-time-notifications.js) - 自動開啟聊天視窗

---

## 測試結果

### 連續發送訊息測試
```
✅ 第 1 次發送 → 成功
✅ 第 2 次發送 → 成功
✅ 第 3 次發送 → 成功
✅ WebSocket 持續連接
✅ 沒有錯誤訊息
```

### 自動彈出聊天視窗測試
```
視窗 1: 用戶 A
視窗 2: 用戶 B

1. 用戶 A 向用戶 B 發送訊息 ✅
2. 用戶 B 立即收到通知（右上角） ✅
3. 用戶 B 的聊天視窗自動彈出（右下角） ✅
4. 聊天視窗顯示用戶 A 的頭像 ✅
5. 聊天視窗顯示用戶 A 的名稱 ✅
6. 聊天視窗顯示歷史訊息 ✅
7. 可以直接在視窗中回覆 ✅
```

---

## API 端點

### GET /blog/api/user/{username}/

**用途**: 獲取用戶基本資訊，用於自動開啟聊天視窗

**參數**:
- `username` (路徑參數) - 用戶名

**回應**:

**成功 (200)**:
```json
{
  "success": true,
  "user": {
    "id": 1,
    "username": "ruru",
    "display_name": "Ruru",
    "avatar_url": "http://127.0.0.1:8000/media/avatars/ruru_123456.jpg"
  }
}
```

**失敗 (404)**:
```json
{
  "success": false,
  "error": "用戶不存在"
}
```

---

## 用戶體驗提升

### 修復前
1. 用戶 A 發送訊息
2. 用戶 B 收到通知
3. 用戶 B 點擊通知 → 跳轉到訊息對話頁面
4. 用戶 B 手動回到個人資料頁面
5. 用戶 B 手動點擊「即時聊天」
6. 才能開始即時對話

### 修復後
1. 用戶 A 發送訊息
2. 用戶 B 收到通知 + **聊天視窗自動彈出**
3. 用戶 B 直接在視窗中回覆
4. 真正的「即時」對話體驗 ✅

---

## 安全性考量

### API 安全性
- ✅ 只返回公開資訊（username, display_name, avatar）
- ✅ 不返回敏感資訊（email, password, phone）
- ✅ 任何已登入用戶都可以查詢（符合公開個人資料的設計）

### WebSocket 安全性
- ✅ 已有用戶認證檢查
- ✅ 訊息只發送給房間內的用戶
- ✅ 無法偽造發送者

---

## 效能影響

### API 查詢
- **每次自動開啟聊天視窗**: 1 次 API 請求
- **快取**: 可考慮在前端快取用戶資料（未來優化）
- **資料庫查詢**: 1 次 User 查詢 + 1 次 Profile 查詢（已有外鍵優化）

### WebSocket
- **無額外負載**: 使用現有的通知系統
- **訊息傳遞**: 與之前相同的效能

---

## 常見問題

### Q: 為什麼需要 API 端點？
**A**: 因為通知只包含 `username`，但開啟聊天視窗需要：
- `user_id` - 建立 WebSocket 連接
- `display_name` - 顯示在聊天視窗標題
- `avatar_url` - 顯示頭像

### Q: 如果 API 請求失敗會怎樣？
**A**: 聊天視窗不會自動開啟，但通知仍然會顯示。用戶可以點擊通知跳轉到訊息頁面。

### Q: 會不會重複開啟聊天視窗？
**A**: 不會。`InstantChatManager` 會檢查視窗是否已開啟，如果已開啟則只聚焦該視窗。

---

## 總結

✅ **問題 1 已修復** - 可以連續發送訊息，不會斷線
✅ **問題 2 已修復** - 收到訊息時聊天視窗自動彈出
✅ **用戶體驗提升** - 真正的即時聊天體驗
✅ **向下兼容** - 不影響現有功能

**即時聊天功能現在完全可用且體驗流暢！** 🎉
