from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def hello(request):
    return HttpResponse('hello, world')

def hello2(request):
    return HttpResponse('hello, world2')

def about(request):
    return render(request, 'blog/about.html')

def home(request):
    person1 = {
        'name': '大頭綠',
        'age': 17,
        'slogan': ['唯天唯大', '如日方中', '英姿煥發']
    }
    person2 = {
        'name': '大頭藍',
        'age': 18,
        'slogan': ['志在四方', '勇往直前', '心懷天下']
    }
    person3 = {
        'name': '大頭紅',
        'age': 19,
        'slogan': ['才華洋溢', '氣宇軒昂', '光芒萬丈']
    }
    context = {
        'people':[person1, person2, person3],
        'version': 1.0,
        'date': '2025-12-19',
        'last_update': '2025-12-19'
    }
    return render(request, 'blog/home.html', context)

def member(request):
    """會員中心頁面 - 個人資料與活動儀表板"""
    # 模擬當前登入的會員資料 - 大頭綠
    current_member = {
        'name': '大頭綠',
        'username': 'greenbig',
        'email': 'green.big@tfghs.tp.edu.tw',
        'school': 'Taipei First Girls High School',
        'grade': '高二',
        'bio': '熱愛程式設計與科技創新，夢想成為全端工程師。喜歡用代碼解決生活中的問題，享受創造的樂趣。',
        'location': 'Taipei, Taiwan',
        'birthday': '2007-05-15',
        'joined_date': '2024-01-15',
        'level': 'Gold',
        'points': 2850,
        'next_level_points': 3500,
        'avatar_color': '#10b981',
        
        # 統計數據
        'stats': {
            'posts': 42,
            'comments': 156,
            'likes_received': 328,
            'followers': 89,
            'following': 45,
            'projects': 8
        },
        
        # 最近活動
        'recent_activities': [
            {
                'type': 'post',
                'title': '深入理解 Django ORM 查詢優化',
                'date': '2 小時前',
                'icon': '📝'
            },
            {
                'type': 'comment',
                'title': '在「Python 裝飾器進階應用」發表評論',
                'date': '5 小時前',
                'icon': '💬'
            },
            {
                'type': 'like',
                'title': '收到來自 3 位會員的按讚',
                'date': '1 天前',
                'icon': '❤️'
            },
            {
                'type': 'achievement',
                'title': '解鎖成就：連續發文 7 天',
                'date': '3 天前',
                'icon': '🏆'
            },
        ],
        
        # 技能標籤
        'skills': ['Python', 'Django', 'JavaScript', 'HTML/CSS', 'Git', 'SQL'],
        
        # 成就徽章
        'achievements': [
            {'name': '早起鳥', 'icon': '🌅', 'description': '連續 7 天早晨發文'},
            {'name': '熱心助人', 'icon': '🤝', 'description': '回覆超過 100 則評論'},
            {'name': '人氣作者', 'icon': '⭐', 'description': '單篇文章獲得 50+ 讚'},
            {'name': '程式大師', 'icon': '💻', 'description': '發布 10+ 技術教學'},
        ],
        
        # 學習進度
        'learning_progress': [
            {'course': 'Django 全端開發', 'progress': 75, 'color': '#667eea'},
            {'course': 'JavaScript 進階', 'progress': 60, 'color': '#f59e0b'},
            {'course': 'React 入門', 'progress': 40, 'color': '#06b6d4'},
        ]
    }
    
    context = {
        'member': current_member,
        'version': 1.0,
        'date': '2025-12-19',
        'last_update': '2025-12-19'
    }
    return render(request, 'blog/member.html', context)