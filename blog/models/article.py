"""
文章相關的 Models
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Article(models.Model):
    """文章模型"""
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
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新時間')

    def __str__(self):
        return self.title

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
