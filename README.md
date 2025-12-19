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

RuDjango is a practice project built with Django 6.0, aimed at deep learning of Django framework's core concepts and best practices. Through implementing a complete web application, this project covers everything from project architecture, routing configuration, template system to static file management.

## ✨ Features

### 🎯 Implemented Features
- ✅ **Modular App Design** - Utilizing Django App architecture for feature separation
- ✅ **Dynamic Template System** - Integrating Django Template Language with template inheritance
- ✅ **Static Resource Management** - Standardized CSS/JS/Images organization
- ✅ **Responsive Interface** - Modern UI design supporting multiple devices
- ✅ **URL Routing Configuration** - Hierarchical URL management with clear routing structure
- ✅ **Team Showcase System** - Dynamic rendering of team member information

### 🎨 Pages
- **Home** - Showcasing team members and project features
- **About** - Project information and technical highlights
- **Admin Panel** - Django Admin system integration

## 🚀 Quick Start

### Requirements

- Python 3.13+
- Django 6.0+
- pip package manager

### Installation Steps

1. **Clone the repository**
```bash
git clone https://github.com/swiftruru/RuDjango.git
cd RuDjango
```

2. **Create virtual environment**
```bash
python -m venv RuDjango-env
source RuDjango-env/bin/activate  # macOS/Linux
# or
RuDjango-env\Scripts\activate     # Windows
```

3. **Install dependencies**
```bash
pip install django
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create superuser (optional)**
```bash
python manage.py createsuperuser
```

6. **Start development server**
```bash
python manage.py runserver
```

7. **Browse the application**
- Home: http://127.0.0.1:8000/
- Blog Home: http://127.0.0.1:8000/blog/
- About Page: http://127.0.0.1:8000/blog/about
- Admin Panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
RuDjangoProject/
│
├── 📂 RuDjangoProject/          # Project configuration
│   ├── settings.py              # Global settings
│   ├── urls.py                  # Main URL configuration
│   ├── wsgi.py                  # WSGI deployment interface
│   └── asgi.py                  # ASGI deployment interface
│
├── 📂 blog/                     # Blog application
│   ├── 📂 static/blog/          # App-level static files
│   │   ├── css/                 # Stylesheets
│   │   │   ├── home.css        # Home page styles
│   │   │   └── about.css       # About page styles
│   │   ├── images/              # Image assets
│   │   └── js/                  # JavaScript files
│   │
│   ├── 📂 templates/blog/       # App-level templates
│   │   ├── base.html           # Base template
│   │   ├── home.html           # Home page template
│   │   └── about.html          # About page template
│   │
│   ├── views.py                # View logic
│   ├── urls.py                 # App routing
│   ├── models.py               # Data models
│   └── admin.py                # Admin configuration
│
├── 📂 static/                   # Project-level static files
│   └── css/
│       └── base.css            # Global base styles
│
├── 📂 templates/                # Project-level templates
│
├── manage.py                   # Django management script
├── db.sqlite3                  # SQLite database
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore configuration
```

## 📚 Learning Notes

### Django Core Concepts in Practice

#### 1. **Project Architecture Design**
- **Project Level (RuDjangoProject)**: Handles global configuration, URL distribution, shared resources
- **App Level (blog)**: Implements specific features, independent and reusable

#### 2. **URL Routing Configuration**
```python
# Project level - Traffic distribution
path('', views.home, name='home')          # Root path
path('blog/', include('blog.urls'))         # App routing

# App level - Specific routes
path('', views.home, name='blog_home')      # Blog home
path('about', views.about, name='about')    # About page
```

#### 3. **Template Inheritance System**
```django
{# Base template base.html #}
{% block content %}{% endblock %}

{# Child template home.html #}
{% extends 'blog/base.html' %}
{% block content %}
  <!-- Page content -->
{% endblock %}
```

#### 4. **Static File Management**
- **Configuration**: `STATIC_URL` + `STATICFILES_DIRS`
- **Best Practice**: App-specific static files in `app/static/app/` directory
- **Usage**: `{% static 'blog/css/home.css' %}`

#### 5. **Views and Context**
```python
def home(request):
    context = {
        'people': [person1, person2, person3],
        'version': 1.0,
    }
    return render(request, 'blog/home.html', context)
```

### Issues Encountered and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Page not found (404) | Root path not configured | Add `path('', views.home)` in main urls.py |
| Static files not loading | Incorrect path configuration | Use `{% static 'blog/css/...' %}` format |
| TemplateDoesNotExist | Template path incorrect | After moving to app, use `'blog/template.html'` |

## 🎓 Key Learnings

### Django Best Practices
✅ **Modular Design** - Independent App structure  
✅ **DRY Principle** - Template inheritance to avoid code repetition  
✅ **Naming Conventions** - Clear URL names and template paths  
✅ **Static Resource Separation** - Page-specific CSS independently managed  
✅ **MVT Architecture** - Clear Model-View-Template separation  

### Tech Stack
- **Backend Framework**: Django 6.0
- **Template Engine**: Django Template Language
- **Frontend Styling**: CSS3 (Responsive Design)
- **Database**: SQLite3
- **Version Control**: Git

## 🔧 Development Roadmap

### Upcoming Features
- [ ] Database model design and ORM operations
- [ ] Form handling and validation
- [ ] User authentication system
- [ ] RESTful API development
- [ ] Test writing
- [ ] Deployment configuration

## 📝 Version History

### v1.0.0 (2025-12-19)
- ✨ Initialize Django project structure
- ✨ Create blog application
- ✨ Implement home and about pages
- ✨ Configure static file system
- ✨ Integrate template inheritance architecture
- 🎨 Implement responsive UI design
- 📝 Complete project documentation

## 👨‍💻 Author

**Ru** - Django Learner

- Project Goal: Master Django full-stack development
- Learning Focus: MVT architecture, ORM, RESTful API
- Practice Direction: From basics to advanced, building complete projects step by step

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
