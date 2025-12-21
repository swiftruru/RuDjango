"""
管理命令：為既有文章追溯積分
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import Article, UserProfile, Activity


class Command(BaseCommand):
    help = '為既有的文章追溯給予積分'

    def handle(self, *args, **options):
        """執行命令"""
        # 獲取所有文章
        articles = Article.objects.filter(author__isnull=False).select_related('author')

        total_articles = articles.count()
        points_per_article = 50
        users_updated = set()

        self.stdout.write(f'找到 {total_articles} 篇文章需要處理...')

        for article in articles:
            author = article.author

            # 確保使用者有 profile
            profile, created = UserProfile.objects.get_or_create(user=author)

            # 檢查是否已經有該文章的活動記錄（避免重複給分）
            existing_activity = Activity.objects.filter(
                user=author,
                activity_type='post',
                related_object_id=article.id
            ).exists()

            if not existing_activity:
                # 給予積分
                profile.add_points(points_per_article)

                # 記錄活動
                Activity.objects.create(
                    user=author,
                    activity_type='post',
                    title=f'發表了文章《{article.title}》',
                    description=f'獲得了 {points_per_article} 積分',
                    icon='📝',
                    related_object_id=article.id
                )

                users_updated.add(author.username)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ 為文章《{article.title}》給予 {author.username} {points_per_article} 積分'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'- 文章《{article.title}》已經給過積分，跳過'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！共更新 {len(users_updated)} 位使用者的積分'
            )
        )

        # 顯示每位使用者的總積分
        for username in users_updated:
            user = User.objects.get(username=username)
            profile = user.profile
            article_count = user.articles.count()
            self.stdout.write(
                f'{username}: {article_count} 篇文章，總積分 {profile.points} XP，等級 {profile.level}'
            )
