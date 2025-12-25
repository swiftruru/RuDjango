"""
文章相關的 Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


class Tag(models.Model):
    """標籤模型"""
    name = models.CharField(max_length=50, unique=True, verbose_name='標籤名稱')
    slug = models.SlugField(max_length=50, unique=True, blank=True, verbose_name='網址名稱')
    description = models.TextField(blank=True, verbose_name='標籤描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')

    def save(self, *args, **kwargs):
        """自動生成 slug"""
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @property
    def article_count(self):
        """返回使用此標籤的文章數量"""
        return self.articles.count()

    class Meta:
        verbose_name = '標籤'
        verbose_name_plural = '標籤'
        ordering = ['name']


class Article(models.Model):
    """文章模型"""
    # 文章狀態選項
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('published', '已發布'),
        ('scheduled', '已排程'),
    ]

    title = models.CharField(max_length=100, verbose_name='標題')
    content = models.TextField(verbose_name='內容')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='articles',
        null=True,
        blank=True,
        verbose_name='作者'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='articles',
        blank=True,
        verbose_name='標籤'
    )

    # 草稿與排程功能
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='published',
        verbose_name='狀態'
    )
    publish_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='排程發布時間'
    )

    # 閱讀時間估算 (分鐘)
    reading_time = models.IntegerField(
        default=0,
        verbose_name='閱讀時間(分鐘)'
    )

    # 草稿版本系統 - 用於已發布文章的編輯草稿
    has_draft = models.BooleanField(
        default=False,
        verbose_name='有未發布的草稿'
    )
    draft_title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='草稿標題'
    )
    draft_content = models.TextField(
        null=True,
        blank=True,
        verbose_name='草稿內容'
    )
    draft_tags_json = models.TextField(
        null=True,
        blank=True,
        verbose_name='草稿標籤(JSON)'
    )
    draft_updated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='草稿更新時間'
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """儲存時自動計算閱讀時間"""
        if self.content:
            # 假設平均閱讀速度為每分鐘 200 個中文字或 300 個英文字
            # 簡化計算：每 200 個字元約 1 分鐘
            word_count = len(self.content)
            self.reading_time = max(1, round(word_count / 200))

        # 檢查是否為首次發布（從草稿或排程變為已發布）
        if self.pk:  # 如果文章已存在（不是第一次創建）
            try:
                old_article = Article.objects.get(pk=self.pk)
                # 如果從草稿或排程狀態變為發布狀態，更新 created_at 為當前時間
                if old_article.status in ['draft', 'scheduled'] and self.status == 'published':
                    self.created_at = timezone.now()
            except Article.DoesNotExist:
                pass

        # 如果是排程文章，自動設定狀態
        if self.publish_at:
            # 確保 publish_at 是時區感知的
            if timezone.is_naive(self.publish_at):
                self.publish_at = timezone.make_aware(self.publish_at)

            if self.publish_at > timezone.now():
                self.status = 'scheduled'

        super().save(*args, **kwargs)

    @property
    def is_published(self):
        """檢查文章是否已發布"""
        if self.status == 'published':
            return True
        if self.status == 'scheduled' and self.publish_at and self.publish_at <= timezone.now():
            return True
        return False

    @property
    def can_be_viewed(self):
        """檢查文章是否可以被查看（已發布或到達排程時間）"""
        return self.is_published

    def get_table_of_contents(self):
        """從文章內容生成目錄"""
        import re
        # 匹配 Markdown 標題 (# 到 ####)
        headings = re.findall(r'^(#{1,4})\s+(.+)$', self.content, re.MULTILINE)
        toc = []
        for level, title in headings:
            # 生成錨點 ID (簡化處理)
            anchor_id = re.sub(r'[^\w\s-]', '', title.lower())
            anchor_id = re.sub(r'[-\s]+', '-', anchor_id).strip('-')
            toc.append({
                'level': len(level),
                'title': title.strip(),
                'anchor': anchor_id
            })
        return toc

    def save_draft_version(self, title, content, tags_input):
        """儲存草稿版本（不影響已發布內容）"""
        import json
        self.draft_title = title
        self.draft_content = content
        self.draft_tags_json = json.dumps(tags_input) if tags_input else None
        self.has_draft = True
        self.draft_updated_at = timezone.now()
        self.save()

    def publish_draft_version(self):
        """將草稿版本發布為正式內容"""
        import json
        if not self.has_draft:
            return False

        # 更新正式內容
        self.title = self.draft_title
        self.content = self.draft_content

        # 處理標籤
        if self.draft_tags_json:
            tag_names = json.loads(self.draft_tags_json)
            self.tags.clear()
            for tag_name in tag_names:
                if tag_name.strip():
                    tag, created = Tag.objects.get_or_create(name=tag_name.strip())
                    self.tags.add(tag)

        # 清除草稿版本
        self.has_draft = False
        self.draft_title = None
        self.draft_content = None
        self.draft_tags_json = None
        self.draft_updated_at = None
        self.save()
        return True

    def discard_draft_version(self):
        """捨棄草稿版本"""
        self.has_draft = False
        self.draft_title = None
        self.draft_content = None
        self.draft_tags_json = None
        self.draft_updated_at = None
        self.save()

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-created_at']


class ArticleReadHistory(models.Model):
    """文章閱讀記錄模型"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reading_history',
        verbose_name='用戶'
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='read_records',
        verbose_name='文章'
    )
    first_read_at = models.DateTimeField(auto_now_add=True, verbose_name='首次閱讀時間')
    last_read_at = models.DateTimeField(auto_now=True, verbose_name='最後閱讀時間')
    read_count = models.IntegerField(default=1, verbose_name='閱讀次數')
    reading_time_seconds = models.IntegerField(default=0, verbose_name='閱讀時長(秒)')

    def __str__(self):
        return f"{self.user.username} - {self.article.title}"

    class Meta:
        verbose_name = '文章閱讀記錄'
        verbose_name_plural = '文章閱讀記錄'
        ordering = ['-last_read_at']
        unique_together = ['user', 'article']  # 確保每個用戶對每篇文章只有一條記錄


