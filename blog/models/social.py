"""
社群互動相關的 Models
包含: @提及、文章協作、使用者群組、活動/公告系統
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .article import Article, Comment


class Mention(models.Model):
    """
    @提及功能模型
    記錄在文章、留言中提及其他使用者的情況
    """
    MENTION_TYPE_CHOICES = [
        ('article', '文章'),
        ('comment', '留言'),
        ('message', '訊息'),
    ]

    # 被提及的使用者
    mentioned_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentions_received',
        verbose_name='被提及使用者'
    )

    # 提及者
    mentioning_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='mentions_made',
        verbose_name='提及者'
    )

    # 提及類型和相關物件
    mention_type = models.CharField(
        max_length=20,
        choices=MENTION_TYPE_CHOICES,
        verbose_name='提及類型'
    )

    # 關聯到文章（如果是在文章中提及）
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mentions',
        verbose_name='相關文章'
    )

    # 關聯到留言（如果是在留言中提及）
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mentions',
        verbose_name='相關留言'
    )

    # 提及的具體內容（前後文）
    context = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='提及內容'
    )

    # 已讀狀態
    is_read = models.BooleanField(default=False, verbose_name='已讀')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='提及時間')

    def __str__(self):
        return f'@{self.mentioned_user.username} 被 {self.mentioning_user.username} 提及'

    class Meta:
        verbose_name = '提及'
        verbose_name_plural = '提及'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mentioned_user', '-created_at']),
        ]


class ArticleCollaborator(models.Model):
    """
    文章協作者模型
    允許多位作者共同編輯一篇文章
    """
    ROLE_CHOICES = [
        ('owner', '擁有者'),
        ('editor', '編輯者'),
        ('viewer', '檢視者'),
    ]

    PERMISSION_CHOICES = [
        ('read', '僅讀取'),
        ('comment', '可留言'),
        ('edit', '可編輯'),
        ('full', '完全控制'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='collaborators',
        verbose_name='文章'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='collaborated_articles',
        verbose_name='協作者'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='editor',
        verbose_name='角色'
    )

    permission = models.CharField(
        max_length=20,
        choices=PERMISSION_CHOICES,
        default='edit',
        verbose_name='權限'
    )

    # 邀請狀態
    is_accepted = models.BooleanField(default=False, verbose_name='已接受邀請')
    invited_at = models.DateTimeField(auto_now_add=True, verbose_name='邀請時間')
    accepted_at = models.DateTimeField(null=True, blank=True, verbose_name='接受時間')

    # 邀請者
    invited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='collaboration_invitations_sent',
        verbose_name='邀請者'
    )

    def __str__(self):
        return f'{self.user.username} 協作於 {self.article.title}'

    def accept_invitation(self):
        """接受協作邀請"""
        self.is_accepted = True
        self.accepted_at = timezone.now()
        self.save()

    def can_edit(self):
        """檢查是否有編輯權限"""
        return self.permission in ['edit', 'full'] and self.is_accepted

    def can_delete(self):
        """檢查是否有刪除權限"""
        return self.permission == 'full' and self.is_accepted

    class Meta:
        verbose_name = '文章協作者'
        verbose_name_plural = '文章協作者'
        unique_together = ['article', 'user']
        ordering = ['-invited_at']


class ArticleEditHistory(models.Model):
    """
    文章編輯歷史記錄
    用於協作文章的版本追蹤
    """
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='edit_history',
        verbose_name='文章'
    )

    editor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='article_edits',
        verbose_name='編輯者'
    )

    # 編輯前後的內容
    previous_title = models.CharField(max_length=100, verbose_name='修改前標題')
    new_title = models.CharField(max_length=100, verbose_name='修改後標題')
    previous_content = models.TextField(verbose_name='修改前內容')
    new_content = models.TextField(verbose_name='修改後內容')

    # 編輯摘要
    edit_summary = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='編輯摘要'
    )

    edited_at = models.DateTimeField(auto_now_add=True, verbose_name='編輯時間')

    def __str__(self):
        editor_name = self.editor.username if self.editor else '未知使用者'
        return f'{editor_name} 編輯了 {self.article.title}'

    class Meta:
        verbose_name = '文章編輯歷史'
        verbose_name_plural = '文章編輯歷史'
        ordering = ['-edited_at']


class UserGroup(models.Model):
    """
    使用者群組模型
    讓使用者可以建立興趣社群、學習小組等
    """
    GROUP_TYPE_CHOICES = [
        ('public', '公開群組'),
        ('private', '私密群組'),
        ('invite_only', '邀請制群組'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name='群組名稱')
    description = models.TextField(max_length=500, verbose_name='群組描述')

    # 群組圖片
    cover_image = models.ImageField(
        upload_to='group_covers/',
        null=True,
        blank=True,
        verbose_name='封面圖片'
    )

    # 群組類型
    group_type = models.CharField(
        max_length=20,
        choices=GROUP_TYPE_CHOICES,
        default='public',
        verbose_name='群組類型'
    )

    # 群組創建者
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_groups',
        verbose_name='創建者'
    )

    # 群組成員（多對多關係）
    members = models.ManyToManyField(
        User,
        through='GroupMembership',
        related_name='joined_groups',
        verbose_name='成員'
    )

    # 群組標籤
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='標籤',
        help_text='用逗號分隔多個標籤'
    )

    # 統計資訊
    member_count = models.IntegerField(default=1, verbose_name='成員數量')
    post_count = models.IntegerField(default=0, verbose_name='文章數量')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.name

    def is_member(self, user):
        """檢查使用者是否為群組成員"""
        return self.members.filter(id=user.id).exists()

    def is_admin(self, user):
        """檢查使用者是否為群組管理員"""
        return GroupMembership.objects.filter(
            group=self,
            user=user,
            role__in=['admin', 'owner']
        ).exists()

    def can_join(self, user):
        """檢查使用者是否可以加入群組"""
        if self.is_member(user):
            return False
        if self.group_type == 'public':
            return True
        return False

    class Meta:
        verbose_name = '使用者群組'
        verbose_name_plural = '使用者群組'
        ordering = ['-created_at']


class GroupMembership(models.Model):
    """
    群組成員關係模型
    記錄使用者在群組中的角色和權限
    """
    ROLE_CHOICES = [
        ('owner', '群組擁有者'),
        ('admin', '管理員'),
        ('moderator', '版主'),
        ('member', '成員'),
    ]

    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='群組'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        verbose_name='使用者'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member',
        verbose_name='角色'
    )

    # 加入方式
    join_method = models.CharField(
        max_length=20,
        choices=[
            ('created', '創建'),
            ('joined', '主動加入'),
            ('invited', '被邀請'),
        ],
        default='joined',
        verbose_name='加入方式'
    )

    joined_at = models.DateTimeField(auto_now_add=True, verbose_name='加入時間')

    # 成員統計
    posts_count = models.IntegerField(default=0, verbose_name='發文數')
    comments_count = models.IntegerField(default=0, verbose_name='留言數')

    def __str__(self):
        return f'{self.user.username} @ {self.group.name}'

    class Meta:
        verbose_name = '群組成員'
        verbose_name_plural = '群組成員'
        unique_together = ['group', 'user']
        ordering = ['-joined_at']


class GroupPost(models.Model):
    """
    群組文章模型
    群組內的討論文章
    """
    POST_TYPE_CHOICES = [
        ('discussion', '討論'),
        ('question', '提問'),
        ('announcement', '公告'),
        ('share', '分享'),
    ]

    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='所屬群組'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_posts',
        verbose_name='作者'
    )

    post_type = models.CharField(
        max_length=20,
        choices=POST_TYPE_CHOICES,
        default='discussion',
        verbose_name='文章類型'
    )

    title = models.CharField(max_length=200, verbose_name='標題')
    content = models.TextField(verbose_name='內容')

    # 是否置頂
    is_pinned = models.BooleanField(default=False, verbose_name='置頂')

    # 統計
    views_count = models.IntegerField(default=0, verbose_name='瀏覽數')
    likes_count = models.IntegerField(default=0, verbose_name='按讚數')
    comments_count = models.IntegerField(default=0, verbose_name='留言數')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return f'{self.title} @ {self.group.name}'

    class Meta:
        verbose_name = '群組文章'
        verbose_name_plural = '群組文章'
        ordering = ['-is_pinned', '-created_at']


class Event(models.Model):
    """
    活動/公告系統模型
    用於發布線上活動、課程、公告等
    """
    EVENT_TYPE_CHOICES = [
        ('announcement', '公告'),
        ('online_event', '線上活動'),
        ('course', '課程'),
        ('competition', '競賽'),
        ('meetup', '聚會'),
    ]

    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已發布'),
        ('ongoing', '進行中'),
        ('completed', '已結束'),
        ('cancelled', '已取消'),
    ]

    # 基本資訊
    title = models.CharField(max_length=200, verbose_name='活動標題')
    description = models.TextField(verbose_name='活動描述')
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        verbose_name='活動類型'
    )

    # 組織者
    organizer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organized_events',
        verbose_name='組織者'
    )

    # 關聯群組（如果是群組活動）
    group = models.ForeignKey(
        UserGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='events',
        verbose_name='關聯群組'
    )

    # 活動封面
    cover_image = models.ImageField(
        upload_to='event_covers/',
        null=True,
        blank=True,
        verbose_name='封面圖片'
    )

    # 時間資訊
    start_time = models.DateTimeField(verbose_name='開始時間')
    end_time = models.DateTimeField(verbose_name='結束時間')
    registration_deadline = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='報名截止時間'
    )

    # 地點資訊
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='地點'
    )
    online_link = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='線上連結'
    )

    # 參與人數限制
    max_participants = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='參與人數上限'
    )

    # 參與者
    participants = models.ManyToManyField(
        User,
        through='EventParticipant',
        related_name='joined_events',
        verbose_name='參與者'
    )

    # 狀態
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name='狀態'
    )

    # 統計
    views_count = models.IntegerField(default=0, verbose_name='瀏覽數')
    participants_count = models.IntegerField(default=0, verbose_name='參與人數')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.title

    def is_ongoing(self):
        """檢查活動是否正在進行"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.status == 'published'

    def is_full(self):
        """檢查活動是否已滿"""
        if not self.max_participants:
            return False
        return self.participants_count >= self.max_participants

    def can_register(self):
        """檢查是否可以報名"""
        now = timezone.now()
        if self.registration_deadline and now > self.registration_deadline:
            return False
        if self.is_full():
            return False
        if self.status != 'published':
            return False
        return True

    class Meta:
        verbose_name = '活動/公告'
        verbose_name_plural = '活動/公告'
        ordering = ['-start_time']


