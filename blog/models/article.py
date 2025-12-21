"""
文章相關的 Models
"""
from django.db import models
from django.contrib.auth.models import User


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
