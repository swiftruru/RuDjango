"""
文章相關的視圖函數
處理文章的列表、詳細頁、新增、編輯、刪除等功能
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from ..models import Article, ArticleReadHistory, Comment, Like
from ..forms import ArticleForm, CommentForm


def home(request):
    """
    文章列表頁
    顯示所有文章，按建立時間排序（最新在前）
    支援進階搜尋功能：
    - q: 搜尋關鍵字（標題或內容）
    - search_type: 搜尋類型（all/content/author）
    每頁顯示 6 篇文章
    """
    # 取得搜尋參數
    search_query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'all')
    
    articles = Article.objects.all().order_by("-created_at")

    if search_query:
        if search_type == 'author':
            # 搜尋作者（username 或 first_name）
            articles = articles.filter(
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query)
            ).distinct()
        elif search_type == 'content':
            # 只搜尋標題和內容
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            ).distinct()
        else:
            # 搜尋全部（標題、內容、作者）
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query)
            ).distinct()
    
    # 分頁功能：每頁顯示 6 篇文章
    paginator = Paginator(articles, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,  # 改為分頁物件
        'page_obj': page_obj,
        'search_query': search_query,  # 傳遞搜尋關鍵字到模板
        'search_type': search_type,  # 傳遞搜尋類型到模板
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
    包含上一篇和下一篇文章的導航
    並記錄已登入用戶的閱讀歷史
    處理留言功能
    """
    # 取得指定 id 的文章，若不存在則返回 404
    article = get_object_or_404(Article, id=id)

    # 處理留言提交
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.article = article
            comment.author = request.user
            # 處理回覆留言
            parent_id = request.POST.get('parent_id')
            if parent_id:
                comment.parent = Comment.objects.get(id=parent_id)
            comment.save()
            messages.success(request, '✅ 留言發表成功！')
            return redirect('article_detail', id=id)
    else:
        comment_form = CommentForm()

    # 如果用戶已登入，記錄閱讀歷史
    if request.user.is_authenticated:
        # 檢查是否已存在閱讀記錄
        try:
            read_history = ArticleReadHistory.objects.get(
                user=request.user,
                article=article
            )
            # 已存在，增加閱讀次數
            read_history.read_count = F('read_count') + 1
            read_history.save()
            read_history.refresh_from_db()
        except ArticleReadHistory.DoesNotExist:
            # 不存在，創建新記錄
            read_history = ArticleReadHistory.objects.create(
                user=request.user,
                article=article,
                read_count=1
            )

    # 取得上一篇文章（id 更小的最大值）
    previous_article = Article.objects.filter(id__lt=id).order_by('-id').first()

    # 取得下一篇文章（id 更大的最小值）
    next_article = Article.objects.filter(id__gt=id).order_by('id').first()

    # 取得所有主留言（沒有父留言的留言）
    comments = article.comments.filter(parent=None).order_by('-created_at')

    # 點讚相關數據
    like_count = article.likes.count()
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = Like.objects.filter(article=article, user=request.user).exists()

    context = {
        'article': article,
        'previous_article': previous_article,
        'next_article': next_article,
        'comment_form': comment_form,
        'comments': comments,
        'like_count': like_count,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'blog/articles/detail.html', context)


@login_required
def article_create(request):
    """
    新增文章
    需要登入才能使用
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, '✅ 文章發表成功！')
            return redirect('article_detail', id=article.id)
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'action': '發表文章',
    }
    return render(request, 'blog/articles/form.html', context)


@login_required
def article_edit(request, id):
    """
    編輯文章
    只有作者本人才能編輯
    """
    article = get_object_or_404(Article, id=id)
    
    # 檢查是否為作者本人
    if article.author != request.user:
        messages.error(request, '❌ 您沒有權限編輯此文章！')
        return redirect('article_detail', id=id)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ 文章更新成功！')
            return redirect('article_detail', id=article.id)
    else:
        form = ArticleForm(instance=article)
    
    context = {
        'form': form,
        'article': article,
        'action': '編輯文章',
    }
    return render(request, 'blog/articles/form.html', context)


@login_required
def article_delete(request, id):
    """
    刪除文章
    只有作者本人才能刪除
    """
    article = get_object_or_404(Article, id=id)
    
    # 檢查是否為作者本人
    if article.author != request.user:
        messages.error(request, '❌ 您沒有權限刪除此文章！')
        return redirect('article_detail', id=id)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'✅ 已刪除文章「{title}」')
        return redirect('my_articles')
    
    context = {
        'article': article,
    }
    return render(request, 'blog/articles/delete_confirm.html', context)


@login_required
def my_articles(request):
    """
    我的文章列表
    顯示當前登入使用者發表的所有文章
    """
    articles = Article.objects.filter(author=request.user).order_by('-created_at')

    context = {
        'articles': articles,
    }
    return render(request, 'blog/articles/my_articles.html', context)


@login_required
def comment_delete(request, comment_id):
    """
    刪除留言
    只有留言作者本人才能刪除
    """
    comment = get_object_or_404(Comment, id=comment_id)

    # 檢查是否為留言作者本人
    if comment.author != request.user:
        messages.error(request, '❌ 您沒有權限刪除此留言！')
        return redirect(request.GET.get('next', 'blog_home'))

    # 取得文章 ID 以便刪除後返回
    article_id = comment.article.id
    comment.delete()
    messages.success(request, '✅ 留言已刪除')

    # 返回到來源頁面或文章詳細頁
    next_url = request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('article_detail', id=article_id)


@login_required
def article_like(request, id):
    """
    文章點讚功能
    - 使用者可以對其他會員的文章點讚
    - 不能對自己的文章點讚
    - 再次點擊取消點讚
    - 返回 JSON 格式的響應
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

    article = get_object_or_404(Article, id=id)

    # 檢查是否為自己的文章
    if article.author == request.user:
        return JsonResponse({
            'success': False,
            'error': '不能對自己的文章點讚'
        }, status=403)

    # 檢查是否已經點讚
    like_exists = Like.objects.filter(article=article, user=request.user).first()

    if like_exists:
        # 取消點讚
        like_exists.delete()
        liked = False
        message = '已取消點讚'
    else:
        # 新增點讚
        Like.objects.create(article=article, user=request.user)
        liked = True
        message = '點讚成功'

    # 獲取最新的點讚數量
    like_count = article.likes.count()

    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })
