"""
文章推薦系統
提供多種推薦策略：相關文章、標籤相似度、閱讀歷史個人化推薦
"""

from typing import List, Optional, Dict
from django.db.models import Count, Q, F, QuerySet, Case, When
from django.contrib.auth.models import User
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class ArticleRecommendationEngine:
    """文章推薦引擎"""

    def __init__(self, user: Optional[User] = None):
        """
        初始化推薦引擎

        Args:
            user: 用戶物件（用於個人化推薦）
        """
        self.user = user

    def get_recommendations(
        self,
        article=None,
        limit: int = 10,
        strategy: str = 'hybrid'
    ) -> QuerySet:
        """
        獲取推薦文章

        Args:
            article: 當前文章（用於相關文章推薦）
            limit: 推薦數量
            strategy: 推薦策略
                - 'tag_based': 基於標籤相似度
                - 'reading_history': 基於閱讀歷史
                - 'hybrid': 混合策略（預設）
                - 'popular': 熱門文章
                - 'collaborative': 協同過濾

        Returns:
            QuerySet: 推薦文章列表
        """
        from ..models import Article

        if strategy == 'tag_based' and article:
            return self._tag_based_recommendations(article, limit)
        elif strategy == 'reading_history' and self.user:
            return self._reading_history_recommendations(limit)
        elif strategy == 'popular':
            return self._popular_recommendations(limit)
        elif strategy == 'collaborative' and self.user:
            return self._collaborative_filtering_recommendations(limit)
        elif strategy == 'hybrid':
            return self._hybrid_recommendations(article, limit)
        else:
            # 預設返回最新文章
            return Article.objects.filter(
                status='published'
            ).order_by('-created_at')[:limit]

    def _tag_based_recommendations(self, article, limit: int) -> QuerySet:
        """
        基於標籤的相似文章推薦

        算法：
        1. 獲取當前文章的所有標籤
        2. 找出包含相同標籤的其他文章
        3. 按共同標籤數量排序
        4. 排除當前文章
        """
        from ..models import Article

        # 獲取當前文章的標籤
        article_tags = article.tags.all()

        if not article_tags.exists():
            # 如果文章沒有標籤，返回同作者的其他文章
            return Article.objects.filter(
                author=article.author,
                status='published'
            ).exclude(id=article.id).order_by('-created_at')[:limit]

        # 找出包含相同標籤的文章，按共同標籤數排序
        recommended_articles = Article.objects.filter(
            tags__in=article_tags,
            status='published'
        ).exclude(
            id=article.id
        ).annotate(
            common_tags=Count('tags'),
            like_count=Count('likes', distinct=True)
        ).order_by('-common_tags', '-like_count', '-created_at').distinct()

        return recommended_articles[:limit]

    def _reading_history_recommendations(self, limit: int) -> QuerySet:
        """
        基於閱讀歷史的個人化推薦

        算法：
        1. 分析用戶最近閱讀的文章
        2. 提取用戶興趣標籤（按閱讀頻率）
        3. 推薦包含興趣標籤的文章
        4. 排除已閱讀的文章
        """
        from ..models import Article, ArticleReadHistory

        # 獲取用戶最近閱讀的文章（最近30篇）
        recent_reads = ArticleReadHistory.objects.filter(
            user=self.user
        ).select_related('article').order_by('-last_read_at')[:30]

        if not recent_reads.exists():
            # 如果沒有閱讀歷史，返回熱門文章
            return self._popular_recommendations(limit)

        # 收集用戶閱讀過的文章 ID
        read_article_ids = [history.article_id for history in recent_reads]

        # 提取用戶興趣標籤（從閱讀歷史中）
        interest_tags = []
        for history in recent_reads:
            interest_tags.extend(history.article.tags.values_list('id', flat=True))

        if not interest_tags:
            return self._popular_recommendations(limit)

        # 統計標籤出現頻率
        tag_counter = Counter(interest_tags)
        top_tags = [tag_id for tag_id, count in tag_counter.most_common(10)]

        # 推薦包含興趣標籤的文章
        recommended_articles = Article.objects.filter(
            tags__id__in=top_tags,
            status='published'
        ).exclude(
            id__in=read_article_ids
        ).annotate(
            tag_match_count=Count('tags'),
            like_count=Count('likes', distinct=True)
        ).order_by('-tag_match_count', '-like_count', '-created_at').distinct()

        return recommended_articles[:limit]

    def _popular_recommendations(self, limit: int) -> QuerySet:
        """
        熱門文章推薦

        算法：
        1. 綜合考慮瀏覽量、點讚數、評論數
        2. 計算文章熱度分數
        3. 優先推薦近期發表的文章
        """
        from ..models import Article
        from django.utils import timezone
        from datetime import timedelta

        # 最近30天的文章
        recent_date = timezone.now() - timedelta(days=30)

        articles = Article.objects.filter(
            status='published',
            created_at__gte=recent_date
        ).annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
            read_count=Count('read_records', distinct=True)
        ).order_by(
            '-read_count',
            '-like_count',
            '-comment_count',
            '-created_at'
        )

        return articles[:limit]

    def _collaborative_filtering_recommendations(self, limit: int) -> QuerySet:
        """
        協同過濾推薦（基於用戶相似度）

        算法：
        1. 找出與當前用戶有相似閱讀習慣的用戶
        2. 推薦這些用戶喜歡但當前用戶未讀的文章
        """
        from ..models import Article, ArticleReadHistory, Like

        # 獲取當前用戶閱讀過的文章
        user_read_articles = ArticleReadHistory.objects.filter(
            user=self.user
        ).values_list('article_id', flat=True)

        if not user_read_articles:
            return self._popular_recommendations(limit)

        # 找出也閱讀過這些文章的其他用戶
        similar_users = ArticleReadHistory.objects.filter(
            article_id__in=user_read_articles
        ).exclude(
            user=self.user
        ).values('user').annotate(
            common_reads=Count('article')
        ).order_by('-common_reads')[:10]

        similar_user_ids = [u['user'] for u in similar_users]

        # 找出這些用戶喜歡的文章
        recommended_articles = Article.objects.filter(
            like__user_id__in=similar_user_ids,
            status='published'
        ).exclude(
            id__in=user_read_articles
        ).annotate(
            like_count=Count('likes', distinct=True),
            read_count=Count('read_records', distinct=True)
        ).order_by('-like_count', '-read_count', '-created_at').distinct()

        return recommended_articles[:limit]

    def _hybrid_recommendations(self, article, limit: int) -> QuerySet:
        """
        混合推薦策略

        綜合多種推薦方法：
        1. 如果有當前文章，優先推薦相關文章
        2. 如果用戶已登入，混合閱讀歷史推薦
        3. 補充熱門文章
        """
        from ..models import Article

        recommendations = []
        remaining = limit

        # 1. 基於標籤的推薦（50%）
        if article:
            tag_based = list(self._tag_based_recommendations(
                article,
                limit=int(limit * 0.5)
            ))
            recommendations.extend(tag_based)
            remaining -= len(tag_based)

        # 2. 基於閱讀歷史的推薦（30%）
        if self.user and remaining > 0:
            history_based = list(self._reading_history_recommendations(
                limit=max(int(limit * 0.3), remaining // 2)
            ))
            # 排除已推薦的
            history_based = [
                a for a in history_based
                if a not in recommendations
            ]
            recommendations.extend(history_based[:remaining // 2])
            remaining = limit - len(recommendations)

        # 3. 熱門文章補充
        if remaining > 0:
            popular = list(self._popular_recommendations(limit=remaining * 2))
            # 排除已推薦的
            popular = [
                a for a in popular
                if a not in recommendations
            ]
            recommendations.extend(popular[:remaining])

        # 轉換為 QuerySet
        article_ids = [a.id for a in recommendations[:limit]]

        if not article_ids:
            return Article.objects.none()

        # 保持推薦順序
        preserved_order = Case(
            *[When(id=id, then=pos) for pos, id in enumerate(article_ids)]
        )

        return Article.objects.filter(
            id__in=article_ids
        ).order_by(preserved_order)

    def get_similar_articles(self, article, limit: int = 6) -> QuerySet:
        """
        獲取相似文章（用於文章詳情頁）

        Args:
            article: 當前文章
            limit: 推薦數量

        Returns:
            QuerySet: 相似文章列表
        """
        return self._tag_based_recommendations(article, limit)

    def get_personalized_feed(self, limit: int = 20) -> QuerySet:
        """
        獲取個人化推薦流

        Args:
            limit: 推薦數量

        Returns:
            QuerySet: 個人化推薦文章
        """
        if self.user:
            return self._hybrid_recommendations(None, limit)
        else:
            return self._popular_recommendations(limit)


# 便捷函數

def get_recommended_articles(
    article=None,
    user: Optional[User] = None,
    limit: int = 10,
    strategy: str = 'hybrid'
) -> QuerySet:
    """
    獲取推薦文章（便捷函數）

    Args:
        article: 當前文章
        user: 用戶物件
        limit: 推薦數量
        strategy: 推薦策略

    Returns:
        QuerySet: 推薦文章列表
    """
    engine = ArticleRecommendationEngine(user=user)
    return engine.get_recommendations(
        article=article,
        limit=limit,
        strategy=strategy
    )


def get_similar_articles(article, limit: int = 6) -> QuerySet:
    """
    獲取相似文章（便捷函數）

    Args:
        article: 當前文章
        limit: 推薦數量

    Returns:
        QuerySet: 相似文章列表
    """
    engine = ArticleRecommendationEngine()
    return engine.get_similar_articles(article, limit)


def get_personalized_feed(user: User, limit: int = 20) -> QuerySet:
    """
    獲取個人化推薦流（便捷函數）

    Args:
        user: 用戶物件
        limit: 推薦數量

    Returns:
        QuerySet: 個人化推薦文章
    """
    engine = ArticleRecommendationEngine(user=user)
    return engine.get_personalized_feed(limit)
