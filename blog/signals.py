from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Activity, Article, Comment, Like, Follow, UserCourseProgress


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """當新使用者註冊時，自動建立 UserProfile"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """當使用者儲存時，確保 UserProfile 也存在"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Article)
def award_points_for_article(sender, instance, created, **kwargs):
    """當使用者發表文章時，自動給予積分並記錄活動"""
    if created and instance.author:
        # 確保使用者有 profile
        profile, profile_created = UserProfile.objects.get_or_create(user=instance.author)

        # 給予 50 積分
        points_awarded = 50
        profile.add_points(points_awarded)

        # 記錄活動
        Activity.objects.create(
            user=instance.author,
            activity_type='post',
            title=f'發表了文章《{instance.title}》',
            description=f'獲得了 {points_awarded} 積分',
            icon='📝',
            related_object_id=instance.id
        )

        # 檢查並解鎖文章相關成就
        from .utils.achievement_checker import check_article_achievements
        newly_unlocked = check_article_achievements(instance.author)

        # 可以在這裡添加成就解鎖通知
        if newly_unlocked:
            for achievement in newly_unlocked:
                print(f'🎉 {instance.author.username} 解鎖了成就: {achievement.icon} {achievement.name}')


@receiver(post_save, sender=Comment)
def check_comment_achievements_signal(sender, instance, created, **kwargs):
    """當使用者發表評論時，檢查評論相關成就"""
    if created and instance.author:
        from .utils.achievement_checker import check_comment_achievements
        newly_unlocked = check_comment_achievements(instance.author)

        if newly_unlocked:
            for achievement in newly_unlocked:
                print(f'🎉 {instance.author.username} 解鎖了成就: {achievement.icon} {achievement.name}')


@receiver(post_save, sender=Follow)
def check_follower_achievements_signal(sender, instance, created, **kwargs):
    """當使用者獲得新追蹤者時，檢查追蹤者相關成就"""
    if created:
        # 檢查被追蹤者（following）的成就
        from .utils.achievement_checker import check_follower_achievements
        newly_unlocked = check_follower_achievements(instance.following)

        if newly_unlocked:
            for achievement in newly_unlocked:
                print(f'🎉 {instance.following.username} 解鎖了成就: {achievement.icon} {achievement.name}')


@receiver(post_save, sender=Like)
def check_like_achievements_signal(sender, instance, created, **kwargs):
    """當使用者按讚時，檢查按讚相關成就"""
    if created:
        from .utils.achievement_checker import check_like_achievements

        # 檢查按讚者的成就
        newly_unlocked = check_like_achievements(instance.user, instance.article)

        if newly_unlocked:
            for achievement in newly_unlocked:
                if achievement:
                    print(f'🎉 解鎖了成就: {achievement.icon} {achievement.name}')


@receiver(post_save, sender=UserCourseProgress)
def check_course_achievements_signal(sender, instance, created, **kwargs):
    """當使用者更新課程進度時，檢查課程相關成就"""
    # 檢查是否完成課程
    if instance.completed_lessons >= instance.course.total_lessons:
        from .utils.achievement_checker import check_course_achievements
        newly_unlocked = check_course_achievements(instance.user)

        if newly_unlocked:
            for achievement in newly_unlocked:
                print(f'🎉 {instance.user.username} 解鎖了成就: {achievement.icon} {achievement.name}')


@receiver(post_save, sender=UserProfile)
def check_profile_achievements_signal(sender, instance, created, **kwargs):
    """當使用者更新個人資料時，檢查個人資料完整度相關成就"""
    if not created:  # 只在更新時檢查，不在創建時檢查
        from .utils.achievement_checker import check_profile_achievements
        newly_unlocked = check_profile_achievements(instance.user)

        if newly_unlocked:
            for achievement in newly_unlocked:
                print(f'🎉 {instance.user.username} 解鎖了成就: {achievement.icon} {achievement.name}')