class Comment(models.Model):
    """文章留言模型"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='文章'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='留言者'
    )
    content = models.TextField(verbose_name='留言內容')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='留言時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父留言'
    )

    def __str__(self):
        return f"{self.author.username} 在 {self.article.title} 的留言"

    class Meta:
        verbose_name = '留言'
        verbose_name_plural = '留言'
        ordering = ['-created_at']


class Like(models.Model):
    """文章按讚模型"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='文章'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='按讚者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='按讚時間')

    def __str__(self):
        return f"{self.user.username} 讚了 {self.article.title}"

    class Meta:
        verbose_name = '按讚'
        verbose_name_plural = '按讚'
        unique_together = ['article', 'user']  # 確保每個使用者對每篇文章只能按一次讚
        ordering = ['-created_at']


class Bookmark(models.Model):
    """文章書籤/收藏模型"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='文章'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='收藏者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='收藏時間')
    note = models.TextField(blank=True, verbose_name='筆記')

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.article.title}"

    class Meta:
        verbose_name = '書籤'
        verbose_name_plural = '書籤'
        unique_together = ['article', 'user']
        ordering = ['-created_at']


class ArticleShare(models.Model):
    """文章分享統計模型"""
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('line', 'LINE'),
        ('copy', '複製連結'),
        ('other', '其他'),
    ]

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='文章'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='article_shares',
        verbose_name='分享者'
    )
    platform = models.CharField(
        max_length=20,
        choices=PLATFORM_CHOICES,
        verbose_name='分享平台'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='IP位址'
    )
    shared_at = models.DateTimeField(auto_now_add=True, verbose_name='分享時間')

    def __str__(self):
        user_str = self.user.username if self.user else "訪客"
        return f"{user_str} 在 {self.platform} 分享了 {self.article.title}"

    class Meta:
        verbose_name = '文章分享'
        verbose_name_plural = '文章分享'
        ordering = ['-shared_at']
