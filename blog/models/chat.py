"""
即時聊天相關的 Models
與傳統的私人訊息（Message）系統分離
"""

from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    """
    即時聊天訊息
    專門用於即時聊天視窗，與傳統私人訊息（Message）分離
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_chat_messages',
        verbose_name='發送者'
    )
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_chat_messages',
        verbose_name='接收者'
    )
    content = models.TextField(verbose_name='訊息內容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='發送時間')
    is_read = models.BooleanField(default=False, verbose_name='是否已讀')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='已讀時間')

    class Meta:
        verbose_name = '即時聊天訊息'
        verbose_name_plural = '即時聊天訊息'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['sender', 'recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
        ]

    def __str__(self):
        return f'{self.sender.username} → {self.recipient.username}: {self.content[:50]}'

    def mark_as_read(self):
        """標記為已讀"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])


class ChatRoom(models.Model):
    """
    聊天室（可選）
    用於追蹤兩個用戶之間的聊天狀態
    """
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user1',
        verbose_name='用戶1'
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chat_rooms_as_user2',
        verbose_name='用戶2'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='創建時間')
    last_message_at = models.DateTimeField(auto_now=True, verbose_name='最後訊息時間')

    class Meta:
        verbose_name = '聊天室'
        verbose_name_plural = '聊天室'
        ordering = ['-last_message_at']
        # 確保兩個用戶之間只有一個聊天室
        constraints = [
            models.UniqueConstraint(
                fields=['user1', 'user2'],
                name='unique_chat_room'
            )
        ]

    def __str__(self):
        return f'{self.user1.username} ↔ {self.user2.username}'

    @classmethod
    def get_or_create_room(cls, user1, user2):
        """
        獲取或創建聊天室
        確保用戶順序一致（按 ID 排序）
        """
        if user1.id > user2.id:
            user1, user2 = user2, user1

        room, created = cls.objects.get_or_create(
            user1=user1,
            user2=user2
        )
        return room

    def get_unread_count(self, user):
        """獲取未讀訊息數量"""
        return ChatMessage.objects.filter(
            sender=self.user1 if user == self.user2 else self.user2,
            recipient=user,
            is_read=False
        ).count()
