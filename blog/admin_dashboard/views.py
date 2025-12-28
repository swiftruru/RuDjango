from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from blog.models import Article, Comment, Tag, Like, Bookmark, ChatMessage, Notification, UserGroup, GroupMembership, GroupPost, SearchHistory, Message
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import JsonResponse


def is_staff(user):
    """檢查用戶是否為管理員"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def dashboard(request):
    """管理後台首頁 - 儀表板"""

    # 統計數據
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # 用戶統計
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=today).count()
    new_users_week = User.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = User.objects.filter(date_joined__date__gte=month_ago).count()

    # 文章統計
    total_articles = Article.objects.filter(status='published').count()
    draft_articles = Article.objects.filter(status='draft').count()
    articles_today = Article.objects.filter(created_at__date=today).count()
    articles_week = Article.objects.filter(created_at__date__gte=week_ago).count()

    # 互動統計
    total_comments = Comment.objects.count()
    total_likes = Like.objects.count()
    total_bookmarks = Bookmark.objects.count()
    comments_today = Comment.objects.filter(created_at__date=today).count()

    # 聊天統計
    total_messages = ChatMessage.objects.count()
    messages_today = ChatMessage.objects.filter(created_at__date=today).count()

    # 群組統計
    total_groups = UserGroup.objects.count()
    groups_week = UserGroup.objects.filter(created_at__date__gte=week_ago).count()
    total_group_members = GroupMembership.objects.count()
    total_group_posts = GroupPost.objects.count()

    # 通知統計
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    notifications_today = Notification.objects.filter(created_at__date=today).count()
    notifications_week = Notification.objects.filter(created_at__date__gte=week_ago).count()

    # 標籤統計
    total_tags = Tag.objects.count()
    tags_week = Tag.objects.filter(created_at__date__gte=week_ago).count()

    # 熱門文章 Top 10
    popular_articles = Article.objects.filter(status='published').annotate(
        like_count=Count('likes')
    ).order_by('-like_count', '-created_at')[:10]

    # 熱門標籤 Top 10
    popular_tags = Tag.objects.annotate(
        total_articles=Count('articles')
    ).order_by('-total_articles')[:10]

    # 活躍用戶 Top 10 (根據文章數量)
    active_users = User.objects.select_related('profile').annotate(
        article_count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('-article_count')[:10]

    # 熱門群組 Top 5 (使用現有的 member_count 和 post_count 欄位)
    popular_groups = UserGroup.objects.order_by('-member_count', '-post_count')[:5]

    # 最新通知
    recent_notifications = Notification.objects.select_related('user', 'sender').order_by('-created_at')[:5]

    # 按類型統計通知
    notification_by_type = {}
    for type_code, type_name in Notification.NOTIFICATION_TYPES:
        notification_by_type[type_name] = Notification.objects.filter(notification_type=type_code).count()

    context = {
        # 用戶統計
        'total_users': total_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,

        # 文章統計
        'total_articles': total_articles,
        'draft_articles': draft_articles,
        'articles_today': articles_today,
        'articles_week': articles_week,

        # 互動統計
        'total_comments': total_comments,
        'total_likes': total_likes,
        'total_bookmarks': total_bookmarks,
        'comments_today': comments_today,

        # 聊天統計
        'total_messages': total_messages,
        'messages_today': messages_today,

        # 群組統計
        'total_groups': total_groups,
        'groups_week': groups_week,
        'total_group_members': total_group_members,
        'total_group_posts': total_group_posts,

        # 通知統計
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notifications_today': notifications_today,
        'notifications_week': notifications_week,
        'notification_by_type': notification_by_type,

        # 標籤統計
        'total_tags': total_tags,
        'tags_week': tags_week,

        # 排行榜
        'popular_articles': popular_articles,
        'popular_tags': popular_tags,
        'active_users': active_users,
        'popular_groups': popular_groups,

        # 其他
        'recent_notifications': recent_notifications,
    }

    return render(request, 'admin_dashboard/pages/dashboard.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def user_list(request):
    """用戶列表"""

    # 取得搜尋和篩選參數
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', 'all')  # all, active, staff, superuser
    sort_by = request.GET.get('sort', '-date_joined')  # date_joined, username, articles

    # 基本查詢
    users = User.objects.select_related('profile').annotate(
        article_count=Count('articles', filter=Q(articles__status='published')),
        comment_count=Count('comments'),
        like_count=Count('likes')
    )

    # 搜尋功能
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )

    # 狀態篩選
    if filter_status == 'active':
        users = users.filter(is_active=True)
    elif filter_status == 'staff':
        users = users.filter(is_staff=True)
    elif filter_status == 'superuser':
        users = users.filter(is_superuser=True)

    # 排序
    if sort_by == 'username':
        users = users.order_by('username')
    elif sort_by == '-username':
        users = users.order_by('-username')
    elif sort_by == 'articles':
        users = users.order_by('-article_count')
    elif sort_by == 'date_joined':
        users = users.order_by('date_joined')
    else:
        users = users.order_by(sort_by)

    # 分頁
    paginator = Paginator(users, 20)  # 每頁顯示 20 個用戶
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_status': filter_status,
        'sort_by': sort_by,
        'total_users': users.count(),
    }

    return render(request, 'admin_dashboard/pages/users/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def user_detail(request, user_id):
    """用戶詳情"""

    user = get_object_or_404(User.objects.select_related('profile'), id=user_id)

    # 用戶統計
    total_articles = Article.objects.filter(author=user, status='published').count()
    draft_articles = Article.objects.filter(author=user, status='draft').count()
    total_comments = Comment.objects.filter(author=user).count()
    total_likes = Like.objects.filter(user=user).count()
    total_bookmarks = Bookmark.objects.filter(user=user).count()

    # 最近文章
    recent_articles = Article.objects.filter(author=user).order_by('-created_at')[:5]

    # 最近留言
    recent_comments = Comment.objects.filter(author=user).select_related('article').order_by('-created_at')[:5]

    # 追蹤統計
    followers_count = user.followers.count()
    following_count = user.following.count()

    # 獲取最後登入IP（從LoginAttempt記錄中取得最近一次成功登入的IP）
    from blog.models.security import LoginAttempt
    last_login_attempt = LoginAttempt.objects.filter(
        user=user,
        attempt_type='success'
    ).order_by('-attempted_at').first()
    last_login_ip = last_login_attempt.ip_address if last_login_attempt else None

    context = {
        'user_obj': user,
        'total_articles': total_articles,
        'draft_articles': draft_articles,
        'total_comments': total_comments,
        'total_likes': total_likes,
        'total_bookmarks': total_bookmarks,
        'recent_articles': recent_articles,
        'recent_comments': recent_comments,
        'followers_count': followers_count,
        'following_count': following_count,
        'last_login_ip': last_login_ip,
    }

    return render(request, 'admin_dashboard/pages/users/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def user_toggle_status(request, user_id):
    """切換用戶啟用/停用狀態"""

    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # 防止停用自己
        if user.id == request.user.id:
            return JsonResponse({
                'success': False,
                'message': '無法停用自己的帳號'
            })

        # 防止停用超級管理員
        if user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': '無法停用超級管理員'
            })

        # 切換狀態
        user.is_active = not user.is_active
        user.save()

        status_text = '啟用' if user.is_active else '停用'

        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'用戶 {user.username} 已{status_text}'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def user_toggle_staff(request, user_id):
    """切換用戶管理員權限"""

    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # 只有超級管理員可以設定管理員權限
        if not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': '只有超級管理員可以設定管理員權限'
            })

        # 切換管理員狀態
        user.is_staff = not user.is_staff
        user.save()

        status_text = '授予' if user.is_staff else '移除'

        return JsonResponse({
            'success': True,
            'is_staff': user.is_staff,
            'message': f'已{status_text}用戶 {user.username} 的管理員權限'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def article_list(request):
    """文章列表"""

    # 取得搜尋和篩選參數
    search_query = request.GET.get('search', '')
    filter_status = request.GET.get('status', 'all')  # all, published, draft
    sort_by = request.GET.get('sort', '-created_at')  # -created_at, created_at, -likes, -views, title

    # 基本查詢
    articles = Article.objects.select_related('author').prefetch_related('tags').annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    )

    # 搜尋功能
    if search_query:
        articles = articles.filter(
            Q(title__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()

    # 狀態篩選
    if filter_status == 'published':
        articles = articles.filter(status='published')
    elif filter_status == 'draft':
        articles = articles.filter(status='draft')

    # 排序
    if sort_by == '-likes':
        articles = articles.order_by('-like_count')
    elif sort_by == '-views':
        articles = articles.order_by('-views')
    elif sort_by == 'title':
        articles = articles.order_by('title')
    elif sort_by == 'created_at':
        articles = articles.order_by('created_at')
    else:
        articles = articles.order_by(sort_by)

    # 分頁
    paginator = Paginator(articles, 20)  # 每頁顯示 20 篇文章
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_status': filter_status,
        'sort_by': sort_by,
        'total_articles': articles.count(),
    }

    return render(request, 'admin_dashboard/pages/articles/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def article_detail(request, article_id):
    """文章詳情"""

    article = get_object_or_404(Article.objects.select_related('author').prefetch_related('tags'), id=article_id)

    # 統計資訊
    total_likes = Like.objects.filter(article=article).count()
    total_comments = Comment.objects.filter(article=article).count()
    total_bookmarks = Bookmark.objects.filter(article=article).count()

    # 最近留言
    recent_comments = Comment.objects.filter(article=article).select_related('author').order_by('-created_at')[:10]

    context = {
        'article': article,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_bookmarks': total_bookmarks,
        'recent_comments': recent_comments,
    }

    return render(request, 'admin_dashboard/pages/articles/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def article_delete(request, article_id):
    """刪除文章"""

    if request.method == 'POST':
        article = get_object_or_404(Article, id=article_id)

        article_title = article.title
        article.delete()

        return JsonResponse({
            'success': True,
            'message': f'文章《{article_title}》已刪除'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def comment_list(request):
    """留言列表"""

    # 取得搜尋和篩選參數
    search_query = request.GET.get('search', '')
    filter_article = request.GET.get('article', '')  # 篩選特定文章的留言
    sort_by = request.GET.get('sort', '-created_at')  # -created_at, created_at, author

    # 基本查詢
    comments = Comment.objects.select_related('author', 'article', 'parent')

    # 搜尋功能
    if search_query:
        comments = comments.filter(
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query) |
            Q(article__title__icontains=search_query)
        )

    # 文章篩選
    if filter_article:
        comments = comments.filter(article_id=filter_article)

    # 排序
    if sort_by == 'created_at':
        comments = comments.order_by('created_at')
    elif sort_by == 'author':
        comments = comments.order_by('author__username')
    else:
        comments = comments.order_by(sort_by)

    # 分頁
    paginator = Paginator(comments, 20)  # 每頁顯示 20 條留言
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 取得所有文章列表供篩選使用
    all_articles = Article.objects.filter(status='published').order_by('-created_at')[:50]

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_article': filter_article,
        'sort_by': sort_by,
        'total_comments': comments.count(),
        'all_articles': all_articles,
    }

    return render(request, 'admin_dashboard/pages/comments/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def comment_delete(request, comment_id):
    """刪除留言"""

    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)

        comment.delete()

        return JsonResponse({
            'success': True,
            'message': '留言已刪除'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def tag_list(request):
    """標籤列表"""

    # 取得搜尋和排序參數
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-published_article_count')  # -published_article_count, name, -created_at

    # 基本查詢
    tags = Tag.objects.annotate(
        published_article_count=Count('articles', filter=Q(articles__status='published'))
    )

    # 搜尋功能
    if search_query:
        tags = tags.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # 排序
    if sort_by == 'name':
        tags = tags.order_by('name')
    elif sort_by == '-created_at':
        tags = tags.order_by('-created_at')
    elif sort_by == 'created_at':
        tags = tags.order_by('created_at')
    else:
        tags = tags.order_by('-published_article_count', 'name')

    # 分頁
    paginator = Paginator(tags, 20)  # 每頁顯示 20 個標籤
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_tags': tags.count(),
    }

    return render(request, 'admin_dashboard/pages/tags/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def tag_detail(request, tag_id):
    """標籤詳情"""

    tag = get_object_or_404(Tag, id=tag_id)

    # 使用此標籤的文章
    articles = Article.objects.filter(tags=tag, status='published').select_related('author').annotate(
        like_count=Count('likes'),
        comment_count=Count('comments')
    ).order_by('-created_at')

    # 分頁
    paginator = Paginator(articles, 10)  # 每頁顯示 10 篇文章
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'tag': tag,
        'page_obj': page_obj,
        'total_articles': articles.count(),
    }

    return render(request, 'admin_dashboard/pages/tags/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def tag_delete(request, tag_id):
    """刪除標籤"""

    if request.method == 'POST':
        tag = get_object_or_404(Tag, id=tag_id)

        tag_name = tag.name
        tag.delete()

        return JsonResponse({
            'success': True,
            'message': f'標籤「{tag_name}」已刪除'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


# ==================== 聊天管理 ====================

@login_required
@user_passes_test(is_staff, login_url='/blog/')
def chat_list(request):
    """聊天室列表 - 直接從 ChatMessage 聚合"""
    from blog.models.chat import ChatMessage
    from django.db.models import Q
    from django.contrib.auth.models import User

    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-last_message_at')

    # 從 ChatMessage 中找出所有聊天對話（去重）
    messages = ChatMessage.objects.select_related('sender', 'recipient').all()

    # 建立聊天室字典
    chat_rooms_dict = {}

    for msg in messages:
        # 確保 user1_id < user2_id，避免重複
        user1_id = min(msg.sender.id, msg.recipient.id)
        user2_id = max(msg.sender.id, msg.recipient.id)
        key = (user1_id, user2_id)

        if key not in chat_rooms_dict:
            user1 = User.objects.get(id=user1_id)
            user2 = User.objects.get(id=user2_id)

            chat_rooms_dict[key] = {
                'user1': user1,
                'user2': user2,
                'messages': [],
            }

        chat_rooms_dict[key]['messages'].append(msg)

    # 轉換為列表並添加統計資訊
    chat_rooms = []
    for (user1_id, user2_id), data in chat_rooms_dict.items():
        room_messages = data['messages']
        last_message = max(room_messages, key=lambda m: m.created_at)

        # 創建虛擬聊天室物件
        class VirtualChatRoom:
            def __init__(self, user1, user2, messages, last_msg):
                self.id = f"{user1.id}-{user2.id}"
                self.user1 = user1
                self.user2 = user2
                self.total_messages = len(messages)
                self.last_message = last_msg
                self.last_message_at = last_msg.created_at
                self.created_at = min(messages, key=lambda m: m.created_at).created_at

        room = VirtualChatRoom(data['user1'], data['user2'], room_messages, last_message)

        # 搜尋過濾
        if search_query:
            if (search_query.lower() in room.user1.username.lower() or
                search_query.lower() in room.user2.username.lower()):
                chat_rooms.append(room)
        else:
            chat_rooms.append(room)

    # 排序
    if sort_by == '-last_message_at':
        chat_rooms.sort(key=lambda r: r.last_message_at, reverse=True)
    elif sort_by == 'last_message_at':
        chat_rooms.sort(key=lambda r: r.last_message_at)
    elif sort_by == '-created_at':
        chat_rooms.sort(key=lambda r: r.created_at, reverse=True)
    elif sort_by == 'created_at':
        chat_rooms.sort(key=lambda r: r.created_at)

    # 分頁
    paginator = Paginator(chat_rooms, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_rooms = len(chat_rooms)
    total_messages = ChatMessage.objects.count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_rooms': total_rooms,
        'total_messages': total_messages,
    }

    return render(request, 'admin_dashboard/pages/chats/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def chat_detail(request, room_id):
    """聊天室詳情 - 查看完整對話"""
    from blog.models.chat import ChatMessage
    from django.db.models import Q
    from django.contrib.auth.models import User

    # 解析虛擬 room_id (格式: "user1_id-user2_id")
    try:
        user1_id, user2_id = room_id.split('-')
        user1_id, user2_id = int(user1_id), int(user2_id)
    except (ValueError, AttributeError):
        from django.http import Http404
        raise Http404("聊天室不存在")

    user1 = get_object_or_404(User, id=user1_id)
    user2 = get_object_or_404(User, id=user2_id)

    # 創建虛擬聊天室物件
    class VirtualRoom:
        def __init__(self, u1, u2):
            self.id = f"{u1.id}-{u2.id}"
            self.user1 = u1
            self.user2 = u2

    room = VirtualRoom(user1, user2)

    # 獲取該聊天室的所有訊息
    messages = ChatMessage.objects.filter(
        Q(sender=user1, recipient=user2) |
        Q(sender=user2, recipient=user1)
    ).select_related('sender', 'recipient').order_by('created_at')

    # 分頁
    paginator = Paginator(messages, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_messages = messages.count()
    unread_count = messages.filter(is_read=False).count()

    # 計算最後活躍時間
    last_message = messages.order_by('-created_at').first()
    room.last_message_at = last_message.created_at if last_message else None

    context = {
        'room': room,
        'page_obj': page_obj,
        'total_messages': total_messages,
        'unread_count': unread_count,
    }

    return render(request, 'admin_dashboard/pages/chats/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def chat_delete(request, room_id):
    """刪除聊天室及其所有訊息"""
    if request.method == 'POST':
        from blog.models.chat import ChatMessage
        from django.db.models import Q
        from django.contrib.auth.models import User

        # 解析虛擬 room_id
        try:
            user1_id, user2_id = room_id.split('-')
            user1_id, user2_id = int(user1_id), int(user2_id)
        except (ValueError, AttributeError):
            return JsonResponse({'success': False, 'message': '無效的聊天室 ID'})

        user1 = get_object_or_404(User, id=user1_id)
        user2 = get_object_or_404(User, id=user2_id)

        # 刪除該聊天室的所有訊息
        deleted_count = ChatMessage.objects.filter(
            Q(sender=user1, recipient=user2) |
            Q(sender=user2, recipient=user1)
        ).delete()[0]

        room_name = f'{user1.username} ↔ {user2.username}'

        return JsonResponse({
            'success': True,
            'message': f'聊天室「{room_name}」及 {deleted_count} 則訊息已刪除'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


# ==================== 通知管理 ====================

@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_list(request):
    """通知列表"""

    # 取得搜尋和篩選參數
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('type', 'all')  # all, comment, like, follower, message, share, mention
    filter_status = request.GET.get('status', 'all')  # all, read, unread
    sort_by = request.GET.get('sort', '-created_at')  # -created_at, created_at

    # 基本查詢
    notifications = Notification.objects.select_related('user', 'sender')

    # 搜尋功能 (搜尋接收者或發送者)
    if search_query:
        notifications = notifications.filter(
            Q(user__username__icontains=search_query) |
            Q(sender__username__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    # 類型篩選
    if filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)

    # 狀態篩選
    if filter_status == 'read':
        notifications = notifications.filter(is_read=True)
    elif filter_status == 'unread':
        notifications = notifications.filter(is_read=False)

    # 排序
    if sort_by == 'created_at':
        notifications = notifications.order_by('created_at')
    else:
        notifications = notifications.order_by('-created_at')

    # 分頁
    paginator = Paginator(notifications, 20)  # 每頁顯示 20 條通知
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_notifications = Notification.objects.count()
    unread_count = Notification.objects.filter(is_read=False).count()
    read_count = Notification.objects.filter(is_read=True).count()

    # 各類型通知數量
    type_stats = {}
    for type_code, type_name in Notification.NOTIFICATION_TYPES:
        type_stats[type_code] = {
            'name': type_name,
            'count': Notification.objects.filter(notification_type=type_code).count()
        }

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_type': filter_type,
        'filter_status': filter_status,
        'sort_by': sort_by,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
        'read_count': read_count,
        'type_stats': type_stats,
        'notification_types': Notification.NOTIFICATION_TYPES,
    }

    return render(request, 'admin_dashboard/pages/notifications/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_detail(request, notification_id):
    """通知詳情"""

    notification = get_object_or_404(
        Notification.objects.select_related('user', 'sender', 'content_type'),
        id=notification_id
    )

    # 自動標記為已讀
    if not notification.is_read and notification.user == request.user:
        notification.mark_as_read()

    context = {
        'notification': notification,
    }

    return render(request, 'admin_dashboard/pages/notifications/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_delete(request, notification_id):
    """刪除通知"""

    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id)

        notification.delete()

        return JsonResponse({
            'success': True,
            'message': '通知已刪除'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_batch_delete(request):
    """批量刪除通知"""

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return JsonResponse({
                'success': False,
                'message': '未選擇任何通知'
            })

        deleted_count = Notification.objects.filter(id__in=notification_ids).delete()[0]

        return JsonResponse({
            'success': True,
            'message': f'已刪除 {deleted_count} 條通知'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_mark_read(request, notification_id):
    """標記通知為已讀"""

    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id)

        notification.mark_as_read()

        return JsonResponse({
            'success': True,
            'message': '通知已標記為已讀'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def notification_batch_mark_read(request):
    """批量標記通知為已讀"""

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        notification_ids = data.get('notification_ids', [])

        if not notification_ids:
            return JsonResponse({
                'success': False,
                'message': '未選擇任何通知'
            })

        notifications = Notification.objects.filter(id__in=notification_ids, is_read=False)
        updated_count = 0

        for notification in notifications:
            notification.mark_as_read()
            updated_count += 1

        return JsonResponse({
            'success': True,
            'message': f'已標記 {updated_count} 條通知為已讀'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


# ==================== 群組管理 ====================

@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_list(request):
    """群組列表"""

    # 取得搜尋和篩選參數
    search_query = request.GET.get('search', '')
    filter_type = request.GET.get('type', 'all')  # all, public, private, invite_only
    sort_by = request.GET.get('sort', '-created_at')  # -created_at, created_at, -member_count, -post_count, name

    # 基本查詢
    groups = UserGroup.objects.select_related('creator').annotate(
        total_members=Count('members', distinct=True),
        total_posts=Count('posts', distinct=True)
    )

    # 搜尋功能
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(creator__username__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # 類型篩選
    if filter_type != 'all':
        groups = groups.filter(group_type=filter_type)

    # 排序
    if sort_by == 'created_at':
        groups = groups.order_by('created_at')
    elif sort_by == '-member_count':
        groups = groups.order_by('-total_members')
    elif sort_by == '-post_count':
        groups = groups.order_by('-total_posts')
    elif sort_by == 'name':
        groups = groups.order_by('name')
    else:
        groups = groups.order_by('-created_at')

    # 分頁
    paginator = Paginator(groups, 20)  # 每頁顯示 20 個群組
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_groups = UserGroup.objects.count()
    public_groups = UserGroup.objects.filter(group_type='public').count()
    private_groups = UserGroup.objects.filter(group_type='private').count()
    invite_only_groups = UserGroup.objects.filter(group_type='invite_only').count()

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'filter_type': filter_type,
        'sort_by': sort_by,
        'total_groups': total_groups,
        'public_groups': public_groups,
        'private_groups': private_groups,
        'invite_only_groups': invite_only_groups,
        'group_types': UserGroup.GROUP_TYPE_CHOICES,
    }

    return render(request, 'admin_dashboard/pages/groups/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_detail(request, group_id):
    """群組詳情"""

    group = get_object_or_404(
        UserGroup.objects.select_related('creator').prefetch_related('memberships__user', 'posts__author'),
        id=group_id
    )

    # 群組成員列表
    memberships = GroupMembership.objects.filter(group=group).select_related('user').order_by('-joined_at')

    # 群組文章列表（最新10篇）
    recent_posts = GroupPost.objects.filter(group=group).select_related('author').order_by('-created_at')[:10]

    # 統計資訊
    total_members = memberships.count()
    total_posts = GroupPost.objects.filter(group=group).count()
    admin_count = memberships.filter(role__in=['owner', 'admin']).count()
    moderator_count = memberships.filter(role='moderator').count()

    # 角色分佈
    role_stats = {}
    for role_code, role_name in GroupMembership.ROLE_CHOICES:
        role_stats[role_code] = {
            'name': role_name,
            'count': memberships.filter(role=role_code).count()
        }

    context = {
        'group': group,
        'memberships': memberships,
        'recent_posts': recent_posts,
        'total_members': total_members,
        'total_posts': total_posts,
        'admin_count': admin_count,
        'moderator_count': moderator_count,
        'role_stats': role_stats,
    }

    return render(request, 'admin_dashboard/pages/groups/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_delete(request, group_id):
    """刪除群組"""

    if request.method == 'POST':
        group = get_object_or_404(UserGroup, id=group_id)

        group_name = group.name
        member_count = group.member_count
        post_count = group.post_count

        group.delete()

        return JsonResponse({
            'success': True,
            'message': f'群組「{group_name}」已刪除（{member_count} 位成員，{post_count} 篇文章）'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_member_remove(request, group_id, user_id):
    """移除群組成員"""

    if request.method == 'POST':
        group = get_object_or_404(UserGroup, id=group_id)
        user = get_object_or_404(User, id=user_id)

        # 檢查是否為群組創建者（創建者無法被移除）
        if group.creator.id == user.id:
            return JsonResponse({
                'success': False,
                'message': '無法移除群組創建者'
            })

        # 刪除成員關係
        membership = GroupMembership.objects.filter(group=group, user=user).first()
        if membership:
            membership.delete()

            # 更新群組成員數量
            group.member_count = group.members.count()
            group.save()

            return JsonResponse({
                'success': True,
                'message': f'已將 {user.username} 從群組中移除'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '該使用者不是群組成員'
            })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_member_change_role(request, group_id, user_id):
    """變更群組成員角色"""

    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        new_role = data.get('role')

        if new_role not in dict(GroupMembership.ROLE_CHOICES).keys():
            return JsonResponse({
                'success': False,
                'message': '無效的角色'
            })

        group = get_object_or_404(UserGroup, id=group_id)
        user = get_object_or_404(User, id=user_id)

        # 檢查是否為群組創建者（創建者角色無法變更）
        if group.creator.id == user.id:
            return JsonResponse({
                'success': False,
                'message': '無法變更群組創建者的角色'
            })

        membership = GroupMembership.objects.filter(group=group, user=user).first()
        if membership:
            old_role = membership.get_role_display()
            membership.role = new_role
            membership.save()

            return JsonResponse({
                'success': True,
                'message': f'{user.username} 的角色已從「{old_role}」變更為「{membership.get_role_display()}」'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '該使用者不是群組成員'
            })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def group_post_delete(request, post_id):
    """刪除群組文章"""

    if request.method == 'POST':
        post = get_object_or_404(GroupPost, id=post_id)

        post_title = post.title
        group_name = post.group.name

        post.delete()

        return JsonResponse({
            'success': True,
            'message': f'已刪除群組「{group_name}」中的文章「{post_title}」'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def search_analytics(request):
    """搜尋分析頁面"""

    # 時間範圍
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    # 基本統計
    total_searches = SearchHistory.objects.count()
    searches_today = SearchHistory.objects.filter(created_at__date=today).count()
    searches_week = SearchHistory.objects.filter(created_at__date__gte=week_ago).count()
    searches_month = SearchHistory.objects.filter(created_at__date__gte=month_ago).count()

    # 獨立用戶數
    unique_users_total = SearchHistory.objects.values('user').distinct().count()
    unique_users_week = SearchHistory.objects.filter(
        created_at__date__gte=week_ago
    ).values('user').distinct().count()

    # 熱門搜尋關鍵字 Top 20
    popular_searches = SearchHistory.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).values('query').annotate(
        search_count=Count('id'),
        avg_results=Count('results_count') / Count('id')
    ).order_by('-search_count')[:20]

    # 按搜尋類型統計
    search_by_type = {}
    for type_code, type_name in SearchHistory._meta.get_field('search_type').choices:
        count = SearchHistory.objects.filter(search_type=type_code).count()
        search_by_type[type_name] = count

    # 零結果搜尋（最近30天）
    zero_results_searches = SearchHistory.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30),
        results_count=0
    ).values('query').annotate(
        search_count=Count('id')
    ).order_by('-search_count')[:10]

    # 最活躍的搜尋用戶 Top 10
    active_searchers = SearchHistory.objects.values(
        'user__username', 'user__id'
    ).annotate(
        search_count=Count('id')
    ).order_by('-search_count')[:10]

    # 每日搜尋趨勢（最近7天）
    daily_searches = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        count = SearchHistory.objects.filter(created_at__date=date).count()
        daily_searches.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })

    # 平均結果數量
    from django.db.models import Avg
    avg_results = SearchHistory.objects.aggregate(
        avg=Avg('results_count')
    )['avg'] or 0

    context = {
        # 基本統計
        'total_searches': total_searches,
        'searches_today': searches_today,
        'searches_week': searches_week,
        'searches_month': searches_month,
        'unique_users_total': unique_users_total,
        'unique_users_week': unique_users_week,
        'avg_results': round(avg_results, 1),

        # 詳細數據
        'popular_searches': popular_searches,
        'search_by_type': search_by_type,
        'zero_results_searches': zero_results_searches,
        'active_searchers': active_searchers,
        'daily_searches': daily_searches,
    }

    return render(request, 'admin_dashboard/pages/analytics/search.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def system_settings(request):
    """系統設定頁面"""
    import sys
    import platform
    from django import VERSION as DJANGO_VERSION

    # Django 版本資訊
    django_version = '.'.join(map(str, DJANGO_VERSION))

    # Python 版本資訊
    python_version = sys.version.split()[0]
    python_path = sys.executable

    # 系統資訊
    system_info = {
        'os': platform.system(),
        'os_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
    }

    # 資料庫統計
    from django.conf import settings
    database_engine = settings.DATABASES['default']['ENGINE'].split('.')[-1]

    # 快取設定
    cache_backend = settings.CACHES['default']['BACKEND'].split('.')[-1]

    # 安裝的應用程式數量
    installed_apps_count = len(settings.INSTALLED_APPS)

    # 中介軟體數量
    middleware_count = len(settings.MIDDLEWARE)

    # 靜態檔案設定
    static_url = settings.STATIC_URL
    static_root = settings.STATIC_ROOT if hasattr(settings, 'STATIC_ROOT') else 'Not set'
    media_url = settings.MEDIA_URL
    media_root = settings.MEDIA_ROOT

    # 安全設定
    debug_mode = settings.DEBUG
    allowed_hosts = settings.ALLOWED_HOSTS
    secret_key_length = len(settings.SECRET_KEY)

    # 時區和語言設定
    timezone_setting = settings.TIME_ZONE
    language_code = settings.LANGUAGE_CODE
    use_tz = settings.USE_TZ

    context = {
        'django_version': django_version,
        'python_version': python_version,
        'python_path': python_path,
        'system_info': system_info,
        'database_engine': database_engine,
        'cache_backend': cache_backend,
        'installed_apps_count': installed_apps_count,
        'middleware_count': middleware_count,
        'static_url': static_url,
        'static_root': static_root,
        'media_url': media_url,
        'media_root': media_root,
        'debug_mode': debug_mode,
        'allowed_hosts': allowed_hosts,
        'secret_key_length': secret_key_length,
        'timezone_setting': timezone_setting,
        'language_code': language_code,
        'use_tz': use_tz,
    }

    return render(request, 'admin_dashboard/pages/system/settings.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def system_logs(request):
    """系統日誌頁面"""
    import os
    import logging
    from pathlib import Path

    # 獲取日誌文件路徑
    base_dir = Path(__file__).resolve().parent.parent.parent
    log_dir = base_dir / 'logs'

    # 日誌統計
    log_stats = {
        'total_logs': 0,
        'error_count': 0,
        'warning_count': 0,
        'info_count': 0,
    }

    # 日誌文件列表
    log_files = []
    if log_dir.exists():
        for log_file in log_dir.glob('*.log'):
            try:
                file_stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': file_stat.st_size,
                    'size_mb': round(file_stat.st_size / (1024 * 1024), 2),
                    'modified': timezone.datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.get_current_timezone()),
                })
            except Exception as e:
                continue

    # 按修改時間排序
    log_files.sort(key=lambda x: x['modified'], reverse=True)

    # 最近的日誌條目（從最新的日誌文件中讀取）
    recent_logs = []
    if log_files:
        try:
            latest_log_path = log_files[0]['path']
            with open(latest_log_path, 'r', encoding='utf-8', errors='ignore') as f:
                # 讀取最後100行
                lines = f.readlines()[-100:]
                for line in reversed(lines):
                    line = line.strip()
                    if line:
                        log_entry = {
                            'message': line,
                            'level': 'INFO',
                        }

                        # 判斷日誌級別
                        if 'ERROR' in line.upper():
                            log_entry['level'] = 'ERROR'
                            log_stats['error_count'] += 1
                        elif 'WARNING' in line.upper() or 'WARN' in line.upper():
                            log_entry['level'] = 'WARNING'
                            log_stats['warning_count'] += 1
                        else:
                            log_stats['info_count'] += 1

                        recent_logs.append(log_entry)
                        log_stats['total_logs'] += 1

                        if len(recent_logs) >= 50:
                            break
        except Exception as e:
            pass

    # Django 日誌配置信息
    logger_config = {
        'handlers': [],
        'loggers': [],
    }

    # 獲取已配置的日誌處理器
    from django.conf import settings
    if hasattr(settings, 'LOGGING'):
        logging_config = settings.LOGGING
        if 'handlers' in logging_config:
            logger_config['handlers'] = list(logging_config['handlers'].keys())
        if 'loggers' in logging_config:
            logger_config['loggers'] = list(logging_config['loggers'].keys())

    # 系統活動日誌（從資料庫）
    recent_activities = []

    # 最近的用戶註冊
    recent_users = User.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        recent_activities.append({
            'time': user.date_joined,
            'type': '用戶註冊',
            'description': f'用戶 {user.username} 註冊',
            'level': 'INFO',
        })

    # 最近的文章發布
    recent_articles = Article.objects.order_by('-created_at')[:5]
    for article in recent_articles:
        recent_activities.append({
            'time': article.created_at,
            'type': '文章發布',
            'description': f'{article.author.username} 發布文章「{article.title}」',
            'level': 'INFO',
        })

    # 最近的留言
    recent_comments = Comment.objects.select_related('author', 'article').order_by('-created_at')[:5]
    for comment in recent_comments:
        recent_activities.append({
            'time': comment.created_at,
            'type': '留言',
            'description': f'{comment.author.username} 在「{comment.article.title}」發表留言',
            'level': 'INFO',
        })

    # 按時間排序活動日誌
    recent_activities.sort(key=lambda x: x['time'], reverse=True)
    recent_activities = recent_activities[:20]

    context = {
        'log_stats': log_stats,
        'log_files': log_files,
        'recent_logs': recent_logs,
        'logger_config': logger_config,
        'recent_activities': recent_activities,
    }

    return render(request, 'admin_dashboard/pages/system/logs.html', context)


# ==================== 安全管理 ====================

@login_required
@user_passes_test(is_staff, login_url='/blog/')
def security_login_attempts(request):
    """登入嘗試記錄頁面"""
    from blog.models.security import LoginAttempt

    # 取得篩選參數
    filter_type = request.GET.get('type', 'all')  # all, success, failed
    filter_ip = request.GET.get('ip', '')
    filter_username = request.GET.get('username', '')
    sort_by = request.GET.get('sort', '-attempted_at')

    # 基本查詢
    attempts = LoginAttempt.objects.select_related('user').all()

    # 類型篩選
    if filter_type == 'success':
        attempts = attempts.filter(attempt_type='success')
    elif filter_type == 'failed':
        attempts = attempts.filter(attempt_type='failed')

    # IP 篩選
    if filter_ip:
        attempts = attempts.filter(ip_address__icontains=filter_ip)

    # 用戶名篩選
    if filter_username:
        attempts = attempts.filter(username__icontains=filter_username)

    # 排序
    attempts = attempts.order_by(sort_by)

    # 分頁
    paginator = Paginator(attempts, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_attempts = LoginAttempt.objects.count()
    success_count = LoginAttempt.objects.filter(attempt_type='success').count()
    failed_count = LoginAttempt.objects.filter(attempt_type='failed').count()

    # 最近24小時統計
    from datetime import timedelta
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    attempts_24h = LoginAttempt.objects.filter(attempted_at__gte=twenty_four_hours_ago).count()
    failed_24h = LoginAttempt.objects.filter(
        attempted_at__gte=twenty_four_hours_ago,
        attempt_type='failed'
    ).count()

    # 可疑 IP（過去5分鐘內失敗5次以上）
    five_minutes_ago = timezone.now() - timedelta(minutes=5)
    suspicious_ips = LoginAttempt.objects.filter(
        attempted_at__gte=five_minutes_ago,
        attempt_type='failed'
    ).values('ip_address').annotate(
        fail_count=Count('id')
    ).filter(fail_count__gte=5).order_by('-fail_count')[:10]

    # 最常失敗的用戶名（可能是被攻擊的目標）
    top_failed_usernames = LoginAttempt.objects.filter(
        attempt_type='failed'
    ).values('username').annotate(
        fail_count=Count('id')
    ).order_by('-fail_count')[:10]

    context = {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'filter_ip': filter_ip,
        'filter_username': filter_username,
        'sort_by': sort_by,
        'total_attempts': total_attempts,
        'success_count': success_count,
        'failed_count': failed_count,
        'attempts_24h': attempts_24h,
        'failed_24h': failed_24h,
        'suspicious_ips': suspicious_ips,
        'top_failed_usernames': top_failed_usernames,
    }

    return render(request, 'admin_dashboard/pages/security/login_attempts.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def security_ip_blacklist(request):
    """IP 黑名單管理"""
    from blog.models.security import IPBlacklist

    # 取得篩選參數
    filter_status = request.GET.get('status', 'active')  # active, inactive, all
    sort_by = request.GET.get('sort', '-blocked_at')

    # 基本查詢
    blacklist = IPBlacklist.objects.select_related('blocked_by').all()

    # 狀態篩選
    if filter_status == 'active':
        blacklist = blacklist.filter(is_active=True)
    elif filter_status == 'inactive':
        blacklist = blacklist.filter(is_active=False)

    # 排序
    blacklist = blacklist.order_by(sort_by)

    # 分頁
    paginator = Paginator(blacklist, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計
    total_blocked = IPBlacklist.objects.filter(is_active=True).count()

    context = {
        'page_obj': page_obj,
        'filter_status': filter_status,
        'sort_by': sort_by,
        'total_blocked': total_blocked,
    }

    return render(request, 'admin_dashboard/pages/security/ip_blacklist.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def security_ip_block(request, ip_address):
    """封鎖 IP"""
    if request.method == 'POST':
        import json
        from blog.models.security import IPBlacklist

        data = json.loads(request.body)
        reason = data.get('reason', '頻繁登入失敗')
        duration_hours = data.get('duration_hours', None)  # None 表示永久

        # 計算解除封鎖時間
        unblock_at = None
        if duration_hours:
            unblock_at = timezone.now() + timedelta(hours=int(duration_hours))

        # 創建或更新黑名單記錄
        blacklist, created = IPBlacklist.objects.get_or_create(
            ip_address=ip_address,
            defaults={
                'reason': reason,
                'blocked_by': request.user,
                'unblock_at': unblock_at,
                'is_active': True
            }
        )

        if not created:
            blacklist.reason = reason
            blacklist.blocked_by = request.user
            blacklist.unblock_at = unblock_at
            blacklist.is_active = True
            blacklist.save()

        return JsonResponse({
            'success': True,
            'message': f'IP {ip_address} 已封鎖'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def security_ip_unblock(request, blacklist_id):
    """解除 IP 封鎖"""
    if request.method == 'POST':
        from blog.models.security import IPBlacklist

        blacklist = get_object_or_404(IPBlacklist, id=blacklist_id)
        blacklist.is_active = False
        blacklist.save()

        return JsonResponse({
            'success': True,
            'message': f'IP {blacklist.ip_address} 已解除封鎖'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})


# ==================== 訊息管理 ====================

@login_required
@user_passes_test(is_staff, login_url='/blog/')
def message_list(request):
    """私人訊息管理列表"""

    # 取得篩選參數
    filter_status = request.GET.get('status', 'all')  # all, read, unread, recalled
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', '-created_at')

    # 基本查詢（排除已被雙方刪除的訊息）
    messages = Message.objects.select_related('sender', 'recipient').filter(
        Q(sender_deleted=False) | Q(recipient_deleted=False)
    )

    # 狀態篩選
    if filter_status == 'read':
        messages = messages.filter(is_read=True, is_recalled=False)
    elif filter_status == 'unread':
        messages = messages.filter(is_read=False, is_recalled=False)
    elif filter_status == 'recalled':
        messages = messages.filter(is_recalled=True)

    # 搜尋功能
    if search_query:
        messages = messages.filter(
            Q(subject__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(sender__username__icontains=search_query) |
            Q(recipient__username__icontains=search_query)
        )

    # 排序
    messages = messages.order_by(sort_by)

    # 分頁
    paginator = Paginator(messages, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計資訊
    total_messages = Message.objects.filter(
        Q(sender_deleted=False) | Q(recipient_deleted=False)
    ).count()
    read_count = Message.objects.filter(is_read=True, is_recalled=False).count()
    unread_count = Message.objects.filter(is_read=False, is_recalled=False).count()
    recalled_count = Message.objects.filter(is_recalled=True).count()

    # 最近24小時統計
    from datetime import timedelta
    twenty_four_hours_ago = timezone.now() - timedelta(hours=24)
    messages_24h = Message.objects.filter(created_at__gte=twenty_four_hours_ago).count()

    context = {
        'page_obj': page_obj,
        'filter_status': filter_status,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_messages': total_messages,
        'read_count': read_count,
        'unread_count': unread_count,
        'recalled_count': recalled_count,
        'messages_24h': messages_24h,
    }

    return render(request, 'admin_dashboard/pages/messages/list.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def message_detail(request, message_id):
    """訊息詳情"""

    message = get_object_or_404(
        Message.objects.select_related('sender', 'sender__profile', 'recipient', 'recipient__profile', 'parent_message'),
        id=message_id
    )

    # 獲取對話串（如果有的話）
    if message.parent_message:
        # 這是回覆訊息，獲取整個對話
        root_message = message.parent_message
        conversation = Message.objects.filter(
            Q(id=root_message.id) | Q(parent_message=root_message)
        ).select_related('sender', 'sender__profile', 'recipient', 'recipient__profile').order_by('created_at')
    else:
        # 這是原始訊息，獲取所有回覆
        conversation = Message.objects.filter(
            Q(id=message.id) | Q(parent_message=message)
        ).select_related('sender', 'sender__profile', 'recipient', 'recipient__profile').order_by('created_at')

    context = {
        'message': message,
        'conversation': conversation,
    }

    return render(request, 'admin_dashboard/pages/messages/detail.html', context)


@login_required
@user_passes_test(is_staff, login_url='/blog/')
def message_delete(request, message_id):
    """刪除訊息（硬刪除，僅管理員可用）"""

    if request.method == 'POST':
        message = get_object_or_404(Message, id=message_id)

        # 記錄訊息資訊用於回應
        sender = message.sender.username
        recipient = message.recipient.username

        # 硬刪除
        message.delete()

        return JsonResponse({
            'success': True,
            'message': f'已刪除 {sender} 發送給 {recipient} 的訊息'
        })

    return JsonResponse({'success': False, 'message': '無效的請求'})
