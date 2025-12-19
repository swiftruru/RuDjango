from django.shortcuts import render


def home(request):
    """專案首頁視圖"""
    context = {
        'project_name': 'RuDjango',
        'version': '1.0.0',
        'apps': [
            {
                'name': 'Blog',
                'description': 'Team showcase and blog system',
                'icon': '📝',
                'url': '/blog/',
                'features': ['Team Members', 'Dynamic Content', 'Responsive Design']
            },
            {
                'name': 'Admin',
                'description': 'Django administration interface',
                'icon': '⚙️',
                'url': '/admin/',
                'features': ['User Management', 'Data Control', 'System Config']
            },
        ],
        'tech_stack': [
            {'name': 'Django', 'version': '6.0', 'icon': '🎯'},
            {'name': 'Python', 'version': '3.13', 'icon': '🐍'},
            {'name': 'SQLite', 'version': '3', 'icon': '💾'},
            {'name': 'HTML/CSS', 'version': '5/3', 'icon': '🎨'},
        ],
        'stats': {
            'apps': 1,
            'templates': 3,
            'views': 4,
            'urls': 2,
        }
    }
    return render(request, 'home.html', context)
