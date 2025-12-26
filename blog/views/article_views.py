"""
文章相關的視圖函數
處理文章的列表、詳細頁、新增、編輯、刪除等功能
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, F, Count
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import Article, ArticleReadHistory, Comment, Like, Tag, Bookmark, ArticleShare
from ..forms import ArticleForm, CommentForm
from ..utils.notifications import notify_comment, notify_like, notify_share, notify_mention
from ..utils.mention_parser import parse_mentions
from ..utils.seo import generate_meta_description, generate_keywords, extract_first_image_from_markdown
from ..utils.recommendations import get_recommended_articles, get_similar_articles, get_personalized_feed
from django.contrib.auth.models import User


def home(request):
    """
    文章列表頁
    顯示所有已發布的文章，按建立時間排序（最新在前）
    支援進階搜尋功能：
    - q: 搜尋關鍵字（標題或內容）
    - search_type: 搜尋類型（all/content/author）
    每頁顯示 6 篇文章
    支援 AJAX 請求返回 JSON 格式數據（用於無限滾動）
    """
    # 自動更新已到期的排程文章為已發布狀態
    # 使用 update() 批次更新，避免逐筆 save() 造成效能問題
    Article.objects.filter(
        status='scheduled',
        publish_at__lte=timezone.now()
    ).update(status='published')

    # 取得搜尋參數
    search_query = request.GET.get('q', '')
    search_type = request.GET.get('search_type', 'all')

    # 只顯示已發布的文章
    # 使用 select_related 優化作者查詢，prefetch_related 優化標籤查詢
    articles = Article.objects.filter(status='published').select_related('author').prefetch_related('tags').order_by("-created_at")

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

    # 如果是 AJAX 請求，返回 JSON 格式數據
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.template.loader import render_to_string

        # 渲染文章卡片 HTML
        articles_html = render_to_string(
            'blog/articles/_article_cards.html',
            {
                'articles': page_obj,
                'search_query': search_query,
                'request': request,
            }
        )

        return JsonResponse({
            'success': True,
            'html': articles_html,
            'has_next': page_obj.has_next(),
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
        })

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

            # 發送通知給文章作者
            notify_comment(article, comment)

            # 處理 @mention 通知
            mentioned_usernames = parse_mentions(comment.content)
            for username in mentioned_usernames:
                try:
                    mentioned_user = User.objects.get(username=username)
                    notify_mention(
                        mentioned_user=mentioned_user,
                        mentioning_user=request.user,
                        content_type='comment',
                        content_object=comment,
                        article=article
                    )
                except User.DoesNotExist:
                    continue

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

    # SEO 相關數據
    meta_description = generate_meta_description(article.content)
    meta_keywords = generate_keywords(article)

    # 提取 Open Graph 圖片
    og_image_url = extract_first_image_from_markdown(article.content)
    if og_image_url and not og_image_url.startswith('http'):
        # 如果是相對路徑，轉換為絕對路徑
        og_image_url = request.build_absolute_uri(og_image_url)

    # 獲取相似文章推薦（基於標籤）
    similar_articles = get_similar_articles(article, limit=6)

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
        'similar_articles': similar_articles,
        # SEO
        'meta_description': meta_description,
        'meta_keywords': meta_keywords,
        'og_image_url': og_image_url,
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

            # 處理 @mention 通知
            if article.status == 'published':  # 只有已發布的文章才發送通知
                # 從文章標題和內容中解析 @mention
                all_text = f"{article.title} {article.content}"
                mentioned_usernames = parse_mentions(all_text)

                # 為每個被提及的使用者發送通知
                for username in mentioned_usernames:
                    try:
                        mentioned_user = User.objects.get(username=username)
                        notify_mention(
                            mentioned_user=mentioned_user,
                            mentioning_user=request.user,
                            content_type='article',
                            content_object=article,
                            article=article
                        )
                    except User.DoesNotExist:
                        continue

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

            # 處理 @mention 通知（僅已發布文章）
            if article.status == 'published':
                all_text = f"{article.title} {article.content}"
                mentioned_usernames = parse_mentions(all_text)
                for username in mentioned_usernames:
                    try:
                        mentioned_user = User.objects.get(username=username)
                        notify_mention(
                            mentioned_user=mentioned_user,
                            mentioning_user=request.user,
                            content_type='article',
                            content_object=article,
                            article=article
                        )
                    except User.DoesNotExist:
                        continue

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

            # 發送通知給文章作者
            notify_like(article, request.user)

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
    # 使用 update() 批次更新，避免逐筆 save() 造成效能問題
    Article.objects.filter(
        status='scheduled',
        publish_at__lte=timezone.now()
    ).update(status='published')

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

        # 發送通知給文章作者（僅限已登入用戶）
        if request.user.is_authenticated:
            notify_share(article, request.user)

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

def advanced_search(request):
    """
    進階搜尋頁面
    支援多條件篩選：
    - q: 關鍵字搜尋
    - tags: 標籤篩選（支援多個標籤）
    - author: 作者篩選
    - date_from: 開始日期
    - date_to: 結束日期
    - sort: 排序方式（latest/oldest/popular）
    """
    # 取得所有搜尋參數
    search_query = request.GET.get('q', '').strip()
    selected_tags = request.GET.getlist('tags')  # 支援多個標籤
    author_filter = request.GET.get('author', '').strip()
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort', 'latest')

    # 基礎查詢：只顯示已發布的文章
    articles = Article.objects.filter(status='published')

    # 關鍵字搜尋
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(author__first_name__icontains=search_query)
        )

    # 標籤篩選（支援多個標籤 - OR 關係）
    if selected_tags:
        articles = articles.filter(tags__slug__in=selected_tags).distinct()

    # 作者篩選
    if author_filter:
        articles = articles.filter(
            Q(author__username__icontains=author_filter) |
            Q(author__first_name__icontains=author_filter)
        )

    # 日期範圍篩選
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            articles = articles.filter(created_at__gte=from_date)
        except ValueError:
            pass

    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # 包含當天的所有時間
            to_date = to_date.replace(hour=23, minute=59, second=59)
            articles = articles.filter(created_at__lte=to_date)
        except ValueError:
            pass

    # 排序
    if sort_by == 'oldest':
        articles = articles.order_by('created_at')
    elif sort_by == 'popular':
        # 按點讚數排序
        articles = articles.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')
    else:  # latest (預設)
        articles = articles.order_by('-created_at')

    # 分頁
    paginator = Paginator(articles, 12)  # 進階搜尋每頁顯示更多
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 記錄搜尋歷史（只在有搜尋關鍵字時）
    if search_query and request.user.is_authenticated:
        from ..models import SearchHistory
        SearchHistory.add_search(
            user=request.user,
            query=search_query,
            search_type='article',
            results_count=paginator.count
        )

    # 取得所有可用標籤
    all_tags = Tag.objects.all().order_by('name')

    # 取得所有作者（有發布文章的）
    authors = Article.objects.filter(status='published')\
        .values('author__username', 'author__first_name')\
        .annotate(article_count=Count('id'))\
        .order_by('-article_count')[:20]  # 只顯示前20個活躍作者

    context = {
        'articles': page_obj,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_tags': selected_tags,
        'author_filter': author_filter,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'all_tags': all_tags,
        'authors': authors,
        'total_results': paginator.count,
    }
    return render(request, 'blog/search/advanced.html', context)


def search_suggestions(request):
    """
    搜尋建議 API
    提供自動完成建議：
    - 搜尋歷史（如果沒有輸入或輸入很短）
    - 熱門搜尋
    - 文章標題
    - 標籤
    - 作者
    返回 JSON 格式
    """
    from ..models import SearchHistory

    query = request.GET.get('q', '').strip()
    suggestions = []

    # 如果沒有輸入或輸入很短，顯示搜尋歷史和熱門搜尋
    if not query or len(query) < 2:
        # 顯示使用者的搜尋歷史（最多 5 個）
        if request.user.is_authenticated:
            recent_searches = SearchHistory.get_recent_searches(request.user, limit=5)
            for search in recent_searches:
                suggestions.append({
                    'type': 'history',
                    'text': search['query'],
                    'url': f"/blog/search/?q={search['query']}",
                    'icon': '🕐'
                })

        # 顯示熱門搜尋（最多 5 個）
        popular_searches = SearchHistory.get_popular_searches(limit=5)
        for search in popular_searches:
            suggestions.append({
                'type': 'popular',
                'text': search['query'],
                'url': f"/blog/search/?q={search['query']}",
                'icon': '🔥',
                'count': search['search_count']
            })

        return JsonResponse({
            'success': True,
            'suggestions': suggestions,
            'query': query,
            'show_history': True
        })

    # 如果有輸入，顯示相關建議
    # 搜尋文章標題（最多 5 個）
    articles = Article.objects.filter(
        status='published',
        title__icontains=query
    ).values('id', 'title')[:5]

    for article in articles:
        suggestions.append({
            'type': 'article',
            'text': article['title'],
            'url': f"/blog/article/{article['id']}/",
            'icon': '📄'
        })

    # 搜尋標籤（最多 3 個）
    tags = Tag.objects.filter(
        name__icontains=query
    ).values('slug', 'name')[:3]

    for tag in tags:
        suggestions.append({
            'type': 'tag',
            'text': tag['name'],
            'url': f"/blog/tag/{tag['slug']}/",
            'icon': '🏷️'
        })

    # 搜尋作者（最多 3 個）
    from django.contrib.auth import get_user_model
    User = get_user_model()

    authors = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query)
    ).exclude(
        articles__isnull=True
    ).distinct()[:3]

    for author in authors:
        display_name = author.first_name if author.first_name else author.username
        suggestions.append({
            'type': 'author',
            'text': display_name,
            'url': f"/blog/member/{author.username}/",
            'icon': '👤'
        })

    return JsonResponse({
        'success': True,
        'suggestions': suggestions,
        'query': query,
        'show_history': False
    })


def quick_search(request):
    """
    快速搜尋 API
    用於即時搜尋，返回簡化的結果
    """
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse({'results': [], 'count': 0})

    # 搜尋文章
    articles = Article.objects.filter(
        status='published'
    ).filter(
        Q(title__icontains=query) |
        Q(content__icontains=query)
    ).select_related('author').prefetch_related('tags')[:10]

    results = []
    for article in articles:
        results.append({
            'id': article.id,
            'title': article.title,
            'excerpt': article.content[:100] + '...' if len(article.content) > 100 else article.content,
            'author': article.author.first_name if article.author.first_name else article.author.username,
            'created_at': article.created_at.strftime('%Y-%m-%d'),
            'url': f"/blog/article/{article.id}/",
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in article.tags.all()[:3]]
        })

    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results),
        'query': query
    })


def get_similar_articles_api(request, id):
    """
    獲取相似文章 API
    基於標籤相似度推薦相關文章
    """
    article = get_object_or_404(Article, id=id)

    # 獲取相似文章（預設 6 篇）
    limit = int(request.GET.get('limit', 6))
    similar_articles = get_similar_articles(article, limit=limit)

    # 序列化文章數據
    results = []
    for similar_article in similar_articles:
        results.append({
            'id': similar_article.id,
            'title': similar_article.title,
            'excerpt': similar_article.content[:150] + '...' if len(similar_article.content) > 150 else similar_article.content,
            'author': {
                'username': similar_article.author.username,
                'display_name': similar_article.author.first_name if similar_article.author.first_name else similar_article.author.username,
            },
            'created_at': similar_article.created_at.strftime('%Y-%m-%d'),
            'like_count': similar_article.likes.count(),
            'comment_count': similar_article.comments.count(),
            'url': f"/blog/article/{similar_article.id}/",
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in similar_article.tags.all()[:5]]
        })

    return JsonResponse({
        'success': True,
        'article_id': article.id,
        'article_title': article.title,
        'recommendations': results,
        'count': len(results)
    })


def get_personalized_recommendations_api(request):
    """
    獲取個人化推薦 API
    基於用戶閱讀歷史的個人化推薦
    需要登入
    """
    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '需要登入才能獲取個人化推薦'
        }, status=401)

    # 獲取個人化推薦（預設 20 篇）
    limit = int(request.GET.get('limit', 20))
    recommended_articles = get_personalized_feed(request.user, limit=limit)

    # 序列化文章數據
    results = []
    for article in recommended_articles:
        results.append({
            'id': article.id,
            'title': article.title,
            'excerpt': article.content[:150] + '...' if len(article.content) > 150 else article.content,
            'author': {
                'username': article.author.username,
                'display_name': article.author.first_name if article.author.first_name else article.author.username,
            },
            'created_at': article.created_at.strftime('%Y-%m-%d'),
            
            'like_count': article.likes.count(),
            'comment_count': article.comments.count(),
            'url': f"/blog/article/{article.id}/",
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in article.tags.all()[:5]]
        })

    return JsonResponse({
        'success': True,
        'recommendations': results,
        'count': len(results),
        'strategy': 'personalized'
    })


def get_recommended_articles_api(request):
    """
    獲取推薦文章 API
    支援多種推薦策略
    - strategy: 推薦策略 (tag_based/reading_history/popular/collaborative/hybrid)
    - limit: 推薦數量
    - article_id: 當前文章 ID（用於相關文章推薦）
    """
    strategy = request.GET.get('strategy', 'hybrid')
    limit = int(request.GET.get('limit', 10))
    article_id = request.GET.get('article_id')

    # 獲取當前文章（如果有）
    article = None
    if article_id:
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            pass

    # 獲取推薦文章
    user = request.user if request.user.is_authenticated else None
    recommended_articles = get_recommended_articles(
        article=article,
        user=user,
        limit=limit,
        strategy=strategy
    )

    # 序列化文章數據
    results = []
    for rec_article in recommended_articles:
        results.append({
            'id': rec_article.id,
            'title': rec_article.title,
            'excerpt': rec_article.content[:150] + '...' if len(rec_article.content) > 150 else rec_article.content,
            'author': {
                'username': rec_article.author.username,
                'display_name': rec_article.author.first_name if rec_article.author.first_name else rec_article.author.username,
            },
            'created_at': rec_article.created_at.strftime('%Y-%m-%d'),
            
            'like_count': rec_article.likes.count(),
            'comment_count': rec_article.comments.count(),
            'url': f"/blog/article/{rec_article.id}/",
            'tags': [{'name': tag.name, 'slug': tag.slug} for tag in rec_article.tags.all()[:5]]
        })

    return JsonResponse({
        'success': True,
        'recommendations': results,
        'count': len(results),
        'strategy': strategy
    })


def personalized_feed(request):
    """
    個人化推薦頁面
    顯示基於用戶閱讀歷史的個人化推薦文章
    """
    if not request.user.is_authenticated:
        messages.info(request, '請先登入以獲取個人化推薦')
        return redirect('login')

    # 獲取個人化推薦
    recommended_articles = get_personalized_feed(request.user, limit=20)

    # 分頁
    paginator = Paginator(list(recommended_articles), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 獲取用戶最近閱讀的文章（用於顯示）
    recent_reads = ArticleReadHistory.objects.filter(
        user=request.user
    ).select_related('article').order_by('-last_read_at')[:5]

    context = {
        'articles': page_obj,
        'page_obj': page_obj,
        'recent_reads': recent_reads,
        'total_recommendations': len(list(recommended_articles)),
    }
    return render(request, 'blog/recommendations/personalized_feed.html', context)


def get_search_history(request):
    """
    獲取搜尋歷史 API
    返回使用者最近的搜尋記錄
    """
    from ..models import SearchHistory

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '請先登入'
        }, status=401)

    limit = int(request.GET.get('limit', 20))
    searches = SearchHistory.objects.filter(
        user=request.user
    ).values('query', 'search_type', 'results_count', 'created_at')[:limit]

    history_list = []
    for search in searches:
        history_list.append({
            'query': search['query'],
            'type': search['search_type'],
            'results_count': search['results_count'],
            'created_at': search['created_at'].strftime('%Y-%m-%d %H:%M'),
            'url': f"/blog/search/?q={search['query']}"
        })

    return JsonResponse({
        'success': True,
        'history': history_list,
        'count': len(history_list)
    })


def clear_search_history(request):
    """
    清除搜尋歷史 API
    刪除使用者的所有搜尋記錄
    """
    from ..models import SearchHistory

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '請先登入'
        }, status=401)

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': '僅支援 POST 請求'
        }, status=405)

    deleted_count, _ = SearchHistory.clear_user_history(request.user)

    return JsonResponse({
        'success': True,
        'message': f'已清除 {deleted_count} 筆搜尋記錄',
        'deleted_count': deleted_count
    })


def delete_search_item(request):
    """
    刪除單筆搜尋記錄 API
    """
    from ..models import SearchHistory

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'error': '請先登入'
        }, status=401)

    if request.method != 'POST':
        return JsonResponse({
            'success': False,
            'error': '僅支援 POST 請求'
        }, status=405)

    query = request.POST.get('query', '').strip()
    if not query:
        return JsonResponse({
            'success': False,
            'error': '缺少搜尋關鍵字'
        }, status=400)

    # 刪除該使用者的特定搜尋記錄
    deleted_count, _ = SearchHistory.objects.filter(
        user=request.user,
        query=query
    ).delete()

    return JsonResponse({
        'success': True,
        'message': f'已刪除搜尋記錄',
        'deleted_count': deleted_count
    })
