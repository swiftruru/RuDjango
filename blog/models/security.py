"""
安全相關 Models
登入嘗試追蹤、IP 封鎖等
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class LoginAttempt(models.Model):
    """
    登入嘗試記錄
    追蹤所有登入嘗試（成功和失敗）
    """

    ATTEMPT_TYPES = [
        ('success', '成功'),
        ('failed', '失敗'),
    ]

    # 嘗試登入的用戶名（可能不存在）
    username = models.CharField(
        max_length=150,
        verbose_name='用戶名',
        db_index=True
    )

    # 實際用戶（如果存在）
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='login_attempts',
        verbose_name='用戶'
    )

    # IP 地址
    ip_address = models.GenericIPAddressField(
        verbose_name='IP 地址',
        db_index=True
    )

    # User Agent
    user_agent = models.TextField(
        verbose_name='User Agent',
        blank=True
    )

    # 嘗試類型
    attempt_type = models.CharField(
        max_length=10,
        choices=ATTEMPT_TYPES,
        verbose_name='嘗試類型',
        db_index=True
    )

    # 失敗原因
    failure_reason = models.CharField(
        max_length=200,
        verbose_name='失敗原因',
        blank=True
    )

    # 嘗試時間
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='嘗試時間',
        db_index=True
    )

    # 地理位置資訊（可選）
    country = models.CharField(
        max_length=100,
        verbose_name='國家',
        blank=True
    )

    city = models.CharField(
        max_length=100,
        verbose_name='城市',
        blank=True
    )

    class Meta:
        verbose_name = '登入嘗試'
        verbose_name_plural = '登入嘗試'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['ip_address', '-attempted_at']),
            models.Index(fields=['username', '-attempted_at']),
            models.Index(fields=['attempt_type', '-attempted_at']),
        ]

    def __str__(self):
        return f"{self.username} - {self.ip_address} - {self.get_attempt_type_display()} ({self.attempted_at})"

    @classmethod
    def record_attempt(cls, username, ip_address, user_agent, success, user=None, failure_reason=''):
        """
        記錄登入嘗試

        Args:
            username: 用戶名
            ip_address: IP 地址
            user_agent: User Agent
            success: 是否成功
            user: User 對象（可選）
            failure_reason: 失敗原因（可選）

        Returns:
            LoginAttempt instance
        """
        attempt = cls.objects.create(
            username=username,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            attempt_type='success' if success else 'failed',
            failure_reason=failure_reason
        )

        # 檢查是否需要發送安全警報
        if not success:
            cls.check_suspicious_activity(ip_address, username)

        return attempt

    @classmethod
    def check_suspicious_activity(cls, ip_address, username):
        """
        檢查可疑活動並發送警報

        Args:
            ip_address: IP 地址
            username: 用戶名
        """
        from blog.utils.admin_notifications import create_security_alert_notification, get_superusers

        # 檢查過去 5 分鐘內的失敗次數
        five_minutes_ago = timezone.now() - timedelta(minutes=5)

        # 檢查同一 IP 的失敗次數
        ip_failed_count = cls.objects.filter(
            ip_address=ip_address,
            attempt_type='failed',
            attempted_at__gte=five_minutes_ago
        ).count()

        # 如果超過 5 次失敗，發送警報
        if ip_failed_count >= 5:
            superusers = get_superusers()
            if superusers.exists():
                create_security_alert_notification(
                    admin_users=superusers,
                    alert_message=f"偵測到異常登入嘗試：IP {ip_address} 在5分鐘內嘗試登入失敗{ip_failed_count}次",
                    link="/admin/dashboard/security/login-attempts/"
                )

        # 檢查同一用戶名從不同 IP 的失敗次數
        username_failed_count = cls.objects.filter(
            username=username,
            attempt_type='failed',
            attempted_at__gte=five_minutes_ago
        ).values('ip_address').distinct().count()

        # 如果同一用戶名從 3 個以上不同 IP 嘗試登入，發送警報
        if username_failed_count >= 3:
            superusers = get_superusers()
            if superusers.exists():
                create_security_alert_notification(
                    admin_users=superusers,
                    alert_message=f"偵測到異常活動：用戶名 '{username}' 在5分鐘內從{username_failed_count}個不同IP嘗試登入",
                    link="/admin/dashboard/security/login-attempts/"
                )

    @classmethod
    def get_failed_attempts_by_ip(cls, ip_address, minutes=5):
        """
        獲取特定 IP 在指定時間內的失敗次數

        Args:
            ip_address: IP 地址
            minutes: 分鐘數

        Returns:
            int: 失敗次數
        """
        time_threshold = timezone.now() - timedelta(minutes=minutes)
        return cls.objects.filter(
            ip_address=ip_address,
            attempt_type='failed',
            attempted_at__gte=time_threshold
        ).count()

    @classmethod
    def is_ip_blocked(cls, ip_address, threshold=10, minutes=5):
        """
        檢查 IP 是否應該被封鎖

        Args:
            ip_address: IP 地址
            threshold: 失敗次數閾值
            minutes: 時間範圍（分鐘）

        Returns:
            bool: 是否應該封鎖
        """
        failed_count = cls.get_failed_attempts_by_ip(ip_address, minutes)
        return failed_count >= threshold


class IPBlacklist(models.Model):
    """
    IP 黑名單
    """

    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name='IP 地址'
    )

    reason = models.TextField(
        verbose_name='封鎖原因'
    )

    # 封鎖者
    blocked_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blocked_ips',
        verbose_name='封鎖者'
    )

    # 封鎖時間
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='封鎖時間'
    )

    # 解除封鎖時間（null 表示永久封鎖）
    unblock_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='解除封鎖時間'
    )

    # 是否啟用
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否啟用'
    )

    class Meta:
        verbose_name = 'IP 黑名單'
        verbose_name_plural = 'IP 黑名單'
        ordering = ['-blocked_at']

    def __str__(self):
        return f"{self.ip_address} - {self.reason}"

    @classmethod
    def is_blocked(cls, ip_address):
        """
        檢查 IP 是否在黑名單中

        Args:
            ip_address: IP 地址

        Returns:
            bool: 是否被封鎖
        """
        now = timezone.now()
        return cls.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).filter(
            models.Q(unblock_at__isnull=True) | models.Q(unblock_at__gt=now)
        ).exists()

    def is_expired(self):
        """檢查封鎖是否已過期"""
        if self.unblock_at is None:
            return False
        return timezone.now() > self.unblock_at


class IPWhitelist(models.Model):
    """
    IP 白名單
    白名單中的 IP 永不會被封鎖
    """

    ip_address = models.GenericIPAddressField(
        unique=True,
        verbose_name='IP 地址'
    )

    description = models.CharField(
        max_length=200,
        verbose_name='描述'
    )

    # 添加者
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='whitelisted_ips',
        verbose_name='添加者'
    )

    # 添加時間
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='添加時間'
    )

    # 是否啟用
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否啟用'
    )

    class Meta:
        verbose_name = 'IP 白名單'
        verbose_name_plural = 'IP 白名單'
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.ip_address} - {self.description}"

    @classmethod
    def is_whitelisted(cls, ip_address):
        """
        檢查 IP 是否在白名單中

        Args:
            ip_address: IP 地址

        Returns:
            bool: 是否在白名單中
        """
        return cls.objects.filter(
            ip_address=ip_address,
            is_active=True
        ).exists()
