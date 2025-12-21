"""
初始化會員系統測試資料
這個腳本會建立成就、課程、技能等測試資料
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from blog.models import Achievement, LearningCourse, Skill
from django.contrib.auth.models import User


def create_achievements():
    """建立成就資料"""
    achievements_data = [
        {
            'name': '早起鳥',
            'description': '連續 7 天早晨發文',
            'icon': '🌅',
            'category': 'activity',
            'points': 50,
            'condition_type': 'consecutive_morning_posts',
            'condition_value': 7
        },
        {
            'name': '熱心助人',
            'description': '回覆超過 100 則評論',
            'icon': '🤝',
            'category': 'social',
            'points': 100,
            'condition_type': 'total_comments',
            'condition_value': 100
        },
        {
            'name': '人氣作者',
            'description': '單篇文章獲得 50+ 讚',
            'icon': '⭐',
            'category': 'contribution',
            'points': 150,
            'condition_type': 'post_likes',
            'condition_value': 50
        },
        {
            'name': '程式大師',
            'description': '發布 10+ 技術教學',
            'icon': '💻',
            'category': 'contribution',
            'points': 200,
            'condition_type': 'tutorial_posts',
            'condition_value': 10
        },
        {
            'name': '學習之星',
            'description': '完成 5 門課程',
            'icon': '📚',
            'category': 'learning',
            'points': 100,
            'condition_type': 'completed_courses',
            'condition_value': 5
        },
        {
            'name': '社交達人',
            'description': '追蹤者超過 100 人',
            'icon': '👥',
            'category': 'social',
            'points': 150,
            'condition_type': 'followers_count',
            'condition_value': 100
        },
    ]

    for data in achievements_data:
        achievement, created = Achievement.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f'✅ 建立成就：{achievement}')
        else:
            print(f'⏭️  成就已存在：{achievement}')


def create_courses():
    """建立學習課程資料"""
    courses_data = [
        {
            'name': 'Django 全端開發',
            'description': '從零開始學習 Django 框架，建立完整的 Web 應用程式',
            'color': '#667eea',
            'total_lessons': 30
        },
        {
            'name': 'JavaScript 進階',
            'description': '深入學習 JavaScript ES6+ 語法和非同步程式設計',
            'color': '#f59e0b',
            'total_lessons': 25
        },
        {
            'name': 'React 入門',
            'description': '學習 React 基礎，包含 Hooks、Components 和狀態管理',
            'color': '#06b6d4',
            'total_lessons': 20
        },
        {
            'name': 'Python 資料科學',
            'description': '使用 Pandas、NumPy 進行資料分析',
            'color': '#8b5cf6',
            'total_lessons': 28
        },
        {
            'name': 'SQL 資料庫設計',
            'description': '關聯式資料庫設計與 SQL 查詢優化',
            'color': '#ec4899',
            'total_lessons': 22
        },
    ]

    for data in courses_data:
        course, created = LearningCourse.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            print(f'✅ 建立課程：{course}')
        else:
            print(f'⏭️  課程已存在：{course}')


def create_skills():
    """建立技能標籤資料"""
    skills_data = [
        'Python', 'Django', 'JavaScript', 'React', 'Vue.js',
        'HTML/CSS', 'Git', 'SQL', 'PostgreSQL', 'MongoDB',
        'Docker', 'AWS', 'Linux', 'Node.js', 'TypeScript',
        'Machine Learning', 'Data Science', 'API Design', 'Testing', 'CI/CD'
    ]

    for skill_name in skills_data:
        skill, created = Skill.objects.get_or_create(name=skill_name)
        if created:
            print(f'✅ 建立技能：{skill}')
        else:
            print(f'⏭️  技能已存在：{skill}')


def main():
    print('=' * 60)
    print('開始初始化會員系統測試資料...')
    print('=' * 60)

    print('\n📜 建立成就資料...')
    create_achievements()

    print('\n📚 建立學習課程資料...')
    create_courses()

    print('\n🏷️  建立技能標籤資料...')
    create_skills()

    print('\n' + '=' * 60)
    print('✅ 初始化完成！')
    print('=' * 60)
    print('\n現在您可以：')
    print('1. 登入管理後台 (http://localhost:8000/admin/) 管理資料')
    print('2. 登入會員中心查看您的個人資料')
    print('3. 編輯個人資料、添加技能標籤')
    print('4. 在後台手動分配成就和課程進度')


if __name__ == '__main__':
    main()
