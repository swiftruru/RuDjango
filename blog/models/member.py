"""
會員相關的 Models
"""
import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver


def user_avatar_path(instance, filename):
    """
    自定義頭像上傳路徑和檔名
    格式: avatars/uid_{user_id}_{username}.{ext}
    """
    # 取得檔案副檔名
    ext = filename.split('.')[-1]
    # 建立新檔名: uid_{user_id}_{username}.{ext}
    new_filename = f'uid_{instance.user.id}_{instance.user.username}.{ext}'
    # 返回完整路徑
    return os.path.join('avatars', new_filename)


class UserProfile(models.Model):
    """使用者資料擴展"""
    LEVEL_CHOICES = [
        ('Bronze', '銅牌'),
        ('Silver', '銀牌'),
        ('Gold', '金牌'),
        ('Platinum', '白金'),
        ('Diamond', '鑽石'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True, verbose_name='個人簡介')
    avatar = models.ImageField(upload_to=user_avatar_path, null=True, blank=True, verbose_name='頭像')
    school = models.CharField(max_length=100, blank=True, verbose_name='學校')
    grade = models.CharField(max_length=50, blank=True, verbose_name='年級')
    location = models.CharField(max_length=100, blank=True, verbose_name='地點')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')

    # 等級系統
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Bronze', verbose_name='會員等級')
    points = models.IntegerField(default=0, verbose_name='積分')

    # 社交資料
    website = models.URLField(max_length=200, blank=True, verbose_name='個人網站')
    github = models.CharField(max_length=100, blank=True, verbose_name='GitHub')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return f'{self.user.username} 的個人資料'

    class Meta:
        verbose_name = '使用者資料'
        verbose_name_plural = '使用者資料'

    def get_next_level_points(self):
        """計算下一等級所需積分"""
        level_order = [
            ('Bronze', 1000),
            ('Silver', 2500),
            ('Gold', 5000),
            ('Platinum', 10000),
            ('Diamond', 20000),
        ]

        # 找到當前等級的位置
        for i, (level_name, threshold) in enumerate(level_order):
            if self.level == level_name:
                # 如果已經是最高等級，返回當前等級門檻
                if i == len(level_order) - 1:
                    return threshold
                # 否則返回下一個等級的門檻
                return level_order[i + 1][1]

        return 20000

    def add_points(self, points):
        """增加積分並自動升級"""
        self.points += points
        self._update_level()
        self.save()

    def _update_level(self):
        """根據積分更新等級"""
        if self.points >= 20000:
            self.level = 'Diamond'
        elif self.points >= 10000:
            self.level = 'Platinum'
        elif self.points >= 5000:
            self.level = 'Gold'
        elif self.points >= 2500:
            self.level = 'Silver'
        elif self.points >= 1000:
            self.level = 'Silver'
        else:
            self.level = 'Bronze'


class Skill(models.Model):
    """技能標籤"""
    name = models.CharField(max_length=50, unique=True, verbose_name='技能名稱')
    users = models.ManyToManyField(User, related_name='skills', blank=True, verbose_name='使用者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '技能標籤'
        verbose_name_plural = '技能標籤'
        ordering = ['name']


class Achievement(models.Model):
    """成就系統"""
    CATEGORY_CHOICES = [
        ('activity', '活躍度'),
        ('learning', '學習'),
        ('social', '社交'),
        ('contribution', '貢獻'),
        ('special', '特殊'),
    ]

    name = models.CharField(max_length=100, verbose_name='成就名稱')
    description = models.TextField(max_length=300, verbose_name='成就描述')
    icon = models.CharField(max_length=10, default='🏆', verbose_name='圖示')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='activity', verbose_name='分類')
    points = models.IntegerField(default=10, verbose_name='獲得積分')

    # 解鎖條件（可用於程式判斷）
    condition_type = models.CharField(max_length=50, blank=True, verbose_name='條件類型')
    condition_value = models.IntegerField(default=0, verbose_name='條件數值')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    def __str__(self):
        return f'{self.icon} {self.name}'

    class Meta:
        verbose_name = '成就'
        verbose_name_plural = '成就'
        ordering = ['category', 'name']


class UserAchievement(models.Model):
    """使用者成就記錄"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements', verbose_name='使用者')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, verbose_name='成就')
    unlocked_at = models.DateTimeField(auto_now_add=True, verbose_name='解鎖時間')

    def __str__(self):
        return f'{self.user.username} - {self.achievement.name}'

    class Meta:
        verbose_name = '使用者成就'
        verbose_name_plural = '使用者成就'
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']


class LearningCourse(models.Model):
    """學習課程"""
    name = models.CharField(max_length=100, verbose_name='課程名稱')
    description = models.TextField(max_length=500, blank=True, verbose_name='課程描述')
    color = models.CharField(max_length=7, default='#4CAF50', verbose_name='進度條顏色')
    total_lessons = models.IntegerField(default=10, verbose_name='總課程數')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '學習課程'
        verbose_name_plural = '學習課程'
        ordering = ['name']


class UserCourseProgress(models.Model):
    """使用者課程進度"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress', verbose_name='使用者')
    course = models.ForeignKey(LearningCourse, on_delete=models.CASCADE, verbose_name='課程')
    completed_lessons = models.IntegerField(default=0, verbose_name='已完成課程數')
    last_activity = models.DateTimeField(auto_now=True, verbose_name='最後活動時間')

    def __str__(self):
        return f'{self.user.username} - {self.course.name}'

    class Meta:
        verbose_name = '使用者課程進度'
        verbose_name_plural = '使用者課程進度'
        unique_together = ['user', 'course']
        ordering = ['-last_activity']

    @property
    def progress_percentage(self):
        """計算進度百分比"""
        if self.course.total_lessons == 0:
            return 0
        return int((self.completed_lessons / self.course.total_lessons) * 100)


class Activity(models.Model):
    """使用者活動記錄"""
    ACTIVITY_TYPES = [
        ('post', '發表文章'),
        ('comment', '發表評論'),
        ('like', '按讚'),
        ('achievement', '獲得成就'),
        ('level_up', '等級提升'),
        ('course', '完成課程'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', verbose_name='使用者')
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPES, verbose_name='活動類型')
    title = models.CharField(max_length=200, verbose_name='活動標題')
    description = models.TextField(max_length=500, blank=True, verbose_name='活動描述')
    icon = models.CharField(max_length=10, default='📝', verbose_name='圖示')
    related_object_id = models.IntegerField(null=True, blank=True, verbose_name='相關物件ID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    def __str__(self):
        return f'{self.user.username} - {self.title}'

    class Meta:
        verbose_name = '使用者活動'
        verbose_name_plural = '使用者活動'
        ordering = ['-created_at']


class Follow(models.Model):
    """追蹤系統"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following', verbose_name='追蹤者')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers', verbose_name='被追蹤者')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='追蹤時間')

    def __str__(self):
        return f'{self.follower.username} 追蹤 {self.following.username}'

    class Meta:
        verbose_name = '追蹤關係'
        verbose_name_plural = '追蹤關係'
        unique_together = ['follower', 'following']
        ordering = ['-created_at']


# ===== 信號處理器 =====

@receiver(pre_save, sender=UserProfile)
def delete_old_avatar(sender, instance, **kwargs):
    """
    在保存新頭像之前，自動刪除舊頭像檔案
    避免佔用 media 空間
    """
    if not instance.pk:
        # 如果是新建的 profile，不需要刪除舊檔案
        return

    try:
        # 取得資料庫中的舊 profile
        old_profile = UserProfile.objects.get(pk=instance.pk)

        # 如果舊 profile 有頭像，且新頭像與舊頭像不同
        if old_profile.avatar and old_profile.avatar != instance.avatar:
            # 刪除舊頭像檔案
            if os.path.isfile(old_profile.avatar.path):
                os.remove(old_profile.avatar.path)
    except UserProfile.DoesNotExist:
        # 如果找不到舊 profile，不做任何處理
        pass
    except Exception as e:
        # 記錄錯誤但不中斷保存流程
        print(f"刪除舊頭像時發生錯誤: {e}")
