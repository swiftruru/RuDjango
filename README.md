# 🚀 RuDjango - Django 學習實戰專案

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

一個用於學習和實踐 Django 框架的現代化 Web 應用程式

[功能特色](#-功能特色) • [快速開始](#-快速開始) • [專案結構](#-專案結構) • [學習筆記](#-學習筆記)

</div>

---

## 📖 專案簡介

RuDjango 是一個基於 Django 6.0 開發的練習專案，旨在深入學習 Django 框架的核心概念與最佳實踐。透過實作完整的 Web 應用，掌握從專案架構、路由配置、模板系統到靜態文件管理的各個環節。

## ✨ 功能特色

### 🎯 已實現功能
- ✅ **模組化應用設計** - 使用 Django App 架構，實現功能分離
- ✅ **動態模板系統** - 整合 Django Template Language，實現頁面繼承與複用
- ✅ **靜態資源管理** - 規範化的 CSS/JS/Images 組織架構
- ✅ **響應式介面** - 現代化的 UI 設計，支援多種裝置
- ✅ **URL 路由配置** - 階層式 URL 管理，清晰的路由結構
- ✅ **團隊展示系統** - 動態渲染團隊成員資訊

### 🎨 頁面展示
- **首頁（Home）** - 展示團隊成員與專案特色
- **關於（About）** - 介紹專案資訊與技術特點
- **管理後台** - Django Admin 系統整合

## 🚀 快速開始

### 環境需求

- Python 3.13+
- Django 6.0+
- pip 套件管理工具

### 安裝步驟

1. **克隆專案**
```bash
git clone https://github.com/你的使用者名稱/RuDjango.git
cd RuDjango
```

2. **建立虛擬環境**
```bash
python -m venv RuDjango-env
source RuDjango-env/bin/activate  # macOS/Linux
# 或
RuDjango-env\Scripts\activate     # Windows
```

3. **安裝依賴套件**
```bash
pip install django
```

4. **資料庫遷移**
```bash
python manage.py migrate
```

5. **建立超級使用者（可選）**
```bash
python manage.py createsuperuser
```

6. **啟動開發伺服器**
```bash
python manage.py runserver
```

7. **瀏覽專案**
- 首頁: http://127.0.0.1:8000/
- Blog 首頁: http://127.0.0.1:8000/blog/
- 關於頁面: http://127.0.0.1:8000/blog/about
- 管理後台: http://127.0.0.1:8000/admin/

## 📁 專案結構

```
RuDjangoProject/
│
├── 📂 RuDjangoProject/          # 專案配置目錄
│   ├── settings.py              # 全局設定檔
│   ├── urls.py                  # 主路由配置
│   ├── wsgi.py                  # WSGI 部署接口
│   └── asgi.py                  # ASGI 部署接口
│
├── 📂 blog/                     # Blog 應用
│   ├── 📂 static/blog/          # 應用層級靜態文件
│   │   ├── css/                 # 樣式表
│   │   │   ├── home.css        # 首頁樣式
│   │   │   └── about.css       # 關於頁面樣式
│   │   ├── images/              # 圖片資源
│   │   └── js/                  # JavaScript 文件
│   │
│   ├── 📂 templates/blog/       # 應用層級模板
│   │   ├── base.html           # 基礎模板
│   │   ├── home.html           # 首頁模板
│   │   └── about.html          # 關於頁面模板
│   │
│   ├── views.py                # 視圖邏輯
│   ├── urls.py                 # 應用路由
│   ├── models.py               # 資料模型
│   └── admin.py                # 後台管理配置
│
├── 📂 static/                   # 專案層級靜態文件
│   └── css/
│       └── base.css            # 全站基礎樣式
│
├── 📂 templates/                # 專案層級模板（保留舊模板）
│
├── manage.py                   # Django 管理腳本
├── db.sqlite3                  # SQLite 資料庫
├── README.md                   # 專案說明文件
└── .gitignore                  # Git 忽略文件配置
```

## 📚 學習筆記

### Django 核心概念實踐

#### 1. **專案架構設計**
- **專案層級（RuDjangoProject）**: 負責全局配置、URL 分發、共用資源
- **應用層級（blog）**: 負責具體功能實現，獨立且可重用

#### 2. **URL 路由配置**
```python
# 專案層級 - 分發流量
path('', views.home, name='home')          # 根路徑
path('blog/', include('blog.urls'))         # 應用路由

# 應用層級 - 具體路由
path('', views.home, name='blog_home')      # blog 首頁
path('about', views.about, name='about')    # 關於頁面
```

#### 3. **模板繼承系統**
```django
{# 基礎模板 base.html #}
{% block content %}{% endblock %}

{# 子模板 home.html #}
{% extends 'blog/base.html' %}
{% block content %}
  <!-- 頁面內容 -->
{% endblock %}
```

#### 4. **靜態文件管理**
- **配置方式**: `STATIC_URL` + `STATICFILES_DIRS`
- **最佳實踐**: 應用專屬靜態文件放在 `app/static/app/` 目錄下
- **使用方式**: `{% static 'blog/css/home.css' %}`

#### 5. **Views 與 Context**
```python
def home(request):
    context = {
        'people': [person1, person2, person3],
        'version': 1.0,
    }
    return render(request, 'blog/home.html', context)
```

### 遇到的問題與解決方案

| 問題 | 原因 | 解決方案 |
|------|------|---------|
| Page not found (404) | 根路徑未配置 | 在主 urls.py 添加 `path('', views.home)` |
| 靜態文件失聯 | 路徑配置錯誤 | 使用 `{% static 'blog/css/...' %}` 格式 |
| TemplateDoesNotExist | 模板路徑不正確 | 模板移至 app 後，使用 `'blog/template.html'` |

## 🎓 學習重點

### Django 最佳實踐
✅ **模組化設計** - 功能獨立的 App 結構  
✅ **DRY 原則** - 模板繼承避免重複代碼  
✅ **命名規範** - 清晰的 URL name 和模板路徑  
✅ **靜態資源分離** - 頁面專屬 CSS 獨立管理  
✅ **MVT 架構** - Model-View-Template 分層清晰  

### 技術棧
- **後端框架**: Django 6.0
- **模板引擎**: Django Template Language
- **前端樣式**: CSS3（響應式設計）
- **資料庫**: SQLite3
- **版本控制**: Git

## 🔧 開發功能

### 待實現功能
- [ ] 資料庫模型設計與 ORM 操作
- [ ] 表單處理與驗證
- [ ] 用戶認證系統
- [ ] RESTful API 開發
- [ ] 測試撰寫
- [ ] 部署配置

## 📝 版本紀錄

### v1.0.0 (2025-12-19)
- ✨ 初始化 Django 專案結構
- ✨ 建立 blog 應用
- ✨ 實現首頁與關於頁面
- ✨ 配置靜態文件系統
- ✨ 整合模板繼承架構
- 🎨 實現響應式 UI 設計
- 📝 完善專案文檔

## 👨‍💻 作者

**Ru** - Django 學習者

- 專案目標：深入掌握 Django 全棧開發
- 學習重點：MVT 架構、ORM、RESTful API
- 練習方向：從基礎到進階，逐步建構完整專案

## 📄 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 🙏 致謝

- Django 官方文檔
- Python 社群
- 所有為開源做出貢獻的開發者

---

<div align="center">

**⭐ 如果這個專案對你有幫助，歡迎給個 Star！**

Made with ❤️ and Django

</div>
