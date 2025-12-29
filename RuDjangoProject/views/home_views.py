"""
Project home page views
"""
from django.shortcuts import render


def home(request):
    """Project home page view"""
    context = {
        'project_name': 'RuDjango',
        'tagline': 'Modern Community Platform',
        'version': '2.0.0',
        'description': 'A feature-rich Django community platform with real-time chat, content management, and comprehensive admin dashboard',

        'features': [
            {
                'icon': '✍️',
                'title': 'Content Management',
                'description': 'Markdown editor with syntax highlighting, LaTeX formulas, and Mermaid diagrams',
                'items': ['Rich Text Editor', 'Code Highlighting', 'Math Formulas', 'Diagrams']
            },
            {
                'icon': '💬',
                'title': 'Real-time Chat',
                'description': 'WebSocket-powered instant messaging with typing indicators and read receipts',
                'items': ['Instant Messaging', 'Typing Indicators', 'Read Receipts', 'Chat History']
            },
            {
                'icon': '🔔',
                'title': 'Notifications',
                'description': 'Real-time WebSocket notifications with Web Push support',
                'items': ['Real-time Updates', 'Web Push', 'Email Alerts', 'Custom Preferences']
            },
            {
                'icon': '👥',
                'title': 'User System',
                'description': 'Complete member management with profiles, levels, and achievements',
                'items': ['User Profiles', 'Level System', 'Achievements', 'Follow System']
            },
            {
                'icon': '🔍',
                'title': 'Advanced Search',
                'description': 'Powerful search with history, suggestions, and analytics',
                'items': ['Full-text Search', 'Search History', 'Hot Searches', 'Smart Filters']
            },
            {
                'icon': '📊',
                'title': 'Admin Dashboard',
                'description': 'Modern admin interface for complete platform management',
                'items': ['User Management', 'Content Moderation', 'Analytics', 'Security Monitoring']
            },
        ],

        'tech_stack': [
            {'name': 'Django', 'version': '4.2', 'category': 'Backend'},
            {'name': 'Django Channels', 'version': '4.3', 'category': 'WebSocket'},
            {'name': 'Python', 'version': '3.9+', 'category': 'Language'},
            {'name': 'JavaScript ES6+', 'version': 'Latest', 'category': 'Frontend'},
            {'name': 'Tailwind CSS', 'version': '3.0', 'category': 'Styling'},
            {'name': 'PostgreSQL/SQLite', 'version': '3+', 'category': 'Database'},
        ],

        'stats': {
            'models': '20+',
            'views': '50+',
            'apis': '30+',
            'templates': '40+',
        },

        'quick_links': [
            {'name': 'Blog Platform', 'url': '/blog/', 'icon': '📝'},
            {'name': 'Admin Dashboard', 'url': '/dashboard/', 'icon': '⚙️'},
            {'name': 'About', 'url': '/blog/about/', 'icon': '💡'},
        ]
    }
    return render(request, 'home.html', context)
