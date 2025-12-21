"""
成就解鎖檢查器
自動檢查使用者是否符合成就條件，並自動解鎖
"""
from django.utils import timezone
from django.db.models import Count
from ..models import Achievement, UserAchievement, Activity, UserProfile


class AchievementChecker:
    """成就檢查器類別"""

    def __init__(self, user):
        self.user = user

    def check_all(self):
        """檢查所有成就"""
        newly_unlocked = []

        # 獲取所有成就
        all_achievements = Achievement.objects.all()

        for achievement in all_achievements:
            # 檢查是否已解鎖
            if UserAchievement.objects.filter(user=self.user, achievement=achievement).exists():
                continue

            # 根據條件類型檢查
            if self._check_condition(achievement):
                # 解鎖成就
                user_achievement = UserAchievement.objects.create(
                    user=self.user,
                    achievement=achievement
                )
                newly_unlocked.append(achievement)

                # 增加積分
                profile = UserProfile.objects.get(user=self.user)
                profile.add_points(achievement.points)

                # 記錄活動
                Activity.objects.create(
                    user=self.user,
                    activity_type='achievement',
                    title=f'獲得成就: {achievement.name}',
                    description=achievement.description,
                    icon='🏆',
                    related_object_id=achievement.id
                )

        return newly_unlocked

    def _check_condition(self, achievement):
        """檢查單個成就的條件是否達成"""
        condition_type = achievement.condition_type
        condition_value = achievement.condition_value

        try:
            if condition_type == 'article_count':
                return self.user.articles.count() >= condition_value

            elif condition_type == 'login_count':
                # 需要在登入時記錄
                return True  # 簡化處理

            elif condition_type == 'consecutive_login':
                # 需要專門的登入記錄系統
                return False  # 暫不實作

            elif condition_type == 'total_login':
                # 需要專門的登入記錄系統
                return False  # 暫不實作

            elif condition_type == 'course_completed':
                from ..models import UserCourseProgress
                from django.db import models as db_models
                completed_courses = UserCourseProgress.objects.filter(
                    user=self.user,
                    completed_lessons__gte=db_models.F('course__total_lessons')
                ).count()
                return completed_courses >= condition_value

            elif condition_type == 'follower_count':
                return self.user.followers.count() >= condition_value

            elif condition_type == 'comment_count':
                # 需要評論系統
                return False  # 暫不實作

            elif condition_type == 'like_given':
                # 需要按讚系統
                return False  # 暫不實作

            elif condition_type == 'article_likes':
                # 需要按讚系統
                return False  # 暫不實作

            elif condition_type == 'total_likes':
                # 需要按讚系統
                return False  # 暫不實作

            elif condition_type == 'profile_complete':
                return self._check_profile_completeness() >= condition_value

            elif condition_type == 'early_post':
                # 檢查是否有早上發表的文章
                early_articles = self.user.articles.filter(
                    created_at__hour__lt=condition_value
                )
                return early_articles.exists()

            elif condition_type == 'late_post':
                # 檢查是否有午夜後發表的文章
                late_articles = self.user.articles.filter(
                    created_at__hour__gte=23
                )
                return late_articles.exists()

            elif condition_type == 'level':
                profile = UserProfile.objects.get(user=self.user)
                level_order = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond']
                current_level_index = level_order.index(profile.level) + 1
                return current_level_index >= condition_value

            elif condition_type == 'early_member':
                # 檢查是否為前N位會員
                from django.contrib.auth.models import User
                user_rank = User.objects.filter(
                    date_joined__lt=self.user.date_joined
                ).count() + 1
                return user_rank <= condition_value

        except Exception as e:
            print(f"檢查成就條件時發生錯誤: {e}")
            return False

        return False

    def _check_profile_completeness(self):
        """檢查個人資料完整度（百分比）"""
        try:
            profile = UserProfile.objects.get(user=self.user)
        except UserProfile.DoesNotExist:
            return 0

        total_fields = 10
        filled_fields = 0

        # 檢查各個欄位
        if self.user.first_name:
            filled_fields += 1
        if self.user.email:
            filled_fields += 1
        if profile.bio:
            filled_fields += 1
        if profile.school:
            filled_fields += 1
        if profile.grade:
            filled_fields += 1
        if profile.location:
            filled_fields += 1
        if profile.birthday:
            filled_fields += 1
        if profile.website or profile.github:
            filled_fields += 1
        if self.user.skills.exists():
            filled_fields += 1
        if profile.avatar:
            filled_fields += 1

        return int((filled_fields / total_fields) * 100)

    def check_article_achievements(self):
        """專門檢查文章相關成就（在發表文章後調用）"""
        article_achievements = Achievement.objects.filter(
            condition_type='article_count'
        )

        newly_unlocked = []
        article_count = self.user.articles.count()

        for achievement in article_achievements:
            # 檢查是否已解鎖
            if UserAchievement.objects.filter(user=self.user, achievement=achievement).exists():
                continue

            # 檢查是否達成條件
            if article_count >= achievement.condition_value:
                UserAchievement.objects.create(
                    user=self.user,
                    achievement=achievement
                )
                newly_unlocked.append(achievement)

                # 增加積分
                profile = UserProfile.objects.get(user=self.user)
                profile.add_points(achievement.points)

                # 記錄活動
                Activity.objects.create(
                    user=self.user,
                    activity_type='achievement',
                    title=f'獲得成就: {achievement.name}',
                    description=achievement.description,
                    icon='🏆',
                    related_object_id=achievement.id
                )

        return newly_unlocked


def check_and_unlock_achievements(user):
    """快速檢查並解鎖成就的函數"""
    checker = AchievementChecker(user)
    return checker.check_all()


def check_article_achievements(user):
    """檢查文章相關成就的快速函數"""
    checker = AchievementChecker(user)
    return checker.check_article_achievements()
