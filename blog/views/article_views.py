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
from django.utils import timezone
from ..models import Article, ArticleReadHistory, Comment, Like, Tag, Bookmark, ArticleShare
from ..forms import ArticleForm, CommentForm


def home(request):
    """
    文章列表頁
    顯示所有已發布的文章，按建立時間排序（最新在前）
    支援進階搜尋功能：
    - q: 搜尋關鍵字（標題或內容）
    - search_type: 搜尋類型（all/content/author）
    每頁顯示 6 篇文章
    """
    # 自動更新已到期的排程文章為已發布狀態
    scheduled_articles = Article.objects.filter(
        status='scheduled',
        publish_at__lte=timezone.now()
    )
    for article in scheduled_articles:
        article.status = 'published'
        article.save()

    # 取得搜尋參數
    search_query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'all')

    # 只顯示已發布的文章
    articles = Article.objects.filter(status='published').order_by("-created_at")

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

    # 自動更新排程文章狀態（如果已到發布時間）- 靜默更新，不顯示訊息
    if article.status == 'scheduled' and article.publish_at and article.publish_at <= timezone.now():
        article.status = 'published'
        article.save()
        # 重新載入文章以確保狀態已更新
        article.refresh_from_db()

    # 檢查文章是否可以被查看
    # 如果是草稿或未到排程時間，只有作者可以查看
    if not article.can_be_viewed and (not request.user.is_authenticated or article.author != request.user):
        messages.error(request, '❌ 此文章尚未發布！')
        return redirect('blog_home')

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

    # 書籤相關數據
    user_has_bookmarked = False
    bookmark_count = article.bookmarks.count()
    if request.user.is_authenticated:
        user_has_bookmarked = Bookmark.objects.filter(article=article, user=request.user).exists()

    # 分享統計
    share_count = article.shares.count()

    # 生成目錄
    table_of_contents = article.get_table_of_contents()

    context = {
        'article': article,
        'previous_article': previous_article,
        'next_article': next_article,
        'comment_form': comment_form,
        'comments': comments,
        'like_count': like_count,
        'user_has_liked': user_has_liked,
        'user_has_bookmarked': user_has_bookmarked,
        'bookmark_count': bookmark_count,
        'share_count': share_count,
        'table_of_contents': table_of_contents,
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

            # 檢查使用者點擊的按鈕 (action 參數)
            action = request.POST.get('action', 'publish')

            if action == 'draft':
                # 點擊「儲存為草稿」按鈕
                article.status = 'draft'
                article.publish_at = None
            else:
                # 點擊「發布」按鈕，使用下拉選單的狀態
                status = request.POST.get('status', 'published')
                article.status = status

                # 處理排程時間
                if status == 'scheduled':
                    publish_at = request.POST.get('publish_at')
                    if publish_at:
                        from django.utils.dateparse import parse_datetime
                        article.publish_at = parse_datetime(publish_at)

            article.save()
            form.save_m2m()  # 儲存 many-to-many 關係 (標籤)

            # 根據狀態顯示不同訊息
            if article.status == 'draft':
                messages.success(request, '✅ 文章已儲存為草稿！')
            elif article.status == 'scheduled':
                messages.success(request, f'✅ 文章已排程，將於 {article.publish_at.strftime("%Y年%m月%d日 %H:%M")} 發布！')
            else:
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
    已發布文章編輯時會儲存為草稿版本，不影響已發布內容
    """
    article = get_object_or_404(Article, id=id)

    # 檢查是否為作者本人
    if article.author != request.user:
        messages.error(request, '❌ 您沒有權限編輯此文章！')
        return redirect('article_detail', id=id)

    if request.method == 'POST':
        # 檢查使用者點擊的按鈕 (action 參數)
        action = request.POST.get('action', 'publish')

        # 如果是已發布文章且點擊「儲存為草稿」，使用草稿版本系統
        if article.status == 'published' and action == 'draft':
            import json
            title = request.POST.get('title', '')
            content = request.POST.get('content', '')
            tags_input = request.POST.get('tags_input', '')

            # 分割標籤（支援逗號和空格）
            tag_names = [name.strip() for name in tags_input.replace(',', ' ').split() if name.strip()]

            # 儲存草稿版本
            article.save_draft_version(title, content, tag_names)

            messages.success(request, '✅ 草稿已儲存！您可以在文章詳情頁發布或捨棄草稿。')
            return redirect('article_detail', id=article.id)

        # 正常編輯流程（包括已發布文章的直接更新）
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)

            if action == 'draft':
                # 點擊「儲存為草稿」按鈕
                article.status = 'draft'
                article.publish_at = None
            else:
                # 點擊「發布/更新」按鈕
                if article.status == 'published':
                    # 已發布文章保持發布狀態，清除草稿
                    article.has_draft = False
                    article.draft_title = None
                    article.draft_content = None
                    article.draft_tags_json = None
                    article.draft_updated_at = None
                else:
                    # 草稿或排程文章，使用下拉選單的狀態
                    status = request.POST.get('status', 'published')
                    article.status = status

                    # 處理排程時間
                    if status == 'scheduled':
                        publish_at = request.POST.get('publish_at')
                        if publish_at:
                            from django.utils.dateparse import parse_datetime
                            article.publish_at = parse_datetime(publish_at)
                    else:
                        article.publish_at = None

            article.save()
            form.save_m2m()  # 儲存 many-to-many 關係 (標籤)

            # 根據狀態顯示不同訊息
            if article.status == 'draft':
                messages.success(request, '✅ 文章已儲存為草稿！')
            elif article.status == 'scheduled':
                messages.success(request, f'✅ 文章已排程，將於 {article.publish_at.strftime("%Y年%m月%d日 %H:%M")} 發布！')
            else:
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
def article_autosave(request, id=None):
    """
    自動儲存文章為草稿 (AJAX)
    支援 Cmd/Ctrl + S 快捷鍵
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

    try:
        from django.utils.dateparse import parse_datetime
        import json

        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        tags_input = data.get('tags_input', '').strip()

        # 如果標題和內容都是空的，不保存
        if not title and not content:
            return JsonResponse({
                'success': False,
                'error': '標題和內容不能都為空'
            })

        # 如果是編輯現有文章
        if id:
            article = get_object_or_404(Article, id=id)
            # 檢查權限
            if article.author != request.user:
                return JsonResponse({
                    'success': False,
                    'error': '您沒有權限編輯此文章'
                }, status=403)

            # 如果是已發布文章，使用草稿版本系統
            if article.status == 'published':
                # 分割標籤（支援逗號和頓號）
                tag_names = [t.strip() for t in tags_input.replace('、', ',').split(',') if t.strip()]
                # 儲存草稿版本
                article.save_draft_version(title or '未命名文章', content, tag_names)
            else:
                # 草稿和排程文章直接更新
                article.title = title or '未命名文章'
                article.content = content
                article.save()

                # 處理標籤
                if tags_input:
                    from ..models import Tag
                    tag_names = [t.strip() for t in tags_input.replace('、', ',').split(',') if t.strip()]
                    tags = []
                    for tag_name in tag_names:
                        tag, created = Tag.objects.get_or_create(name=tag_name)
                        tags.append(tag)
                    article.tags.set(tags)
        else:
            # 創建新文章
            article = Article(
                title=title or '未命名文章',
                content=content,
                author=request.user,
                status='draft'
            )
            article.save()

            # 處理標籤
            if tags_input:
                from ..models import Tag
                tag_names = [t.strip() for t in tags_input.replace('、', ',').split(',') if t.strip()]
                tags = []
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    tags.append(tag)
                article.tags.set(tags)

        return JsonResponse({
            'success': True,
            'message': '草稿已自動儲存',
            'article_id': article.id,
            'saved_at': timezone.now().isoformat()
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': '無效的 JSON 格式'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def draft_publish(request, id):
    """
    發布草稿版本
    將草稿版本的內容覆蓋到已發布文章
    """
    article = get_object_or_404(Article, id=id)

    # 檢查是否為作者本人
    if article.author != request.user:
        messages.error(request, '❌ 您沒有權限發布此草稿！')
        return redirect('article_detail', id=id)

    # 檢查是否有草稿
    if not article.has_draft:
        messages.warning(request, '⚠️ 沒有未發布的草稿！')
        return redirect('article_detail', id=id)

    # 發布草稿版本
    if article.publish_draft_version():
        messages.success(request, '✅ 草稿已發布！文章內容已更新。')
    else:
        messages.error(request, '❌ 發布草稿失敗！')

    return redirect('article_detail', id=id)


@login_required
def draft_discard(request, id):
    """
    捨棄草稿版本
    刪除草稿版本，保留已發布內容不變
    """
    article = get_object_or_404(Article, id=id)

    # 檢查是否為作者本人
    if article.author != request.user:
        messages.error(request, '❌ 您沒有權限捨棄此草稿！')
        return redirect('article_detail', id=id)

    # 檢查是否有草稿
    if not article.has_draft:
        messages.warning(request, '⚠️ 沒有未發布的草稿！')
        return redirect('article_detail', id=id)

    # 捨棄草稿版本
    article.discard_draft_version()
    messages.success(request, '✅ 草稿已捨棄！')

    return redirect('article_detail', id=id)


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

    # 獲取來源頁面，預設為文章詳細頁
    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'✅ 已刪除文章「{title}」')
        # 刪除成功後返回我的文章頁面
        return redirect('my_articles')

    context = {
        'article': article,
        'next_url': next_url,  # 傳遞來源頁面給模板
    }
    return render(request, 'blog/articles/delete_confirm.html', context)


@login_required
def my_articles(request):
    """
    我的文章列表
    顯示當前登入使用者發表的所有文章（包括草稿、已發布、排程）
    支援按狀態篩選
    """
    # 自動更新已到期的排程文章為已發布狀態
    scheduled_articles = Article.objects.filter(
        author=request.user,
        status='scheduled',
        publish_at__lte=timezone.now()
    )
    for article in scheduled_articles:
        article.status = 'published'
        article.save()

    status_filter = request.GET.get('status', 'all')

    articles = Article.objects.filter(author=request.user)

    # 根據狀態篩選
    if status_filter == 'draft':
        articles = articles.filter(status='draft')
    elif status_filter == 'published':
        articles = articles.filter(status='published')
    elif status_filter == 'scheduled':
        articles = articles.filter(status='scheduled')

    articles = articles.order_by('-created_at')

    # 統計各狀態數量
    stats = {
        'total': Article.objects.filter(author=request.user).count(),
        'draft': Article.objects.filter(author=request.user, status='draft').count(),
        'published': Article.objects.filter(author=request.user, status='published').count(),
        'scheduled': Article.objects.filter(author=request.user, status='scheduled').count(),
    }

    context = {
        'articles': articles,
        'status_filter': status_filter,
        'stats': stats,
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

    # 使用 get_or_create 處理點讚邏輯
    # 這個方法在 SQLite 上更穩定
    try:
        like_obj, created = Like.objects.get_or_create(
            article=article,
            user=request.user
        )

        if not created:
            # 如果記錄已存在,刪除它(取消點讚)
            like_obj.delete()
            liked = False
            message = '已取消點讚'
        else:
            # 如果是新創建的,表示點讚成功
            liked = True
            message = '點讚成功'

        # 獲取最新的點讚數量
        like_count = article.likes.count()
    except Exception as e:
        # 如果發生錯誤(例如併發衝突),返回錯誤
        return JsonResponse({
            'success': False,
            'error': '操作失敗,請稍後再試'
        }, status=500)

    return JsonResponse({
        'success': True,
        'liked': liked,
        'like_count': like_count,
        'message': message
    })


def tags_list(request):
    """
    標籤列表頁（標籤雲）
    顯示所有標籤及其使用次數
    """
    tags = Tag.objects.all().order_by('name')

    # 計算每個標籤的文章數量並附加到標籤物件
    tags_with_count = []
    for tag in tags:
        tags_with_count.append({
            'tag': tag,
            'count': tag.articles.count()
        })

    # 按文章數量排序（從多到少）
    tags_with_count.sort(key=lambda x: x['count'], reverse=True)

    context = {
        'tags': tags_with_count,
        'total_tags': len(tags_with_count)
    }
    return render(request, 'blog/tags/list.html', context)


def tag_articles(request, slug):
    """
    顯示某個標籤的所有文章
    支援分頁
    """
    # 自動更新已到期的排程文章為已發布狀態
    scheduled_articles = Article.objects.filter(
        status='scheduled',
        publish_at__lte=timezone.now()
    )
    for article in scheduled_articles:
        article.status = 'published'
        article.save()

    tag = get_object_or_404(Tag, slug=slug)
    # 只顯示已發布的文章
    articles = tag.articles.filter(status='published').order_by('-created_at')

    # 分頁
    paginator = Paginator(articles, 10)  # 每頁 10 篇文章
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'articles': page_obj,
        'total_articles': articles.count()
    }
    return render(request, 'blog/tags/articles.html', context)


@login_required
def article_bookmark(request, id):
    """
    文章書籤/收藏功能
    - 用戶可以收藏文章
    - 再次點擊取消收藏
    - 返回 JSON 格式的響應
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

    article = get_object_or_404(Article, id=id)

    try:
        bookmark, created = Bookmark.objects.get_or_create(
            article=article,
            user=request.user
        )

        if not created:
            # 如果記錄已存在，刪除它（取消收藏）
            bookmark.delete()
            bookmarked = False
            message = '已取消收藏'
        else:
            # 如果是新創建的，表示收藏成功
            bookmarked = True
            message = '收藏成功'

        # 獲取最新的收藏數量
        bookmark_count = article.bookmarks.count()
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '操作失敗，請稍後再試'
        }, status=500)

    return JsonResponse({
        'success': True,
        'bookmarked': bookmarked,
        'bookmark_count': bookmark_count,
        'message': message
    })


@login_required
def my_bookmarks(request):
    """
    我的收藏列表
    顯示當前用戶收藏的所有文章
    """
    bookmarks = Bookmark.objects.filter(user=request.user).order_by('-created_at')

    # 分頁
    paginator = Paginator(bookmarks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bookmarks': page_obj,
        'total_bookmarks': bookmarks.count()
    }
    return render(request, 'blog/articles/my_bookmarks.html', context)


def article_share(request, id):
    """
    記錄文章分享
    - 支援記錄不同平台的分享
    - 可選擇性記錄用戶（訪客也可以分享）
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

    article = get_object_or_404(Article, id=id)
    platform = request.POST.get('platform', 'other')

    # 獲取用戶IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')

    try:
        # 創建分享記錄
        ArticleShare.objects.create(
            article=article,
            user=request.user if request.user.is_authenticated else None,
            platform=platform,
            ip_address=ip_address
        )

        # 獲取總分享數
        share_count = article.shares.count()

        return JsonResponse({
            'success': True,
            'share_count': share_count,
            'message': '感謝分享！'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': '記錄分享失敗'
        }, status=500)


@login_required
def my_drafts(request):
    """
    我的草稿頁面
    顯示當前用戶的所有草稿和排程文章
    """
    # 取得當前用戶的草稿和排程文章
    drafts = Article.objects.filter(
        author=request.user
    ).filter(
        Q(status='draft') | Q(status='scheduled')
    ).order_by('-updated_at')

    # 分頁
    paginator = Paginator(drafts, 10)
    page_number = request.GET.get('page', 1)
    drafts_page = paginator.get_page(page_number)

    # 統計
    draft_count = Article.objects.filter(author=request.user, status='draft').count()
    scheduled_count = Article.objects.filter(author=request.user, status='scheduled').count()

    context = {
        'drafts': drafts_page,
        'total_drafts': drafts.count(),
        'draft_count': draft_count,
        'scheduled_count': scheduled_count,
    }
    return render(request, 'blog/articles/my_drafts.html', context)
