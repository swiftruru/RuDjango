"""
社群互動功能的 Views
包含：@提及、文章協作、使用者群組、活動/公告系統
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator

from ..models import (
    Mention, ArticleCollaborator, ArticleEditHistory,
    UserGroup, GroupMembership, GroupPost,
    Event, EventParticipant, Announcement,
    Article
)


# ============ @提及功能 ============

@login_required
def mention_list(request):
    """顯示使用者收到的所有@提及"""
    mentions = Mention.objects.filter(
        mentioned_user=request.user
    ).select_related(
        'mentioning_user',
        'article',
        'comment'
    ).order_by('-created_at')

    # 分頁
    paginator = Paginator(mentions, 20)
    page_number = request.GET.get('page')
    mentions_page = paginator.get_page(page_number)

    # 標記為已讀
    unread_mentions = mentions.filter(is_read=False)
    if unread_mentions.exists():
        unread_mentions.update(is_read=True)

    context = {
        'mentions': mentions_page,
        'total_count': mentions.count(),
    }
    return render(request, 'blog/social/mention_list.html', context)


@login_required
def mention_count(request):
    """API: 獲取未讀@提及數量"""
    count = Mention.objects.filter(
        mentioned_user=request.user,
        is_read=False
    ).count()
    return JsonResponse({'count': count})


@login_required
def search_users_for_mention(request):
    """API: 搜尋使用者（用於 @mention 自動完成）"""
    query = request.GET.get('q', '').strip()

    # 如果沒有查詢，顯示所有使用者（前 10 個）
    if not query:
        users = User.objects.filter(
            is_active=True
        ).exclude(
            id=request.user.id  # 排除自己
        ).values('id', 'username', 'first_name')[:10]
    else:
        # 搜尋使用者名稱
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query),
            is_active=True
        ).exclude(
            id=request.user.id  # 排除自己
        ).values('id', 'username', 'first_name')[:10]

    # 格式化結果
    user_list = []
    for user in users:
        display_name = user['first_name'] if user['first_name'] else user['username']
        user_list.append({
            'id': user['id'],
            'username': user['username'],
            'display_name': display_name,
            'label': f"@{user['username']}"
        })

    return JsonResponse({'users': user_list})


# ============ 文章協作功能 ============

@login_required
def article_collaborators(request, article_id):
    """顯示文章的協作者列表"""
    article = get_object_or_404(Article, id=article_id)

    # 檢查權限：只有作者或協作者可以查看
    is_author = article.author == request.user
    is_collaborator = ArticleCollaborator.objects.filter(
        article=article,
        user=request.user,
        is_accepted=True
    ).exists()

    if not (is_author or is_collaborator):
        messages.error(request, '您沒有權限查看此文章的協作者')
        return redirect('article_detail', id=article_id)

    collaborators = ArticleCollaborator.objects.filter(
        article=article
    ).select_related('user', 'invited_by').order_by('-invited_at')

    context = {
        'article': article,
        'collaborators': collaborators,
        'is_author': is_author,
    }
    return render(request, 'blog/social/article_collaborators.html', context)


@login_required
def invite_collaborator(request, article_id):
    """邀請協作者"""
    article = get_object_or_404(Article, id=article_id)

    # 只有作者可以邀請協作者
    if article.author != request.user:
        messages.error(request, '只有文章作者可以邀請協作者')
        return redirect('article_detail', id=article_id)

    if request.method == 'POST':
        username = request.POST.get('username')
        role = request.POST.get('role', 'editor')
        permission = request.POST.get('permission', 'edit')

        try:
            user = User.objects.get(username=username)

            # 不能邀請自己
            if user == request.user:
                messages.error(request, '不能邀請自己為協作者')
                return redirect('article_collaborators', article_id=article_id)

            # 檢查是否已經是協作者
            if ArticleCollaborator.objects.filter(article=article, user=user).exists():
                messages.warning(request, f'{username} 已經是協作者了')
                return redirect('article_collaborators', article_id=article_id)

            # 建立邀請
            collaborator = ArticleCollaborator.objects.create(
                article=article,
                user=user,
                role=role,
                permission=permission,
                invited_by=request.user
            )

            messages.success(request, f'已成功邀請 {username} 成為協作者')

            # TODO: 發送通知給被邀請者

        except User.DoesNotExist:
            messages.error(request, f'找不到使用者: {username}')

        return redirect('article_collaborators', article_id=article_id)

    return redirect('article_collaborators', article_id=article_id)


@login_required
def accept_collaboration(request, collaborator_id):
    """接受協作邀請"""
    collaborator = get_object_or_404(ArticleCollaborator, id=collaborator_id)

    if collaborator.user != request.user:
        messages.error(request, '無效的邀請')
        return redirect('blog_home')

    if collaborator.is_accepted:
        messages.info(request, '您已經接受過這個邀請了')
    else:
        collaborator.accept_invitation()
        messages.success(request, f'您已成為《{collaborator.article.title}》的協作者')

    return redirect('article_detail', id=collaborator.article.id)


@login_required
def remove_collaborator(request, collaborator_id):
    """移除協作者"""
    collaborator = get_object_or_404(ArticleCollaborator, id=collaborator_id)
    article = collaborator.article

    # 只有作者可以移除協作者
    if article.author != request.user:
        messages.error(request, '只有文章作者可以移除協作者')
        return redirect('article_detail', id=article.id)

    username = collaborator.user.username
    collaborator.delete()
    messages.success(request, f'已移除協作者 {username}')

    return redirect('article_collaborators', article_id=article.id)


@login_required
def article_edit_history(request, article_id):
    """查看文章編輯歷史"""
    article = get_object_or_404(Article, id=article_id)

    # 檢查權限
    is_author = article.author == request.user
    is_collaborator = ArticleCollaborator.objects.filter(
        article=article,
        user=request.user,
        is_accepted=True
    ).exists()

    if not (is_author or is_collaborator):
        messages.error(request, '您沒有權限查看此文章的編輯歷史')
        return redirect('article_detail', id=article_id)

    history = ArticleEditHistory.objects.filter(
        article=article
    ).select_related('editor').order_by('-edited_at')

    # 分頁
    paginator = Paginator(history, 20)
    page_number = request.GET.get('page')
    history_page = paginator.get_page(page_number)

    context = {
        'article': article,
        'history': history_page,
    }
    return render(request, 'blog/social/article_edit_history.html', context)


# ============ 使用者群組功能 ============

def group_list(request):
    """顯示所有群組列表"""
    # 基本查詢
    groups = UserGroup.objects.annotate(
        real_member_count=Count('members')
    ).order_by('-created_at')

    # 搜尋
    search_query = request.GET.get('search', '')
    if search_query:
        groups = groups.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # 篩選類型
    group_type = request.GET.get('type', '')
    if group_type:
        groups = groups.filter(group_type=group_type)

    # 分頁
    paginator = Paginator(groups, 12)
    page_number = request.GET.get('page')
    groups_page = paginator.get_page(page_number)

    context = {
        'groups': groups_page,
        'search_query': search_query,
        'selected_type': group_type,
    }
    return render(request, 'blog/social/group_list.html', context)


@login_required
def group_create(request):
    """建立新群組"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        group_type = request.POST.get('group_type', 'public')
        tags = request.POST.get('tags', '')

        # 驗證
        if not name or not description:
            messages.error(request, '請填寫群組名稱和描述')
            return render(request, 'blog/social/group_create.html')

        # 檢查名稱是否已存在
        if UserGroup.objects.filter(name=name).exists():
            messages.error(request, '此群組名稱已被使用')
            return render(request, 'blog/social/group_create.html')

        # 建立群組
        group = UserGroup.objects.create(
            name=name,
            description=description,
            group_type=group_type,
            tags=tags,
            creator=request.user
        )

        # 自動加入創建者為群組擁有者
        GroupMembership.objects.create(
            group=group,
            user=request.user,
            role='owner',
            join_method='created'
        )

        messages.success(request, f'成功建立群組《{name}》')
        return redirect('group_detail', group_id=group.id)

    return render(request, 'blog/social/group_create.html')