class EventParticipant(models.Model):
    """
    活動參與者模型
    """
    STATUS_CHOICES = [
        ('registered', '已報名'),
        ('confirmed', '已確認'),
        ('attended', '已參加'),
        ('cancelled', '已取消'),
    ]

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name='participant_records',
        verbose_name='活動'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='event_participations',
        verbose_name='參與者'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='registered',
        verbose_name='狀態'
    )

    # 報名資訊
    note = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='備註'
    )

    registered_at = models.DateTimeField(auto_now_add=True, verbose_name='報名時間')

    def __str__(self):
        return f'{self.user.username} @ {self.event.title}'

    class Meta:
        verbose_name = '活動參與者'
        verbose_name_plural = '活動參與者'
        unique_together = ['event', 'user']
        ordering = ['-registered_at']


class Announcement(models.Model):
    """
    系統公告模型
    用於發布全站公告、更新通知等
    """
    PRIORITY_CHOICES = [
        ('low', '低'),
        ('normal', '一般'),
        ('high', '高'),
        ('urgent', '緊急'),
    ]

    title = models.CharField(max_length=200, verbose_name='公告標題')
    content = models.TextField(verbose_name='公告內容')

    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name='優先級'
    )

    # 公告作者（管理員）
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name='發布者'
    )

    # 是否顯示
    is_active = models.BooleanField(default=True, verbose_name='啟用')

    # 是否置頂
    is_pinned = models.BooleanField(default=False, verbose_name='置頂')

    # 有效期限
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='過期時間'
    )

    # 統計
    views_count = models.IntegerField(default=0, verbose_name='瀏覽數')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='發布時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.title

    def is_expired(self):
        """檢查公告是否已過期"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at

    def is_visible(self):
        """檢查公告是否應該顯示"""
        return self.is_active and not self.is_expired()

    class Meta:
        verbose_name = '系統公告'
        verbose_name_plural = '系統公告'
        ordering = ['-is_pinned', '-created_at']
