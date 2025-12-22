# 🚀 RuDjango - Django Learning Project

<div align="center">

![Django](https://img.shields.io/badge/Django-6.0-green?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.13-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

A modern web application for learning and practicing Django framework

[Features](#-features) • [Quick Start](#-quick-start) • [Project Structure](#-project-structure) • [Learning Notes](#-learning-notes)

</div>

---

## 📖 About

RuDjango is a comprehensive web application built with Django 6.0, demonstrating advanced Django framework concepts and modern web development practices. This full-featured blogging platform showcases everything from project architecture, ORM relationships, user authentication to real-time interactions and gamification systems.

## ✨ Features

### 🎯 Core Features
- ✅ **User System** - Complete authentication with registration, login/logout
- ✅ **User Profiles** - Extended profiles with avatars, bio, social links, and gamification
- ✅ **Article Management** - Full CRUD operations with rich text editor
- ✅ **Comment System** - Nested comments with real-time interaction
- ✅ **Like System** - Ajax-based likes for articles and comments
- ✅ **Tag System** - Multi-tag support with tag cloud and filtering
- ✅ **Private Messaging** - Inbox/Outbox with thread-based conversations
- ✅ **Follow System** - User following with follower/following lists
- ✅ **Reading History** - Automatic tracking of article reading progress
- ✅ **Achievements** - Badge system with retroactive achievement awards
- ✅ **Points & Levels** - Gamification with Bronze to Diamond tiers
- ✅ **Activity Tracking** - User activity logging and statistics

### 💬 Social Features
- **Direct Messages** - Private messaging between users with reply threads
- **User Following** - Follow system with real-time follower counts
- **Comment Interactions** - Nested comment system with like support
- **Share Functionality** - Social media sharing integration
- **User Profiles** - Comprehensive profile pages with activity stats

### 🎮 Gamification System
- **Level System** - 5-tier progression (Bronze, Silver, Gold, Platinum, Diamond)
- **Achievement Badges** - Automated achievement unlocking based on activities
- **Points System** - Earn points for articles, comments, and interactions
- **Progress Tracking** - Visual progress bars and statistics

### 🎨 UI/UX Features
- **Responsive Design** - Mobile-first, adapts to all screen sizes
- **Message Notifications** - Toast notifications with auto-dismiss
- **Tag Cloud** - Dynamic font sizing based on article count
- **Modern Gradients** - Beautiful gradient color schemes throughout
- **Interactive Animations** - Smooth hover effects and transitions
- **Dark Theme Elements** - Consistent modern dark mode styling

## 🚀 Quick Start

### Requirements

- Python 3.13+
- Django 6.0+
- pip package manager

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/swiftruru/RuDjango.git
cd RuDjango/RuDjangoProject
```

2. **Create virtual environment**
```bash
python -m venv ../RuDjango-env
source ../RuDjango-env/bin/activate  # macOS/Linux
# or
..\RuDjango-env\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install -r ../requirements.txt
# or manually install:
pip install django pillow markdown pygments sqlparse
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create default achievements**
```bash
python manage.py create_default_achievements
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Start development server**
```bash
python manage.py runserver
```

8. **Browse the application**
- Home: http://127.0.0.1:8000/
- Blog: http://127.0.0.1:8000/blog/
- Tags: http://127.0.0.1:8000/blog/tags/
- Messages: http://127.0.0.1:8000/blog/messages/inbox/
- Admin Panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
RuDjangoProject/
│
├── 📂 RuDjangoProject/          # Project configuration
│   ├── settings.py              # Global settings with custom context processors
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI deployment interface
│   └── asgi.py                  # ASGI deployment interface
│
├── 📂 blog/                     # Main blog application
│   │
│   ├── 📂 models/               # Data models (modular design)
│   │   ├── article.py          # Article, Tag, Comment, Like models
│   │   └── member.py           # UserProfile, Achievement, Activity models
│   │
│   ├── 📂 views/                # View controllers
│   │   ├── article_views.py    # Article CRUD, comments, likes
│   │   ├── member_views.py     # User profiles, following, achievements
│   │   └── message_views.py    # Private messaging system
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
│   │   ├── css/                # Stylesheets
│   │   │   ├── articles/       # Article-related styles
│   │   │   ├── members/        # Member profile styles
│   │   │   ├── messages.css    # Messaging system styles
│   │   │   └── tags.css        # Tag cloud styles
│   │   ├── js/                 # JavaScript files
│   │   │   ├── articles/       # Article interactions (like, share)
│   │   │   └── members/        # Member interactions (follow)
│   │   └── images/             # Image assets
│   │
│   ├── 📂 templates/blog/       # App-level templates
│   │   ├── base.html           # Base template with navigation
│   │   ├── articles/           # Article templates
│   │   ├── members/            # User profile templates
│   │   ├── messages/           # Messaging templates
│   │   └── tags/               # Tag system templates
│   │
│   ├── 📂 templatetags/         # Custom template tags
│   │   └── blog_extras.py      # Custom filters and tags
│   │
│   ├── 📂 utils/                # Utility modules
│   │   └── achievement_checker.py  # Achievement logic
│   │
│   ├── context_processors.py   # Custom context processors
│   ├── signals.py              # Django signals for automation
│   ├── urls.py                 # App routing
│   └── admin.py                # Admin panel configuration
│
├── 📂 media/                    # User-uploaded files
│   └── avatars/                # User avatars
│
├── 📂 static/                   # Project-level static files
│   ├── css/                    # Global styles
│   └── images/                 # Shared images
│
├── 📂 templates/                # Project-level templates
│   └── home.html               # Landing page
│
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database
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
| **Article** | Title, slug, content, tags | Author (FK), Tags (M2M), Comments, Likes |
| **Tag** | Name, slug, description | Articles (M2M) |
| **Comment** | Nested comments, likes | Article (FK), Author (FK), Parent (Self FK) |
| **UserProfile** | Level system, points, achievements | User (O2O), Followers (M2M) |
| **Achievement** | Badge system, unlock conditions | Users (M2M) |
| **Message** | Thread-based conversations | Sender/Recipient (FK), Parent Message |
| **Activity** | User action tracking | User (FK), Content Type (Generic FK) |

## 🎓 Key Learnings

### Django Advanced Patterns
✅ **Modular Model Design** - Separated models into logical modules  
✅ **Signal-based Automation** - Profile creation, activity tracking  
✅ **Custom Management Commands** - Batch operations and data initialization  
✅ **Context Processors** - Global template variables for all views  
✅ **Custom Template Tags** - Markdown rendering, date formatting  
✅ **Generic Foreign Keys** - Flexible content type relationships  
✅ **AJAX Integration** - Seamless user interactions without page reload  
✅ **Form Validation** - Complex field validation and cleaning  

### Architecture Best Practices
✅ **MVT Pattern** - Clear Model-View-Template separation  
✅ **RESTful URLs** - Semantic and hierarchical URL structure  
✅ **DRY Principle** - Template inheritance and code reusability  
✅ **Responsive Design** - Mobile-first CSS with media queries  
✅ **Security** - CSRF protection, user authentication, permission checks  
✅ **Performance** - Query optimization with select_related, prefetch_related  

### Tech Stack
- **Backend Framework**: Django 6.0
- **Template Engine**: Django Template Language + Custom Tags
- **Frontend**: HTML5, CSS3 (Grid/Flexbox), Vanilla JavaScript
- **Database**: SQLite3 with complex ORM relationships
- **Media Handling**: Pillow for image processing
- **Markdown**: Python-Markdown for rich text content
- **Syntax Highlighting**: Pygments for code blocks
- **Version Control**: Git + GitHub

## 🔧 Development Roadmap

### ✅ Completed Features
- [x] User authentication and authorization
- [x] Extended user profiles with gamification
- [x] Article CRUD with rich text support
- [x] Tag system with cloud visualization
- [x] Comment system with nesting
- [x] Like/Unlike functionality
- [x] Private messaging system
- [x] Follow/Unfollow users
- [x] Achievement and badge system
- [x] Activity tracking and history
- [x] Reading progress tracking

### 🚀 Upcoming Features
- [ ] Search functionality (full-text search)
- [ ] Email notifications
- [ ] REST API with Django REST Framework
- [ ] Real-time notifications with WebSockets
- [ ] Article drafts and scheduling
- [ ] Image upload in articles
- [ ] Export articles (PDF, Markdown)
- [ ] Social authentication (Google, GitHub)
- [ ] Rate limiting and throttling
- [ ] Comprehensive test coverage
- [ ] Docker deployment setup
- [ ] Production deployment guide

## 📝 Version History

### v2.0.0 (2025-12-22) - Major Feature Release
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

### v1.5.0 (2025-12-20)
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

- Project Goal: Master Django full-stack development and modern web practices
- Learning Focus: Advanced ORM, User Systems, Real-time Interactions, Gamification
- Achievement: Built a production-ready blogging platform with social features
- Tech Stack: Django, Python, JavaScript, CSS3, SQLite

## 🌟 Key Features Showcase

### 🎮 Gamification System
Users progress through 5 levels (Bronze → Silver → Gold → Platinum → Diamond) by earning points through various activities. Automatic achievement unlocking keeps users engaged.

### 💬 Social Interactions
Complete social platform with following, private messaging, nested comments, and like systems. Users can build their network and engage with content seamlessly.

### 🏷️ Smart Tagging
Multi-tag support with beautiful tag cloud visualization. Tags scale dynamically based on popularity, making content discovery intuitive.

### 📊 Activity Tracking
Comprehensive activity logging system tracks all user actions, providing insights into user behavior and enabling retroactive achievement awards.

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