def group_detail(request, group_id):
    """群組詳情頁"""
    group = get_object_or_404(UserGroup, id=group_id)

    # 檢查使用者是否為成員
    is_member = False
    is_admin = False
    membership = None

    if request.user.is_authenticated:
        is_member = group.is_member(request.user)
        is_admin = group.is_admin(request.user)
        if is_member:
            membership = GroupMembership.objects.get(group=group, user=request.user)

    # 獲取群組文章
    posts = GroupPost.objects.filter(
        group=group
    ).select_related('author').order_by('-is_pinned', '-created_at')

    # 分頁
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts_page = paginator.get_page(page_number)

    # 獲取成員列表（前10位）
    members = GroupMembership.objects.filter(
        group=group
    ).select_related('user').order_by('-joined_at')[:10]

    context = {
        'group': group,
        'is_member': is_member,
        'is_admin': is_admin,
        'membership': membership,
        'posts': posts_page,
        'members': members,
    }
    return render(request, 'blog/social/group_detail.html', context)


@login_required
def group_join(request, group_id):
    """加入群組"""
    group = get_object_or_404(UserGroup, id=group_id)

    if not group.can_join(request.user):
        messages.error(request, '無法加入此群組')
        return redirect('group_detail', group_id=group_id)

    # 建立成員關係
    GroupMembership.objects.create(
        group=group,
        user=request.user,
        role='member',
        join_method='joined'
    )

    # 更新成員數量
    group.member_count = group.members.count()
    group.save()

    messages.success(request, f'成功加入群組《{group.name}》')
    return redirect('group_detail', group_id=group_id)


