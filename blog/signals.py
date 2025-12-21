from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Activity, Article


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
