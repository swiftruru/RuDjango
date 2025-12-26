"""
通知系統相關 Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


class Notification(models.Model):
    """
    通知模型
    支援多種類型的通知：留言、按讚、新追蹤者、私訊
    """

    NOTIFICATION_TYPES = [
        ('comment', '留言'),
        ('like', '按讚'),
        ('follower', '新追蹤者'),
        ('message', '私訊'),
        ('share', '分享'),
        ('mention', '提及'),
    ]

    # 接收通知的用戶
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收者'
    )

    # 觸發通知的用戶
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='發送者',
        null=True,
        blank=True
    )

    # 通知類型
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name='通知類型'
    )

    # 通知訊息
    message = models.TextField(
        verbose_name='通知內容'
    )

    # 相關物件（使用 GenericForeignKey）
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')

    # 連結（跳轉到相關頁面）
    link = models.CharField(
        max_length=500,
        verbose_name='連結',
        blank=True
    )

    # 已讀狀態
    is_read = models.BooleanField(
        default=False,
        verbose_name='是否已讀'
    )

    # 建立時間
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='建立時間'
    )

    # 已讀時間
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='已讀時間'
    )

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.get_notification_type_display()}: {self.message[:50]}"

    def mark_as_read(self):
        """標記為已讀"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

    def get_icon(self):
        """取得通知圖示"""
        icons = {
            'comment': '💬',
            'like': '❤️',
            'follower': '👥',
            'message': '✉️',
            'share': '🔗',
            'mention': '@',
        }
        return icons.get(self.notification_type, '🔔')

    def get_time_since(self):
        """取得時間差（人性化顯示）"""
        now = timezone.now()
        diff = now - self.created_at

        if diff.days > 30:
            return f"{diff.days // 30} 個月前"
        elif diff.days > 0:
            return f"{diff.days} 天前"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600} 小時前"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60} 分鐘前"
        else:
            return "剛剛"


class NotificationPreference(models.Model):
    """
    通知偏好設定
    讓用戶自訂接收哪些類型的通知
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preference',
        verbose_name='用戶'
    )

    # 各類型通知開關
    enable_comment_notifications = models.BooleanField(
        default=True,
        verbose_name='留言通知'
    )

    enable_like_notifications = models.BooleanField(
        default=True,
        verbose_name='按讚通知'
    )

    enable_follower_notifications = models.BooleanField(
        default=True,
        verbose_name='追蹤者通知'
    )

    enable_message_notifications = models.BooleanField(
        default=True,
        verbose_name='私訊通知'
    )

    enable_share_notifications = models.BooleanField(
        default=True,
        verbose_name='分享通知'
    )

    enable_mention_notifications = models.BooleanField(
        default=True,
        verbose_name='提及通知'
    )

    # Email 通知（未來功能）
    enable_email_notifications = models.BooleanField(
        default=False,
        verbose_name='Email 通知'
    )

    # 更新時間
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新時間'
    )

    class Meta:
        verbose_name = '通知偏好'
        verbose_name_plural = '通知偏好'

    def __str__(self):
        return f"{self.user.username} 的通知設定"

    def is_notification_enabled(self, notification_type):
        """檢查指定類型的通知是否啟用"""
        type_mapping = {
            'comment': self.enable_comment_notifications,
            'like': self.enable_like_notifications,
            'follower': self.enable_follower_notifications,
            'message': self.enable_message_notifications,
            'share': self.enable_share_notifications,
            'mention': self.enable_mention_notifications,
        }
        return type_mapping.get(notification_type, True)

    @classmethod
    def get_or_create_for_user(cls, user):
        """為用戶取得或建立通知偏好"""
        preference, created = cls.objects.get_or_create(user=user)
        return preference