@login_required
def group_leave(request, group_id):
    """離開群組"""
    group = get_object_or_404(UserGroup, id=group_id)

    try:
        membership = GroupMembership.objects.get(group=group, user=request.user)

        # 群組擁有者不能離開
        if membership.role == 'owner':
            messages.error(request, '群組擁有者不能離開群組，請先轉移擁有權或刪除群組')
            return redirect('group_detail', group_id=group_id)

        membership.delete()

        # 更新成員數量
        group.member_count = group.members.count()
        group.save()

        messages.success(request, f'已離開群組《{group.name}》')
        return redirect('group_list')

    except GroupMembership.DoesNotExist:
        messages.error(request, '您不是此群組的成員')
        return redirect('group_detail', group_id=group_id)


@login_required
def group_post_create(request, group_id):
    """在群組中發文"""
    group = get_object_or_404(UserGroup, id=group_id)

    # 檢查是否為成員
    if not group.is_member(request.user):
        messages.error(request, '只有群組成員才能發文')
        return redirect('group_detail', group_id=group_id)

    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        post_type = request.POST.get('post_type', 'discussion')

        if not title or not content:
            messages.error(request, '請填寫標題和內容')
            return render(request, 'blog/social/group_post_create.html', {'group': group})

        # 建立文章
        post = GroupPost.objects.create(
            group=group,
            author=request.user,
            title=title,
            content=content,
            post_type=post_type
        )

        # 更新群組文章數量和成員發文統計
        group.post_count += 1
        group.save()

        membership = GroupMembership.objects.get(group=group, user=request.user)
        membership.posts_count += 1
        membership.save()

        messages.success(request, '發文成功')
        return redirect('group_post_detail', post_id=post.id)

    context = {'group': group}
    return render(request, 'blog/social/group_post_create.html', context)


def group_post_detail(request, post_id):
    """群組文章詳情"""
    post = get_object_or_404(
        GroupPost.objects.select_related('group', 'author'),
        id=post_id
    )

    # 增加瀏覽數
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # 檢查使用者權限
    is_member = False
    is_author = False
    if request.user.is_authenticated:
        is_member = post.group.is_member(request.user)
        is_author = post.author == request.user

    context = {
        'post': post,
        'is_member': is_member,
        'is_author': is_author,
    }
    return render(request, 'blog/social/group_post_detail.html', context)


@login_required
def group_members(request, group_id):
    """群組成員列表"""
    group = get_object_or_404(UserGroup, id=group_id)

    members = GroupMembership.objects.filter(
        group=group
    ).select_related('user').order_by('-joined_at')

    # 分頁
    paginator = Paginator(members, 24)
    page_number = request.GET.get('page')
    members_page = paginator.get_page(page_number)

    context = {
        'group': group,
        'members': members_page,
    }
    return render(request, 'blog/social/group_members.html', context)


# ============ 活動/公告系統 ============

def event_list(request):
    """活動列表"""
    # 基本查詢
    events = Event.objects.filter(
        status='published'
    ).select_related('organizer').order_by('-start_time')

    # 篩選類型
    event_type = request.GET.get('type', '')
    if event_type:
        events = events.filter(event_type=event_type)

    # 篩選狀態（進行中/即將開始/已結束）
    status_filter = request.GET.get('status', '')
    now = timezone.now()
    if status_filter == 'ongoing':
        events = events.filter(start_time__lte=now, end_time__gte=now)
    elif status_filter == 'upcoming':
        events = events.filter(start_time__gt=now)
    elif status_filter == 'past':
        events = events.filter(end_time__lt=now)

    # 分頁
    paginator = Paginator(events, 12)
    page_number = request.GET.get('page')
    events_page = paginator.get_page(page_number)

    context = {
        'events': events_page,
        'selected_type': event_type,
        'selected_status': status_filter,
    }
    return render(request, 'blog/social/event_list.html', context)


