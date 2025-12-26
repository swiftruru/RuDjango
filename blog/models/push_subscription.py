"""
Web Push 訂閱相關的 Models
"""

from django.db import models
from django.contrib.auth.models import User


class PushSubscription(models.Model):
    """
    用戶的 Web Push 訂閱資訊
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='push_subscriptions',
        verbose_name='用戶'
    )
    endpoint = models.URLField(verbose_name='推播端點', unique=True)
    p256dh = models.CharField(max_length=255, verbose_name='P256DH 密鑰')
    auth = models.CharField(max_length=255, verbose_name='Auth 密鑰')

    # 裝置資訊
    user_agent = models.TextField(blank=True, verbose_name='用戶代理')
    device_type = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='裝置類型',
        choices=[
            ('desktop', '桌面'),
            ('mobile', '手機'),
            ('tablet', '平板'),
        ]
    )

    # 訂閱狀態
    is_active = models.BooleanField(default=True, verbose_name='是否啟用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='訂閱時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')
    last_used_at = models.DateTimeField(null=True, blank=True, verbose_name='最後使用時間')

    # 推播失敗記錄
    failure_count = models.IntegerField(default=0, verbose_name='失敗次數')
    last_failure_at = models.DateTimeField(null=True, blank=True, verbose_name='最後失敗時間')

    class Meta:
        verbose_name = 'Web Push 訂閱'
        verbose_name_plural = 'Web Push 訂閱'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['endpoint']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.device_type or "unknown"} ({self.created_at.strftime("%Y-%m-%d")})'

    def mark_as_used(self):
        """標記為已使用"""
        from django.utils import timezone
        self.last_used_at = timezone.now()
        self.save(update_fields=['last_used_at'])

    def mark_as_failed(self):
        """標記推播失敗"""
        from django.utils import timezone
        self.failure_count += 1
        self.last_failure_at = timezone.now()

        # 如果連續失敗超過 3 次，停用訂閱
        if self.failure_count >= 3:
            self.is_active = False

        self.save(update_fields=['failure_count', 'last_failure_at', 'is_active'])

    def reset_failures(self):
        """重置失敗計數"""
        self.failure_count = 0
        self.last_failure_at = None
        self.is_active = True
        self.save(update_fields=['failure_count', 'last_failure_at', 'is_active'])
