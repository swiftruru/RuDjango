# 🚀 RuDjango - Advanced Django Blogging Platform

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![Channels](https://img.shields.io/badge/Channels-4.3.2-red?style=for-the-badge&logo=django)
![WebSocket](https://img.shields.io/badge/WebSocket-Enabled-orange?style=for-the-badge&logo=socket.io)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A modern, full-featured blogging platform with real-time features and advanced social interactions

[Features](#-features) • [Quick Start](#-quick-start) • [Project Structure](#-project-structure) • [Learning Notes](#-learning-notes)

</div>

---

## 📖 About

RuDjango is a production-ready blogging platform built with Django 6.0 and Django Channels, demonstrating advanced full-stack web development. This comprehensive application showcases real-time WebSocket communications, instant messaging, advanced content creation with Markdown/LaTeX/Mermaid support, SEO optimization, intelligent search with history tracking, Web Push notifications, and complete social networking features with gamification systems.

## ✨ Features

### 🎯 Core Features
- ✅ **User System** - Complete authentication with registration, login/logout
- ✅ **User Profiles** - Extended profiles with drag-drop avatar upload, bio, social links, and gamification
- ✅ **Article Management** - Full CRUD operations with Markdown editor and live preview
- ✅ **Draft System** - Save, publish, and discard article drafts with auto-save
- ✅ **Comment System** - Nested comments with real-time interaction and @mentions
- ✅ **Like System** - Ajax-based likes for articles and comments
- ✅ **Tag System** - Multi-tag support with tag cloud and filtering
- ✅ **Search System** - Advanced search with history tracking, popular searches, and auto-suggestions
- ✅ **Reading History** - Automatic tracking of article reading progress
- ✅ **Achievements** - Badge system with retroactive achievement awards
- ✅ **Points & Levels** - Gamification with Bronze to Diamond tiers
- ✅ **Activity Tracking** - User activity logging and statistics

### 💬 Real-time Communication
- ✅ **Instant Chat** - WebSocket-based 1-on-1 chat with typing indicators
- ✅ **Chat Center** - Facebook Messenger-style chat dropdown with conversation list
- ✅ **Private Messaging** - Inbox/Outbox with thread-based conversations and recall
- ✅ **Real-time Notifications** - WebSocket notifications with auto-reconnection
- ✅ **Web Push Notifications** - Browser push notifications with VAPID authentication
- ✅ **Chat Windows** - Multiple minimizable chat windows with message history
- ✅ **User Following** - Follow system with real-time follower counts
- ✅ **Notification Center** - Centralized notification hub with preferences

### ✍️ Advanced Content Creation
- ✅ **Markdown Editor** - Dual-pane editor with live preview and synchronized scrolling
- ✅ **Syntax Highlighting** - highlight.js support for code blocks (GitHub Dark theme)
- ✅ **LaTeX Math Formulas** - KaTeX rendering for inline and display math ($...$ and $$...$$)
- ✅ **Mermaid Diagrams** - Support for flowcharts, sequence diagrams, class diagrams, etc.
- ✅ **@Mention System** - Autocomplete user mentions with clickable links
- ✅ **Client-side Rendering** - Consistent rendering between editor and published articles
- ✅ **Rich Text Support** - Full Markdown specification with extensions

### 🔍 Search & Discovery
- ✅ **Advanced Search** - Search by content, tags, authors with filters
- ✅ **Search History** - Track and display recent searches with delete options
- ✅ **Popular Searches** - Show trending searches from last 7 days
- ✅ **Auto-suggestions** - Real-time search suggestions with keyboard navigation
- ✅ **Smart Deduplication** - Prevent duplicate searches within 5-minute window
- ✅ **Search Analytics** - Track search queries and result counts

### 🎮 Gamification System
- ✅ **Level System** - 5-tier progression (Bronze, Silver, Gold, Platinum, Diamond)
- ✅ **Achievement Badges** - Automated achievement unlocking based on activities
- ✅ **Points System** - Earn points for articles, comments, and interactions
- ✅ **Progress Tracking** - Visual progress bars and statistics
- ✅ **Retroactive Awards** - Management commands to award past achievements

### 🌐 SEO & Performance
- ✅ **SEO Optimization** - Auto-generated meta descriptions (155 char max)
- ✅ **XML Sitemap** - Dynamic sitemap for articles, tags, users, and static pages
- ✅ **RSS/Atom Feeds** - Syndication feeds for articles
- ✅ **Open Graph Tags** - Social media sharing optimization
- ✅ **Twitter Cards** - Enhanced Twitter sharing with metadata
- ✅ **Canonical URLs** - Proper URL canonicalization

### 🎨 UI/UX Features
- ✅ **Responsive Design** - Mobile-first, adapts to all screen sizes
- ✅ **Toast Notifications** - Beautiful toast notifications with auto-dismiss
- ✅ **Tag Cloud** - Dynamic font sizing based on article count
- ✅ **Modern Gradients** - Beautiful gradient color schemes throughout
- ✅ **Interactive Animations** - Smooth hover effects and transitions
- ✅ **Mobile Navigation** - Hamburger menu with improved spacing and styling
- ✅ **Chat UI** - Bottom-right chat windows with minimize/maximize
- ✅ **Typing Indicators** - Real-time typing status in chat
- ✅ **Unread Badges** - Visual indicators for unread messages and notifications

## 🚀 Quick Start

### Requirements

- Python 3.13+
- Django 6.0+
- Django Channels 4.3.2+
- pip package manager

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/swiftruru/RuDjango.git
cd RuDjango/RuDjangoProject
```

2. **Create virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

Required packages:
- Django==6.0
- channels==4.3.2
- Pillow==12.0.0
- markdown==3.10
- py-vapid==1.9.1
- asgiref==3.11.0
- sqlparse==0.5.4

4. **Configure environment variables**

```bash
cp .env.example .env
# Edit .env and set:
# - SECRET_KEY (Django secret key)
# - VAPID keys for push notifications (generate with py-vapid)
# - VAPID_MAILTO (your email address)
```

Generate VAPID keys:

```bash
vapid --gen
```

5. **Run migrations**

```bash
python manage.py migrate
```

6. **Create default achievements**

```bash
python manage.py create_default_achievements
```

7. **Create superuser**

```bash
python manage.py createsuperuser
```

8. **Start development server**

```bash
python manage.py runserver
```

9. **Browse the application**

- Home: <http://127.0.0.1:8000/>
- Blog: <http://127.0.0.1:8000/blog/>
- Search: <http://127.0.0.1:8000/blog/search/>
- Tags: <http://127.0.0.1:8000/blog/tags/>
- Messages: <http://127.0.0.1:8000/blog/messages/inbox/>
- Chat: <http://127.0.0.1:8000/blog/chat/>
- Notifications: <http://127.0.0.1:8000/blog/notifications/>
- Admin Panel: <http://127.0.0.1:8000/admin/>

## 📁 Project Structure

```
RuDjangoProject/
│
├── 📂 RuDjangoProject/          # Project configuration
│   ├── settings.py              # Global settings with Channels layer config
│   ├── urls.py                  # Main URL configuration with sitemap/feeds
│   ├── wsgi.py                  # WSGI deployment interface
│   └── asgi.py                  # ASGI application with WebSocket routing
│
├── 📂 blog/                     # Main blog application
│   │
│   ├── 📂 models/               # Data models (modular design)
│   │   ├── __init__.py         # Model exports
│   │   ├── article.py          # Article, Tag, Comment, Like models
│   │   ├── member.py           # UserProfile, Achievement, Activity models
│   │   ├── social.py           # Message, Follow, Share models
│   │   ├── notification.py     # Notification, NotificationPreference models
│   │   ├── chat.py             # ChatMessage, ChatRoom models
│   │   ├── search.py           # SearchHistory model
│   │   └── push_subscription.py # PushSubscription model for Web Push
│   │
│   ├── 📂 views/                # View controllers
│   │   ├── __init__.py         # View exports
│   │   ├── article_views.py    # Article CRUD, search, suggestions
│   │   ├── member_views.py     # User profiles, following, achievements, chat
│   │   ├── message_views.py    # Private messaging system
│   │   └── notification_views.py # Notification center and preferences
│   │
│   ├── 📂 forms/                # Django forms
│   │   ├── article.py          # Article and comment forms
│   │   └── member.py           # Profile and message forms
│   │
│   ├── 📂 management/commands/  # Custom management commands
│   │   ├── create_default_achievements.py
│   │   ├── award_retroactive_achievements.py
│   │   └── award_retroactive_points.py
│   │
│   ├── 📂 static/blog/          # App-level static files
│   │   ├── 📂 css/             # Stylesheets
│   │   │   ├── articles/       # Article-related styles
│   │   │   ├── members/        # Member profile styles
│   │   │   ├── messages.css    # Messaging system styles
│   │   │   ├── tags.css        # Tag cloud styles
│   │   │   ├── instant-chat.css # Chat window styles
│   │   │   ├── chat-center.css # Chat center dropdown styles
│   │   │   ├── search-suggestions.css # Search UI styles
│   │   │   └── real-time-notifications.css # Notification styles
│   │   ├── 📂 js/              # JavaScript files
│   │   │   ├── articles/       # Article interactions (like, share)
│   │   │   ├── members/        # Member interactions (follow)
│   │   │   ├── instant-chat.js # Chat window manager
│   │   │   ├── chat-center.js  # Chat center manager
│   │   │   ├── markdown-preview.js # Markdown editor
│   │   │   ├── search-suggestions.js # Search history & suggestions
│   │   │   └── real-time-notifications.js # WebSocket notifications
│   │   └── 📂 images/          # Image assets
│   │
│   ├── 📂 templates/blog/       # App-level templates
│   │   ├── base.html           # Base template with chat center integration
│   │   ├── 📂 articles/        # Article templates
│   │   │   ├── list.html       # Article list with search
│   │   │   ├── detail.html     # Article detail with client-side rendering
│   │   │   ├── form.html       # Markdown editor with live preview
│   │   │   └── my_drafts.html  # Draft management
│   │   ├── 📂 members/         # User profile templates
│   │   ├── 📂 messages/        # Messaging templates
│   │   ├── 📂 notifications/   # Notification center templates
│   │   ├── 📂 search/          # Advanced search templates
│   │   └── 📂 tags/            # Tag system templates
│   │
│   ├── 📂 templatetags/         # Custom template tags
│   │   └── blog_extras.py      # Markdown, @mention, date filters
│   │
│   ├── 📂 utils/                # Utility modules
│   │   ├── achievement_checker.py  # Achievement logic
│   │   └── seo.py              # SEO helper functions
│   │
│   ├── consumers.py            # WebSocket consumers (Notification, Chat)
│   ├── routing.py              # WebSocket URL routing
│   ├── sitemaps.py             # XML sitemap generation
│   ├── feeds.py                # RSS/Atom feed generation
│   ├── context_processors.py   # Custom context processors
│   ├── signals.py              # Django signals for automation
│   ├── urls.py                 # App routing with API endpoints
│   └── admin.py                # Admin panel configuration
│
├── 📂 media/                    # User-uploaded files
│   └── avatars/                # User avatars
│
├── 📂 static/                   # Project-level static files
│   ├── css/                    # Global styles
│   │   └── base.css           # Base styles with mobile navigation
│   └── images/                 # Shared images
│
├── 📂 templates/                # Project-level templates
│   └── home.html               # Landing page
│
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database
├── .env                        # Environment variables (SECRET_KEY, VAPID keys)
├── .env.example                # Environment variables template
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── .gitattributes             # Git attributes for language detection
```

## 📚 Learning Notes

### Advanced Django Concepts Implemented

#### 1. **Complex ORM Relationships**
```python
# Many-to-Many with Tag system
tags = models.ManyToManyField(Tag, blank=True)

# One-to-One for User Profile extension
user = models.OneToOneField(User, on_delete=models.CASCADE)

# Self-referential for Follow system
following = models.ManyToManyField('self', symmetrical=False)

# Foreign Keys with related names
parent_comment = models.ForeignKey('self', null=True, blank=True)
```

#### 2. **Custom Management Commands**
```bash
python manage.py create_default_achievements
python manage.py award_retroactive_achievements
python manage.py award_retroactive_points
```

#### 3. **Django Signals for Automation**
```python
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
```

#### 4. **Custom Context Processors**
```python
# Provide user display name and unread message count globally
TEMPLATES['OPTIONS']['context_processors'] = [
    'blog.context_processors.user_display_name',
    'blog.context_processors.unread_messages',
]
```

#### 5. **Ajax Interactions**
```javascript
// Like system with AJAX
fetch(url, {
    method: 'POST',
    headers: {'X-CSRFToken': csrftoken}
})
```

#### 6. **Custom Template Tags & Filters**
```django
{% load blog_extras %}
{{ article.content|markdown_to_html|safe }}
```

#### 7. **Form Validation & Processing**
```python
class ArticleForm(forms.ModelForm):
    def clean_tags_input(self):
        # Custom validation logic
        pass
```

### Database Design Highlights

| Model | Key Features | Relationships |
|-------|-------------|---------------|
| **Article** | Title, slug, content, tags, draft status | Author (FK), Tags (M2M), Comments, Likes |
| **Tag** | Name, slug, description | Articles (M2M) |
| **Comment** | Nested comments, likes, @mentions | Article (FK), Author (FK), Parent (Self FK) |
| **UserProfile** | Level system, points, achievements | User (O2O), Followers (M2M) |
| **Achievement** | Badge system, unlock conditions | Users (M2M) |
| **Message** | Thread-based conversations, recall | Sender/Recipient (FK), Parent Message |
| **Activity** | User action tracking | User (FK), Content Type (Generic FK) |
| **Notification** | Type, content, read status | User (FK), Content Type (Generic FK) |
| **NotificationPreference** | Personalized notification settings | User (O2O) |
| **ChatMessage** | Instant messages, read status | Sender/Recipient (FK), Room (FK) |
| **ChatRoom** | 1-on-1 chat rooms | Participants (M2M) |
| **SearchHistory** | Query, type, results count, deduplication | User (FK), indexed created_at |
| **PushSubscription** | Web Push endpoint, keys, expiration | User (FK) |

## 🎓 Key Learnings

### Django Advanced Patterns
✅ **Modular Model Design** - Separated models into logical modules (8 model files)
✅ **Signal-based Automation** - Profile creation, activity tracking, notification generation
✅ **Custom Management Commands** - Batch operations and data initialization
✅ **Context Processors** - Global template variables for all views
✅ **Custom Template Tags** - Markdown rendering, @mention parsing, date formatting
✅ **Generic Foreign Keys** - Flexible content type relationships for notifications
✅ **AJAX Integration** - Seamless user interactions without page reload
✅ **Form Validation** - Complex field validation and cleaning
✅ **WebSocket Integration** - Real-time bi-directional communication with Django Channels
✅ **ASGI Application** - Async server gateway interface for WebSocket support
✅ **Environment Variables** - Secure configuration with .env files

### Real-time Features
✅ **WebSocket Consumers** - Custom consumers for notifications and chat
✅ **Channel Layers** - InMemoryChannelLayer for WebSocket communication
✅ **Auto-reconnection** - Client-side reconnection logic for WebSocket
✅ **Typing Indicators** - Real-time typing status in chat
✅ **Message Read Receipts** - Track message read status
✅ **Web Push Notifications** - VAPID-based browser push notifications

### Frontend Engineering
✅ **Vanilla JavaScript ES6+** - Modern JavaScript without frameworks
✅ **Client-side Markdown Rendering** - marked.js for consistent rendering
✅ **Debounced Input** - Performance optimization for search suggestions
✅ **Keyboard Navigation** - Arrow keys, Enter, Esc for search UI
✅ **Event Delegation** - Efficient event handling for dynamic content
✅ **IME Composition Handling** - Support for Chinese input methods

### Architecture Best Practices
✅ **MVT Pattern** - Clear Model-View-Template separation
✅ **RESTful APIs** - JSON API endpoints for AJAX operations
✅ **DRY Principle** - Template inheritance and code reusability
✅ **Responsive Design** - Mobile-first CSS with media queries
✅ **Security** - CSRF protection, user authentication, permission checks, VAPID keys
✅ **Performance** - Query optimization with select_related, prefetch_related, indexing
✅ **SEO Best Practices** - Meta tags, sitemaps, RSS feeds, canonical URLs

### Tech Stack

#### Backend
- **Framework**: Django 6.0
- **Real-time**: Django Channels 4.3.2
- **Template Engine**: Django Template Language + Custom Tags
- **Database**: SQLite3 with complex ORM relationships and indexing
- **Media Handling**: Pillow 12.0.0 for image processing
- **Content Processing**: Markdown 3.10 for rich text
- **Web Push**: py-vapid 1.9.1 for VAPID authentication
- **ASGI Server**: Daphne (via Channels)

#### Frontend
- **Markup**: HTML5 with semantic elements
- **Styling**: CSS3 (Grid/Flexbox), custom gradients, animations
- **JavaScript**: Vanilla ES6+ (no frameworks)
- **Markdown Rendering**: marked.js v11.1.1
- **Syntax Highlighting**: highlight.js v11.9.0 (GitHub Dark theme)
- **Math Formulas**: KaTeX v0.16.9
- **Diagrams**: Mermaid v10.6.1
- **Real-time**: WebSocket API

#### DevOps & Tools
- **Version Control**: Git + GitHub
- **Environment Management**: python-dotenv
- **Package Management**: pip + requirements.txt
- **Protocol**: HTTP/HTTPS, WebSocket (ws/wss)

## 🔧 Development Roadmap

### ✅ Completed Features

- [x] User authentication and authorization
- [x] Extended user profiles with drag-drop avatar upload
- [x] Article CRUD with Markdown editor and live preview
- [x] Draft system with auto-save functionality
- [x] Tag system with cloud visualization
- [x] Comment system with nesting and @mentions
- [x] Like/Unlike functionality for articles and comments
- [x] Private messaging system with recall
- [x] Instant chat with WebSocket
- [x] Chat center (Facebook Messenger style)
- [x] Follow/Unfollow users
- [x] Achievement and badge system
- [x] Activity tracking and history
- [x] Reading progress tracking
- [x] Real-time notifications with WebSockets
- [x] Web Push notifications (VAPID)
- [x] Notification center with preferences
- [x] Advanced search with history and suggestions
- [x] SEO optimization (meta tags, sitemap, RSS feeds)
- [x] Syntax highlighting for code blocks
- [x] LaTeX math formula support (KaTeX)
- [x] Mermaid diagram support
- [x] Client-side Markdown rendering

### 🚀 Upcoming Features

- [ ] Image upload in articles (inline)
- [ ] Export articles (PDF, Markdown download)
- [ ] Email notifications
- [ ] Social authentication (Google, GitHub)
- [ ] Redis for Channels layer (production)
- [ ] PostgreSQL database migration
- [ ] Rate limiting and API throttling
- [ ] Comprehensive unit and integration tests
- [ ] Docker containerization
- [ ] CI/CD pipeline setup
- [ ] Production deployment guide
- [ ] Performance monitoring and analytics
- [ ] Content moderation system
- [ ] Multi-language support (i18n)

## 📝 Version History

### v3.0.0 (2025-12-26) - Real-time & Content Enhancement Release

**🔥 Major Features**

- ✨ **Real-time Communication**
  - WebSocket-based instant chat system
  - Real-time notifications with auto-reconnection
  - Web Push notifications with VAPID
  - Chat center with Facebook Messenger-style UI
  - Typing indicators and read receipts
  - Multiple chat windows support

- ✨ **Advanced Content Creation**
  - Markdown editor with live preview and synchronized scrolling
  - Syntax highlighting (highlight.js, GitHub Dark theme)
  - LaTeX math formula rendering (KaTeX)
  - Mermaid diagram support (flowcharts, sequence diagrams, etc.)
  - @Mention system with autocomplete
  - Draft system with auto-save
  - Client-side rendering for consistency

- ✨ **Search Enhancement**
  - Advanced search with multiple filters
  - Search history tracking with deduplication
  - Popular searches from last 7 days
  - Real-time search suggestions
  - Keyboard navigation support
  - Auto-complete for articles, tags, and authors

- ✨ **SEO & Performance**
  - Auto-generated meta descriptions
  - XML sitemap generation
  - RSS/Atom feeds
  - Open Graph and Twitter Card tags
  - Canonical URLs
  - Database indexing optimization

**🎨 UI/UX Improvements**

- Enhanced mobile navigation with improved spacing
- Chat windows in bottom-right corner
- Toast notifications system
- Unread message and notification badges
- Responsive design refinements
- IME composition support for Chinese input

**🔧 Technical Enhancements**

- Django Channels 4.3.2 integration
- ASGI application configuration
- WebSocket routing and consumers
- Environment variable configuration (.env)
- 8 modular model files
- API endpoints for AJAX operations
- Client-side JavaScript managers

**🐛 Bug Fixes**

- Fixed math formula rendering issues
- Fixed Chinese input (IME) in chat
- Fixed duplicate message display
- Fixed WebSocket disconnection on second message
- Fixed search form Enter key behavior
- Fixed chat window auto-open for recipients

### v2.0.0 (2025-12-22) - Social Features & Gamification Release

- ✨ Implement complete tag system with tag cloud
- ✨ Add private messaging system with threads
- ✨ Implement user following functionality
- ✨ Add achievement and badge system
- ✨ Implement points and level system (Bronze to Diamond)
- ✨ Add activity tracking system
- ✨ Implement reading history tracking
- ✨ Add comment system with nesting and likes
- ✨ Implement Ajax-based like system
- ✨ Add message notification system with auto-dismiss
- 🎨 Complete UI/UX redesign with modern gradients
- 🎨 Add responsive design for all pages
- 🔧 Optimize context processors for user display
- 🔧 Add custom management commands
- 🐛 Fix various UI and interaction bugs

### v1.5.0 (2025-12-20) - Core Features Release

- ✨ Implement user profile system with avatars
- ✨ Add article CRUD functionality
- ✨ Implement user authentication
- 🎨 Add member profile pages
- 🎨 Implement article list and detail pages

### v1.0.0 (2025-12-19) - Initial Release

- ✨ Initialize Django project structure
- ✨ Create blog application
- ✨ Implement home and about pages
- ✨ Configure static file system
- ✨ Integrate template inheritance architecture
- 🎨 Implement responsive UI design
- 📝 Complete project documentation

## 👨‍💻 Author

**Ru** - Full-Stack Django Developer

- **Project Goal**: Master advanced Django development and modern web technologies
- **Learning Focus**: WebSocket real-time communication, advanced ORM, content creation tools, SEO optimization
- **Achievement**: Built a production-ready blogging platform with real-time features and social networking
- **Tech Stack**: Django 6.0, Django Channels, WebSocket, JavaScript ES6+, CSS3, SQLite
- **Highlight Skills**: ASGI/WebSocket integration, client-side rendering, environment security, advanced search algorithms

## 🌟 Key Features Showcase

### 💬 Real-time Communication
WebSocket-powered instant chat with typing indicators, read receipts, and Facebook Messenger-style chat center. Real-time notifications keep users connected without page refreshes. Web Push notifications work even when the browser tab is closed.

### ✍️ Advanced Content Creation
Professional Markdown editor with live preview, syntax highlighting for code blocks, LaTeX math formulas (KaTeX), and Mermaid diagrams. Writers can create technical documentation, scientific articles, and interactive diagrams with ease.

### 🔍 Intelligent Search
Advanced search system with history tracking, popular searches display, and real-time auto-suggestions. Smart deduplication prevents duplicate searches within 5 minutes. Keyboard navigation (arrow keys, Enter, Esc) provides a seamless user experience.

### 🎮 Gamification System
Users progress through 5 levels (Bronze → Silver → Gold → Platinum → Diamond) by earning points through various activities. Automatic achievement unlocking and retroactive awards keep users engaged and motivated.

### 🌐 SEO Optimized
Auto-generated meta descriptions, XML sitemaps, RSS/Atom feeds, Open Graph tags, and Twitter Cards ensure maximum visibility on search engines and social media platforms.

### 🎨 Modern UI/UX
Responsive mobile-first design with custom gradients, smooth animations, toast notifications, and intuitive navigation. Chat windows, notification badges, and drag-drop avatar upload provide a polished user experience.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Django Official Documentation
- Python Community
- All contributors to open source

---

<div align="center">

**⭐ If this project helps you, please give it a Star!**

Made with ❤️ and Django

</div>
