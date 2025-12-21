"""
建立預設成就資料的管理命令
使用方式: python manage.py create_default_achievements
"""
from django.core.management.base import BaseCommand
from blog.models import Achievement


class Command(BaseCommand):
    help = '建立預設的成就徽章資料'

    def handle(self, *args, **options):
        achievements_data = [
            # 活躍度相關成就
            {
                'name': '初次登場',
                'description': '成功註冊並完成首次登入',
                'icon': '🎉',
                'category': 'activity',
                'points': 10,
                'condition_type': 'login_count',
                'condition_value': 1,
            },
            {
                'name': '常駐會員',
                'description': '連續 7 天登入平台',
                'icon': '🔥',
                'category': 'activity',
                'points': 50,
                'condition_type': 'consecutive_login',
                'condition_value': 7,
            },
            {
                'name': '百日堅持',
                'description': '累計登入 100 天',
                'icon': '💯',
                'category': 'activity',
                'points': 200,
                'condition_type': 'total_login',
                'condition_value': 100,
            },

            # 學習相關成就
            {
                'name': '初學者',
                'description': '發表第一篇文章',
                'icon': '📝',
                'category': 'learning',
                'points': 20,
                'condition_type': 'article_count',
                'condition_value': 1,
            },
            {
                'name': '創作達人',
                'description': '累計發表 10 篇文章',
                'icon': '✍️',
                'category': 'learning',
                'points': 100,
                'condition_type': 'article_count',
                'condition_value': 10,
            },
            {
                'name': '高產作家',
                'description': '累計發表 50 篇文章',
                'icon': '📚',
                'category': 'learning',
                'points': 500,
                'condition_type': 'article_count',
                'condition_value': 50,
            },
            {
                'name': '課程先鋒',
                'description': '完成第一門課程',
                'icon': '🎓',
                'category': 'learning',
                'points': 100,
                'condition_type': 'course_completed',
                'condition_value': 1,
            },
            {
                'name': '學習專家',
                'description': '完成 5 門課程',
                'icon': '🏆',
                'category': 'learning',
                'points': 300,
                'condition_type': 'course_completed',
                'condition_value': 5,
            },

            # 社交相關成就
            {
                'name': '社交新星',
                'description': '獲得第一個追蹤者',
                'icon': '⭐',
                'category': 'social',
                'points': 30,
                'condition_type': 'follower_count',
                'condition_value': 1,
            },
            {
                'name': '人氣王',
                'description': '擁有 50 位追蹤者',
                'icon': '👑',
                'category': 'social',
                'points': 150,
                'condition_type': 'follower_count',
                'condition_value': 50,
            },
            {
                'name': '超級巨星',
                'description': '擁有 100 位追蹤者',
                'icon': '🌟',
                'category': 'social',
                'points': 300,
                'condition_type': 'follower_count',
                'condition_value': 100,
            },
            {
                'name': '評論員',
                'description': '發表 10 則評論',
                'icon': '💬',
                'category': 'social',
                'points': 50,
                'condition_type': 'comment_count',
                'condition_value': 10,
            },

            # 貢獻相關成就
            {
                'name': '點讚達人',
                'description': '給予 100 個讚',
                'icon': '👍',
                'category': 'contribution',
                'points': 50,
                'condition_type': 'like_given',
                'condition_value': 100,
            },
            {
                'name': '人氣文章',
                'description': '單篇文章獲得 100 個讚',
                'icon': '❤️',
                'category': 'contribution',
                'points': 200,
                'condition_type': 'article_likes',
                'condition_value': 100,
            },
            {
                'name': '影響力者',
                'description': '文章總讚數達到 500',
                'icon': '💖',
                'category': 'contribution',
                'points': 500,
                'condition_type': 'total_likes',
                'condition_value': 500,
            },

            # 特殊成就
            {
                'name': '完美主義者',
                'description': '完成所有個人資料欄位',
                'icon': '✨',
                'category': 'special',
                'points': 50,
                'condition_type': 'profile_complete',
                'condition_value': 100,
            },
            {
                'name': '早起的鳥兒',
                'description': '在早上 6 點前發表文章',
                'icon': '🌅',
                'category': 'special',
                'points': 30,
                'condition_type': 'early_post',
                'condition_value': 6,
            },
            {
                'name': '夜貓子',
                'description': '在午夜 12 點後發表文章',
                'icon': '🌙',
                'category': 'special',
                'points': 30,
                'condition_type': 'late_post',
                'condition_value': 0,
            },
            {
                'name': '全能高手',
                'description': '達到鑽石等級',
                'icon': '💎',
                'category': 'special',
                'points': 1000,
                'condition_type': 'level',
                'condition_value': 5,
            },
            {
                'name': '開拓者',
                'description': '成為前 100 位註冊會員',
                'icon': '🚀',
                'category': 'special',
                'points': 100,
                'condition_type': 'early_member',
                'condition_value': 100,
            },
        ]

        created_count = 0
        updated_count = 0

        for data in achievements_data:
            achievement, created = Achievement.objects.update_or_create(
                name=data['name'],
                defaults={
                    'description': data['description'],
                    'icon': data['icon'],
                    'category': data['category'],
                    'points': data['points'],
                    'condition_type': data['condition_type'],
                    'condition_value': data['condition_value'],
                }
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ 建立成就: {achievement.icon} {achievement.name}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ 更新成就: {achievement.icon} {achievement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n完成！共建立 {created_count} 個新成就，更新 {updated_count} 個現有成就。')
        )
