# 網頁載入狀態動畫功能說明

## 📖 功能概述

本專案已實作完整的網頁載入狀態動畫系統，包含頁面初次載入動畫、無限滾動載入效果、以及骨架屏載入畫面，提升用戶體驗。

---

## ✨ 已實作功能

### 1. **全螢幕頁面載入器**

當用戶首次訪問或刷新頁面時，會顯示全螢幕載入動畫。

#### 功能特點：
- 漸層背景（紫色主題）
- Logo 浮動動畫
- 旋轉 Spinner
- 進度條動畫
- 自動淡出效果

#### 相關文件：
- CSS: [blog/static/blog/css/page-loader.css](blog/static/blog/css/page-loader.css)
- JavaScript: [blog/static/blog/js/page-loader.js](blog/static/blog/js/page-loader.js)
- 模板: [blog/templates/blog/base.html](blog/templates/blog/base.html#L16-L26)

#### 使用方式：
載入器會自動顯示並在頁面完全載入後淡出（最少顯示 500ms）。

```javascript
// 手動控制（如果需要）
window.PageLoader.show();    // 顯示載入器
window.PageLoader.hide();    // 隱藏載入器
```

---

### 2. **簡約頂部進度條**

當用戶點擊內部連結導航到其他頁面時，會在頂部顯示細長的進度條。

#### 功能特點：
- 只有 3px 高度
- 漸層顏色動畫
- 不干擾頁面內容
- 自動跟隨連結點擊

#### 使用方式：
```javascript
window.PageLoader.showSimple();    // 顯示簡約載入器
window.PageLoader.hideSimple();    // 隱藏簡約載入器
```

#### 排除特定連結：
如果某些連結不需要顯示載入器，可以添加 `no-loader` class：

```html
<a href="/some-page" class="no-loader">不顯示載入器</a>
```

---

### 3. **無限滾動載入動畫**

在文章列表頁面向下滾動時，會自動載入更多文章並顯示載入動畫。

#### 功能特點：
- 旋轉 Spinner 動畫
- 載入文字提示
- 錯誤處理與重試按鈕
- 平滑的淡入動畫
- 載入完成提示

#### 相關文件：
- JavaScript: [blog/static/blog/js/articles/infinite-scroll.js](blog/static/blog/js/articles/infinite-scroll.js)
- CSS: [blog/static/blog/css/articles/list.css](blog/static/blog/css/articles/list.css#L473-L579)
- 模板: [blog/templates/blog/articles/list.html](blog/templates/blog/articles/list.html#L108-L121)

#### 載入狀態：
1. **載入中**: 顯示旋轉 Spinner 和「載入更多文章...」
2. **載入成功**: 新文章以淡入動畫逐一顯示
3. **載入失敗**: 顯示錯誤訊息和重試按鈕
4. **沒有更多**: 顯示「已經到底了，沒有更多文章囉！」

---

### 4. **骨架屏載入效果**

為文章列表頁面提供骨架屏（Skeleton Screen）載入效果。

#### 功能特點：
- 模擬真實文章卡片佈局
- 波浪動畫效果
- 6 個骨架卡片
- 真實內容載入後自動淡出

#### 相關文件：
- 模板: [blog/templates/blog/articles/_article_skeleton.html](blog/templates/blog/articles/_article_skeleton.html)

#### 使用方式：
在需要的頁面中 include 骨架屏模板：

```django
{% if not articles %}
    {% include 'blog/articles/_article_skeleton.html' %}
{% else %}
    <!-- 真實內容 -->
{% endif %}
```

---

## 🎨 可用的載入器樣式

### 1. 預設載入器（Default Loader）
```html
<div id="page-loader" class="page-loader">
    <div class="loader-content">
        <div class="loader-logo">RuDjango</div>
        <div class="loader-spinner"></div>
        <div class="loader-text">載入中...</div>
        <div class="loader-subtext">精彩內容即將呈現</div>
        <div class="loader-progress">
            <div class="loader-progress-bar"></div>
        </div>
    </div>
</div>
```

### 2. 點狀載入器（Dots Loader）
```html
<div class="loader-dots">
    <div class="loader-dot"></div>
    <div class="loader-dot"></div>
    <div class="loader-dot"></div>
</div>
```

### 3. 方塊載入器（Cube Loader）
```html
<div class="cube-loader">
    <div class="cube"></div>
    <div class="cube"></div>
    <div class="cube"></div>
    <div class="cube"></div>
</div>
```

### 4. 波浪載入器（Wave Loader）
```html
<div class="wave-loader">
    <div class="wave-bar"></div>
    <div class="wave-bar"></div>
    <div class="wave-bar"></div>
    <div class="wave-bar"></div>
    <div class="wave-bar"></div>
</div>
```

---

## ⚙️ 配置選項

### JavaScript 配置

在 [page-loader.js](blog/static/blog/js/page-loader.js#L9-L13) 中：

```javascript
const config = {
    minDisplayTime: 500,   // 最小顯示時間（毫秒）
    fadeOutDuration: 500,  // 淡出動畫時長
    showLoader: true,      // 是否顯示載入器
};
```

### 無限滾動配置

在 [infinite-scroll.js](blog/static/blog/js/articles/infinite-scroll.js) 中：

```javascript
// 檢查距離底部多少像素時開始載入
const threshold = 300;  // 可調整此值

// 節流延遲（限制滾動事件觸發頻率）
throttle(checkScrollPosition, 200);  // 200ms
```

---

## 🎯 動畫效果詳情

### 1. 淡入淡出動畫
- 頁面內容淡入: 0.5s
- 載入器淡出: 0.5s
- 文章卡片淡入: 0.5s

### 2. 旋轉動畫
- Spinner 旋轉: 1s 循環
- 按鈕圖示旋轉: 2s 循環
- 方塊動畫: 1.8s 循環

### 3. 進度條動畫
- 完整週期: 2s
- 前半段載入: 0-70%
- 後半段完成: 70-100%

### 4. 骨架屏動畫
- 波浪週期: 1.5s
- 淡出時長: 0.5s

---

## 📱 響應式設計

所有載入動畫都支援響應式設計：

### 平板 (≤768px)
- Logo 字體縮小
- Spinner 尺寸調整
- 進度條寬度減少

### 手機 (≤480px)
- 進一步縮小所有元素
- 簡化動畫效果
- 優化觸控體驗

---

## 🔧 自訂載入器

### 更改顏色主題

在 [page-loader.css](blog/static/blog/css/page-loader.css) 中修改：

```css
.page-loader {
    /* 更改漸層背景 */
    background: linear-gradient(135deg, #你的顏色1 0%, #你的顏色2 100%);
}

.loader-spinner::after {
    /* 更改 Spinner 顏色 */
    border-top-color: #你的顏色;
    border-right-color: #你的顏色;
}
```

### 更改載入文字

在 [base.html](blog/templates/blog/base.html#L20-L21) 中修改：

```html
<div class="loader-text">你的載入文字</div>
<div class="loader-subtext">你的副標題</div>
```

### 更改 Logo

在 [base.html](blog/templates/blog/base.html#L18) 中修改：

```html
<div class="loader-logo">你的 Logo</div>
```

---

## 🐛 故障排除

### 問題 1: 載入器不消失
**解決方案**: 檢查 JavaScript 是否正確載入
```javascript
console.log(window.PageLoader); // 應該輸出物件
```

### 問題 2: 無限滾動不工作
**解決方案**:
1. 檢查 AJAX 端點是否正確
2. 確認 `X-Requested-With` 標頭是否設定
3. 查看瀏覽器控制台錯誤訊息

### 問題 3: 動畫卡頓
**解決方案**:
1. 增加節流延遲
2. 減少同時顯示的動畫元素
3. 使用 CSS `will-change` 屬性

---

## 📊 性能優化

### 已實作的優化：
1. **節流函數**: 限制滾動事件觸發頻率
2. **CSS 動畫**: 使用 GPU 加速的 CSS 動畫
3. **延遲載入**: 分批顯示文章卡片
4. **最小顯示時間**: 避免閃爍效果

### 建議的優化：
1. 使用 `IntersectionObserver` 替代滾動監聽
2. 實作虛擬滾動（Virtual Scrolling）
3. 圖片懶加載（Lazy Loading）
4. 使用 Service Worker 快取

---

## 🎬 使用示例

### 示例 1: 在自訂頁面使用載入器

```html
{% extends 'blog/base.html' %}
{% load static %}

{% block extra_css %}
<!-- 已自動包含 page-loader.css -->
{% endblock %}

{% block content %}
<div class="your-content">
    <!-- 你的內容 -->
</div>
{% endblock %}

{% block extra_js %}
<script>
// 如果需要手動控制
document.addEventListener('DOMContentLoaded', function() {
    // 顯示載入器
    window.PageLoader.show();

    // 模擬異步操作
    setTimeout(() => {
        window.PageLoader.hide();
    }, 2000);
});
</script>
{% endblock %}
```

### 示例 2: AJAX 請求使用簡約載入器

```javascript
// 開始 AJAX 請求前
window.PageLoader.showSimple();

fetch('/api/data')
    .then(response => response.json())
    .then(data => {
        // 處理數據
    })
    .finally(() => {
        // 完成後隱藏
        window.PageLoader.hideSimple();
    });
```

---

## 📝 更新日誌

### Version 1.0.0 (2025-12-25)
- ✅ 實作全螢幕頁面載入器
- ✅ 實作簡約頂部進度條
- ✅ 實作無限滾動載入動畫
- ✅ 實作骨架屏載入效果
- ✅ 實作錯誤處理與重試
- ✅ 實作響應式設計
- ✅ 優化性能與動畫

---

## 🔗 相關連結

- [無限滾動與分頁改善功能](README.md)
- [Django 官方文檔](https://docs.djangoproject.com/)
- [CSS 動畫指南](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Animations)
- [Intersection Observer API](https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API)

---

## 💡 最佳實踐

1. **不要過度使用動畫** - 保持簡潔優雅
2. **確保可訪問性** - 提供替代方案給禁用 JavaScript 的用戶
3. **測試性能** - 在低端設備上測試動畫流暢度
4. **提供回饋** - 讓用戶知道正在發生什麼
5. **優雅降級** - 確保在不支援的瀏覽器上仍能運作

---

## 🎓 技術棧

- **前端**: HTML5, CSS3, Vanilla JavaScript
- **後端**: Django 5.1, Python 3.13
- **動畫**: CSS Animations, CSS Transitions
- **AJAX**: Fetch API
- **架構模式**: Progressive Enhancement

---

**開發者**: RuDjango Team
**最後更新**: 2025-12-25
**版本**: 1.0.0
