"""
補發所有使用者應得但尚未獲得的徽章
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.utils.achievement_checker import AchievementChecker


class Command(BaseCommand):
    help = '補發所有使用者應得但尚未獲得的徽章'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='只為特定使用者補發徽章',
        )

    def handle(self, *args, **options):
        username = options.get('username')

        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f'為使用者 {username} 補發徽章...\n')
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'找不到使用者: {username}'))
                return
        else:
            users = User.objects.all()
            self.stdout.write(f'為所有 {users.count()} 位使用者補發徽章...\n')

        total_awarded = 0

        for user in users:
            self.stdout.write(f'\n檢查使用者: {user.username}')

            checker = AchievementChecker(user)
            newly_unlocked = checker.check_all()

            if newly_unlocked:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ 為 {user.username} 補發了 {len(newly_unlocked)} 個徽章:'
                    )
                )
                for achievement in newly_unlocked:
                    self.stdout.write(f'    - {achievement.icon} {achievement.name} (+{achievement.points} 積分)')
                total_awarded += len(newly_unlocked)
            else:
                self.stdout.write(f'  - 沒有新徽章')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！總共補發了 {total_awarded} 個徽章'
            )
        )
