"""
RSS/Atom Feed 配置
提供文章訂閱功能
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Atom1Feed
from .models import Article
from .utils.seo import generate_meta_description


class LatestArticlesFeed(Feed):
    """最新文章 RSS Feed"""
    title = "RuDjango - 最新文章"
    link = "/blog/"
    description = "RuDjango 部落格最新文章更新"

    def items(self):
        """返回最新的 10 篇已發布文章"""
        return Article.objects.filter(status='published').order_by('-created_at')[:10]

    def item_title(self, item):
        """文章標題"""
        return item.title

    def item_description(self, item):
        """文章描述"""
        return generate_meta_description(item.content, max_length=200)

    def item_link(self, item):
        """文章連結"""
        return reverse('article_detail', args=[item.id])

    def item_pubdate(self, item):
        """發布日期"""
        return item.created_at

    def item_updateddate(self, item):
        """更新日期"""
        return item.updated_at

    def item_author_name(self, item):
        """作者名稱"""
        return item.author.first_name or item.author.username

    def item_categories(self, item):
        """文章分類（標籤）"""
        return [tag.name for tag in item.tags.all()]


class LatestArticlesAtomFeed(LatestArticlesFeed):
    """最新文章 Atom Feed"""
    feed_type = Atom1Feed
    subtitle = LatestArticlesFeed.description


class ArticlesByAuthorFeed(Feed):
    """特定作者的文章 RSS Feed"""

    def get_object(self, request, username):
        """獲取作者"""
        from django.contrib.auth.models import User
        return User.objects.get(username=username)

    def title(self, obj):
        """Feed 標題"""
        display_name = obj.first_name or obj.username
        return f"RuDjango - {display_name} 的文章"

    def link(self, obj):
        """Feed 連結"""
        return reverse('user_profile', args=[obj.username])

    def description(self, obj):
        """Feed 描述"""
        display_name = obj.first_name or obj.username
        return f"{display_name} 在 RuDjango 發表的文章"

    def items(self, obj):
        """返回作者的最新 10 篇已發布文章"""
        return Article.objects.filter(
            author=obj,
            status='published'
        ).order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return generate_meta_description(item.content, max_length=200)

    def item_link(self, item):
        return reverse('article_detail', args=[item.id])

    def item_pubdate(self, item):
        return item.created_at

    def item_categories(self, item):
        return [tag.name for tag in item.tags.all()]


class ArticlesByTagFeed(Feed):
    """特定標籤的文章 RSS Feed"""

    def get_object(self, request, tag_id):
        """獲取標籤"""
        from .models import Tag
        return Tag.objects.get(id=tag_id)

    def title(self, obj):
        """Feed 標題"""
        return f"RuDjango - 標籤「{obj.name}」的文章"

    def link(self, obj):
        """Feed 連結"""
        return reverse('articles_by_tag', args=[obj.id])

    def description(self, obj):
        """Feed 描述"""
        return f"標籤「{obj.name}」的最新文章"

    def items(self, obj):
        """返回標籤下的最新 10 篇已發布文章"""
        return obj.articles.filter(status='published').order_by('-created_at')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return generate_meta_description(item.content, max_length=200)

    def item_link(self, item):
        return reverse('article_detail', args=[item.id])

    def item_pubdate(self, item):
        return item.created_at

    def item_author_name(self, item):
        return item.author.first_name or item.author.username
