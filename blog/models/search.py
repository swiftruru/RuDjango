from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SearchHistory(models.Model):
    """搜尋歷史記錄"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_history',
        verbose_name='使用者'
    )
    query = models.CharField(max_length=200, verbose_name='搜尋關鍵字')
    search_type = models.CharField(
        max_length=20,
        choices=[
            ('article', '文章'),
            ('tag', '標籤'),
            ('author', '作者'),
            ('all', '全部'),
        ],
        default='article',
        verbose_name='搜尋類型'
    )
    results_count = models.IntegerField(default=0, verbose_name='結果數量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='搜尋時間')

    class Meta:
        db_table = 'blog_search_history'
        ordering = ['-created_at']
        verbose_name = '搜尋歷史'
        verbose_name_plural = '搜尋歷史'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.query}"

    @classmethod
    def add_search(cls, user, query, search_type='article', results_count=0):
        """新增搜尋記錄（避免短時間內重複記錄）"""
        if not user.is_authenticated or not query.strip():
            return None

        # 檢查是否在5分鐘內有相同的搜尋記錄
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        recent_search = cls.objects.filter(
            user=user,
            query=query.strip(),
            search_type=search_type,
            created_at__gte=five_minutes_ago
        ).first()

        if recent_search:
            # 更新結果數量和時間
            recent_search.results_count = results_count
            recent_search.created_at = timezone.now()
            recent_search.save()
            return recent_search
        else:
            # 建立新記錄
            return cls.objects.create(
                user=user,
                query=query.strip(),
                search_type=search_type,
                results_count=results_count
            )

    @classmethod
    def get_recent_searches(cls, user, limit=10):
        """獲取使用者最近的搜尋記錄（去重）"""
        if not user.is_authenticated:
            return []

        # 獲取最近的搜尋記錄，手動去重
        all_searches = cls.objects.filter(user=user).order_by('-created_at')
        seen_queries = set()
        unique_searches = []

        for search in all_searches:
            if search.query not in seen_queries:
                seen_queries.add(search.query)
                unique_searches.append({
                    'query': search.query,
                    'search_type': search.search_type
                })
                if len(unique_searches) >= limit:
                    break

        return unique_searches

    @classmethod
    def get_popular_searches(cls, limit=10):
        """獲取熱門搜尋關鍵字"""
        from django.db.models import Count

        # 計算最近7天的熱門搜尋
        seven_days_ago = timezone.now() - timezone.timedelta(days=7)
        popular = cls.objects.filter(
            created_at__gte=seven_days_ago
        ).values('query').annotate(
            search_count=Count('id')
        ).order_by('-search_count')[:limit]

        return popular

    @classmethod
    def clear_user_history(cls, user):
        """清除使用者的搜尋歷史"""
        if user.is_authenticated:
            return cls.objects.filter(user=user).delete()
        return 0, {}