def event_detail(request, event_id):
    """活動詳情"""
    event = get_object_or_404(
        Event.objects.select_related('organizer', 'group'),
        id=event_id
    )

    # 增加瀏覽數
    event.views_count += 1
    event.save(update_fields=['views_count'])

    # 檢查使用者是否已報名
    is_registered = False
    participant = None
    if request.user.is_authenticated:
        try:
            participant = EventParticipant.objects.get(event=event, user=request.user)
            is_registered = True
        except EventParticipant.DoesNotExist:
            pass

    # 獲取參與者列表（前10位）
    participants = EventParticipant.objects.filter(
        event=event,
        status__in=['registered', 'confirmed', 'attended']
    ).select_related('user').order_by('-registered_at')[:10]

    context = {
        'event': event,
        'is_registered': is_registered,
        'participant': participant,
        'participants': participants,
        'can_register': event.can_register(),
        'is_ongoing': event.is_ongoing(),
    }
    return render(request, 'blog/social/event_detail.html', context)


@login_required
def event_create(request):
    """建立活動"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        event_type = request.POST.get('event_type')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        location = request.POST.get('location', '')
        online_link = request.POST.get('online_link', '')
        max_participants = request.POST.get('max_participants', '')

        # 驗證
        if not all([title, description, event_type, start_time, end_time]):
            messages.error(request, '請填寫所有必填欄位')
            return render(request, 'blog/social/event_create.html')

        # 建立活動
        event = Event.objects.create(
            title=title,
            description=description,
            event_type=event_type,
            organizer=request.user,
            start_time=start_time,
            end_time=end_time,
            location=location,
            online_link=online_link,
            max_participants=int(max_participants) if max_participants else None,
            status='published'
        )

        messages.success(request, f'成功建立活動《{title}》')
        return redirect('event_detail', event_id=event.id)

    return render(request, 'blog/social/event_create.html')


@login_required
def event_register(request, event_id):
    """報名活動"""
    event = get_object_or_404(Event, id=event_id)

    if not event.can_register():
        messages.error(request, '此活動目前無法報名')
        return redirect('event_detail', event_id=event_id)

    # 檢查是否已報名
    if EventParticipant.objects.filter(event=event, user=request.user).exists():
        messages.warning(request, '您已經報名過此活動了')
        return redirect('event_detail', event_id=event_id)

    # 建立報名
    EventParticipant.objects.create(
        event=event,
        user=request.user,
        status='registered'
    )

    # 更新參與人數
    event.participants_count = event.participants.count()
    event.save()

    messages.success(request, f'成功報名活動《{event.title}》')
    return redirect('event_detail', event_id=event_id)


@login_required
def event_cancel_registration(request, event_id):
    """取消報名"""
    event = get_object_or_404(Event, id=event_id)

    try:
        participant = EventParticipant.objects.get(event=event, user=request.user)
        participant.status = 'cancelled'
        participant.save()

        # 更新參與人數
        event.participants_count = event.participants.filter(
            status__in=['registered', 'confirmed', 'attended']
        ).count()
        event.save()

        messages.success(request, '已取消報名')
    except EventParticipant.DoesNotExist:
        messages.error(request, '您尚未報名此活動')

    return redirect('event_detail', event_id=event_id)


def announcement_list(request):
    """系統公告列表"""
    announcements = Announcement.objects.filter(
        is_active=True
    ).select_related('author').order_by('-is_pinned', '-created_at')

    # 過濾未過期的公告
    active_announcements = [a for a in announcements if a.is_visible()]

    # 分頁
    paginator = Paginator(active_announcements, 15)
    page_number = request.GET.get('page')
    announcements_page = paginator.get_page(page_number)

    context = {
        'announcements': announcements_page,
    }
    return render(request, 'blog/social/announcement_list.html', context)


def announcement_detail(request, announcement_id):
    """公告詳情"""
    announcement = get_object_or_404(
        Announcement.objects.select_related('author'),
        id=announcement_id
    )

    # 增加瀏覽數
    announcement.views_count += 1
    announcement.save(update_fields=['views_count'])

    context = {
        'announcement': announcement,
    }
    return render(request, 'blog/social/announcement_detail.html', context)


@login_required
def my_groups(request):
    """我的群組列表"""
    memberships = GroupMembership.objects.filter(
        user=request.user
    ).select_related('group').order_by('-joined_at')

    context = {
        'memberships': memberships,
    }
    return render(request, 'blog/social/my_groups.html', context)


@login_required
def my_events(request):
    """我的活動（已報名的活動）"""
    participations = EventParticipant.objects.filter(
        user=request.user,
        status__in=['registered', 'confirmed', 'attended']
    ).select_related('event').order_by('-registered_at')

    context = {
        'participations': participations,
    }
    return render(request, 'blog/social/my_events.html', context)
