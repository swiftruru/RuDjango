"""
Sitemap 配置
用於搜尋引擎爬蟲索引網站內容
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Tag
from django.contrib.auth.models import User


class ArticleSitemap(Sitemap):
    """文章 Sitemap"""
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        """返回所有已發布的文章"""
        return Article.objects.filter(status='published').order_by('-updated_at')

    def lastmod(self, obj):
        """返回文章最後修改時間"""
        return obj.updated_at

    def location(self, obj):
        """返回文章的 URL"""
        return reverse('article_detail', args=[obj.id])


class TagSitemap(Sitemap):
    """標籤 Sitemap"""
    changefreq = "daily"
    priority = 0.6

    def items(self):
        """返回所有標籤"""
        return Tag.objects.all().order_by('name')

    def location(self, obj):
        """返回標籤的 URL"""
        return reverse('tag_articles', args=[obj.slug])


class UserProfileSitemap(Sitemap):
    """使用者個人頁面 Sitemap"""
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        """返回所有有發布文章的使用者"""
        return User.objects.filter(
            articles__status='published'
        ).distinct().order_by('username')

    def location(self, obj):
        """返回使用者個人頁面的 URL"""
        return reverse('member_profile', args=[obj.username])


class StaticViewSitemap(Sitemap):
    """靜態頁面 Sitemap"""
    priority = 0.8
    changefreq = 'monthly'

    def items(self):
        """返回靜態頁面的 URL 名稱"""
        return [
            'blog_home',
            'tags_list',
        ]

    def location(self, item):
        """返回靜態頁面的 URL"""
        return reverse(item)
