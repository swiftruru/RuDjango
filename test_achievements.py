#!/usr/bin/env python
"""
測試成就系統的腳本
執行方式: python test_achievements.py
"""
import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Achievement, UserAchievement
from blog.utils.achievement_checker import check_article_achievements


def test_achievements():
    print("=" * 60)
    print("成就系統測試")
    print("=" * 60)

    # 1. 檢查成就是否已建立
    achievements = Achievement.objects.all()
    print(f"\n✓ 系統中共有 {achievements.count()} 個成就")

    # 按分類統計
    for category, name in Achievement.CATEGORY_CHOICES:
        count = Achievement.objects.filter(category=category).count()
        print(f"  - {name}: {count} 個")

    # 2. 列出所有成就
    print("\n所有成就列表：")
    print("-" * 60)
    for achievement in achievements:
        print(f"{achievement.icon} {achievement.name}")
        print(f"   分類: {achievement.get_category_display()}")
        print(f"   描述: {achievement.description}")
        print(f"   獎勵: +{achievement.points} XP")
        print(f"   條件: {achievement.condition_type} >= {achievement.condition_value}")
        print()

    # 3. 檢查使用者成就
    print("\n使用者成就統計：")
    print("-" * 60)
    users = User.objects.all()[:5]  # 只顯示前5個使用者

    for user in users:
        unlocked_count = UserAchievement.objects.filter(user=user).count()
        total_count = achievements.count()
        percentage = int((unlocked_count / total_count * 100)) if total_count > 0 else 0

        print(f"\n👤 {user.username}:")
        print(f"   已解鎖: {unlocked_count}/{total_count} ({percentage}%)")

        # 顯示已解鎖的成就
        user_achievements = UserAchievement.objects.filter(user=user).select_related('achievement')
        if user_achievements:
            print("   成就:")
            for ua in user_achievements:
                print(f"   {ua.achievement.icon} {ua.achievement.name} - {ua.unlocked_at.strftime('%Y-%m-%d')}")

    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)


if __name__ == '__main__':
    test_achievements()
