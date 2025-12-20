"""
文章相關的視圖函數
處理文章的列表、詳細頁、新增、編輯、刪除等功能
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from ..models import Article


def home(request):
    """
    文章列表頁
    顯示所有文章，按建立時間排序（最新在前）
    支援搜尋功能，可透過 ?q=關鍵字 搜尋文章標題或內容
    """
    # 取得搜尋關鍵字
    search_query = request.GET.get('q', '')
    
    articles = Article.objects.all().order_by("-created_at")

    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        ).distinct()
    
    context = {
        'articles': articles,
        'search_query': search_query,  # 傳遞搜尋關鍵字到模板
    }
    return render(request, 'blog/articles/list.html', context)


def about(request):
    """
    關於頁面
    顯示部落格的相關資訊
    """
    return render(request, 'blog/pages/about.html')


def article_detail(request, id):
    """
    文章詳細頁
    顯示單篇文章的完整內容
    """
    # 取得指定 id 的文章，若不存在則返回 404
    article = get_object_or_404(Article, id=id)
    context = {
        'article': article,
    }
    return render(request, 'blog/articles/detail.html', context)


# 未來可以在這裡新增：
# def article_create(request):
#     """新增文章"""
#     pass
#
# def article_edit(request, id):
#     """編輯文章"""
#     pass
#
# def article_delete(request, id):
#     """刪除文章"""
#     pass
