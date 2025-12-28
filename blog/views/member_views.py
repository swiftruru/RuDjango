"""
會員相關的視圖函數
處理會員中心、個人資料、會員列表等功能
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from ..models import UserProfile, Activity, UserAchievement, UserCourseProgress, Follow, ArticleReadHistory, Article, Comment, Like
from ..utils.notifications import notify_follower


@login_required
def member(request):
    """
    會員中心頁面 - 重定向到當前用戶的個人資料頁面
    """
    return redirect('member_profile', username=request.user.username)


def member_profile(request, username):
    """查看會員的公開資料（包括自己和其他人）"""
    target_user = get_object_or_404(User, username=username)

    # 取得或建立使用者的 Profile
    try:
        profile = UserProfile.objects.select_related('user').get(user=target_user)
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=target_user)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 計算統計數據
    # 計算用戶所有文章收到的讚數總和
    likes_received = Like.objects.filter(article__author=target_user).count()

    stats = {
        'posts': target_user.articles.count(),
        'comments': target_user.comments.count(),  # 計算實際留言數
        'likes_received': likes_received,
        'followers': target_user.followers.count(),
        'following': target_user.following.count(),
    }

    # 取得最近活動（只有本人能看到）
    recent_activities = []
    if is_own_profile:
        recent_activities = Activity.objects.filter(user=target_user).order_by('-created_at')[:5]

    # 取得使用者技能
    user_skills = target_user.skills.all()

    # 取得使用者成就
    user_achievements = UserAchievement.objects.filter(user=target_user).select_related('achievement').order_by('-unlocked_at')[:4]

    # 取得學習進度（只有本人能看到）
    # 基於閱讀記錄統計，按作者分類
    learning_progress = []
    if is_own_profile:
        # 獲取用戶的所有閱讀記錄
        read_articles = ArticleReadHistory.objects.filter(user=target_user).select_related('article', 'article__author')

        # 統計各作者的文章總數和已閱讀數
        author_stats = {}
        for record in read_articles:
            author = record.article.author
            if author:
                author_name = author.first_name or author.username
                if author_name not in author_stats:
                    # 計算該作者的總文章數
                    total_articles = Article.objects.filter(author=author).count()
                    author_stats[author_name] = {
                        'read': 0,
                        'total': total_articles,
                        'author': author_name,
                    }
                author_stats[author_name]['read'] += 1

        # 轉換為列表格式並計算進度百分比
        for author_name, author_stat in author_stats.items():
            if author_stat['total'] > 0:
                progress = int((author_stat['read'] / author_stat['total']) * 100)
                learning_progress.append({
                    'course': f"{author_name} 的文章",
                    'progress': progress,
                    'color': '#667eea' if progress < 100 else '#48bb78',
                })

        # 按進度排序，取前3個
        learning_progress = sorted(learning_progress, key=lambda x: x['progress'], reverse=True)[:3]

    # 取得最近發表的文章（公開，所有人都能看到）
    recent_articles = target_user.articles.order_by('-created_at')[:5]

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
        'email': target_user.email if is_own_profile else '',  # 只有本人能看到 email
        'avatar': profile.avatar,  # 頭像圖片
        'school': profile.school,
        'grade': profile.grade,
        'bio': profile.bio,
        'location': profile.location,
        'birthday': profile.birthday if is_own_profile else None,  # 只有本人能看到生日
        'joined_date': target_user.date_joined.strftime('%Y-%m-%d'),
        'level': profile.level,
        'points': profile.points,
        'next_level_points': profile.get_next_level_points(),
        'website': profile.website,
        'github': profile.github,
        'stats': stats,
        'recent_activities': recent_activities,
        'skills': user_skills,
        'achievements': user_achievements,
        'learning_progress': learning_progress,
        'recent_articles': recent_articles,
    }

    # 追蹤狀態
    is_following = False
    if request.user.is_authenticated and not is_own_profile:
        is_following = Follow.objects.filter(follower=request.user, following=target_user).exists()

    context = {
        'member': member_data,
        'profile': profile,  # 添加 profile 物件以便使用 avatar_url filter
        'is_own_profile': is_own_profile,
        'is_following': is_following,
    }
    return render(request, 'blog/members/profile.html', context)


@login_required
def member_edit(request):
    """編輯個人資料"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()

            # 重新載入使用者物件以確保取得最新資料
            request.user.refresh_from_db()

            # 如果有上傳頭像，確保 profile 也重新載入
            if 'avatar' in request.FILES:
                profile.refresh_from_db()

            messages.success(request, '✅ 個人資料已成功更新！')
            return redirect('member')
    else:
        form = UserProfileForm(instance=profile, user=request.user)

    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'blog/members/edit_profile.html', context)


def user_login(request):
    """
    使用者登入
    """
    # 獲取 IP 地址
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        # 檢查 IP 是否被封鎖
        from blog.models.security import IPBlacklist, IPWhitelist, LoginAttempt

        # 如果不在白名單且在黑名單中，拒絕登入
        if not IPWhitelist.is_whitelisted(ip_address) and IPBlacklist.is_blocked(ip_address):
            messages.error(request, '❌ 您的 IP 地址已被封鎖，請聯繫管理員。')
            return render(request, 'blog/members/login.html', {
                'form': form,
                'action': '登入',
            })

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # 記錄成功的登入嘗試
                LoginAttempt.record_attempt(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True,
                    user=user
                )

                login(request, user)
                # 使用暱稱（first_name）顯示，如果沒有則顯示帳號名
                display_name = user.first_name if user.first_name else username
                messages.success(request, f'✅ 歡迎回來，{display_name}！')
                # 重定向到 next 參數指定的頁面，或預設到部落格首頁
                next_url = request.GET.get('next', '/blog/')
                return redirect(next_url)
            else:
                # 記錄失敗的登入嘗試
                from django.contrib.auth.models import User
                try:
                    existing_user = User.objects.get(username=username)
                    failure_reason = '密碼錯誤'
                except User.DoesNotExist:
                    existing_user = None
                    failure_reason = '用戶不存在'

                LoginAttempt.record_attempt(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    user=existing_user,
                    failure_reason=failure_reason
                )
        else:
            # 表單驗證失敗（例如必填欄位未填）
            username = request.POST.get('username', '')
            if username:
                LoginAttempt.record_attempt(
                    username=username,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason='表單驗證失敗'
                )
    else:
        form = CustomAuthenticationForm()

    context = {
        'form': form,
        'action': '登入',
    }
    return render(request, 'blog/members/login.html', context)


def user_register(request):
    """
    使用者註冊
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'✅ 帳號 {username} 註冊成功！請登入。')
            return redirect('user_login')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
        'action': '註冊',
    }
    return render(request, 'blog/members/register.html', context)


def user_logout(request):
    """
    使用者登出
    """
    logout(request)
    messages.success(request, '✅ 您已成功登出')
    return redirect('blog_home')


@login_required
def edit_skills(request):
    """編輯技能標籤"""
    from ..models import Skill

    if request.method == 'POST':
        skills_data = request.POST.get('skills', '')

        # 清除當前所有技能
        request.user.skills.clear()

        if skills_data:
            # 分割技能字符串（支援逗號和分號分隔）
            skill_names = [s.strip() for s in skills_data.replace(';', ',').split(',') if s.strip()]

            # 為每個技能創建或獲取 Skill 對象，並添加到用戶
            for skill_name in skill_names:
                # 限制技能名稱長度
                if len(skill_name) <= 50:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    request.user.skills.add(skill)

        messages.success(request, '✅ 技能標籤已成功更新！')
        return redirect('member')

    # GET 請求 - 顯示編輯頁面
    current_skills = request.user.skills.all()

    context = {
        'current_skills': current_skills,
    }
    return render(request, 'blog/members/edit_skills.html', context)


def member_activities(request, username):
    """查看會員的所有活動記錄"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 只有本人能查看自己的活動記錄
    if not is_own_profile:
        messages.error(request, '❌ 您無法查看其他人的活動記錄')
        return redirect('member_profile', username=username)

    # 取得所有活動記錄
    activities_list = Activity.objects.filter(user=target_user).order_by('-created_at')

    # 分頁設定（與部落格列表一致）
    paginator = Paginator(activities_list, 10)  # 每頁顯示 10 筆
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
    }

    context = {
        'member': member_data,
        'activities': page_obj,
        'page_obj': page_obj,
    }

    return render(request, 'blog/members/activities.html', context)


def member_achievements(request, username):
    """查看會員的所有成就徽章"""
    from ..models import Achievement

    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 取得所有成就
    all_achievements = Achievement.objects.all().order_by('category', 'name')

    # 取得使用者已解鎖的成就
    unlocked_achievement_ids = set(
        UserAchievement.objects.filter(user=target_user).values_list('achievement_id', flat=True)
    )

    # 準備成就資料，標記是否已解鎖
    achievements_data = []
    for achievement in all_achievements:
        user_achievement = UserAchievement.objects.filter(
            user=target_user,
            achievement=achievement
        ).first()

        achievements_data.append({
            'achievement': achievement,
            'is_unlocked': achievement.id in unlocked_achievement_ids,
            'unlocked_at': user_achievement.unlocked_at if user_achievement else None,
        })

    # 按分類分組
    categories = {}
    for data in achievements_data:
        category = data['achievement'].get_category_display()
        if category not in categories:
            categories[category] = []
        categories[category].append(data)

    # 計算統計數據
    total_achievements = len(all_achievements)
    unlocked_count = len(unlocked_achievement_ids)
    unlock_percentage = int((unlocked_count / total_achievements * 100)) if total_achievements > 0 else 0

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
    }

    context = {
        'member': member_data,
        'is_own_profile': is_own_profile,
        'categories': categories,
        'total_achievements': total_achievements,
        'unlocked_count': unlocked_count,
        'unlock_percentage': unlock_percentage,
    }

    return render(request, 'blog/members/achievements.html', context)


def learning_progress(request, username):
    """查看會員的學習進度詳細頁面"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 只有本人能查看自己的學習進度
    if not is_own_profile:
        messages.error(request, '❌ 您無法查看其他人的學習進度')
        return redirect('member_profile', username=username)

    # 獲取所有閱讀記錄
    read_histories = ArticleReadHistory.objects.filter(user=target_user).select_related('article', 'article__author').order_by('-last_read_at')

    # 統計總體數據
    total_articles_read = read_histories.count()
    total_read_count = read_histories.aggregate(Sum('read_count'))['read_count__sum'] or 0
    total_reading_time = read_histories.aggregate(Sum('reading_time_seconds'))['reading_time_seconds__sum'] or 0

    # 計算總閱讀時長（轉換為小時和分鐘）
    reading_hours = total_reading_time // 3600
    reading_minutes = (total_reading_time % 3600) // 60

    # 按作者統計進度
    author_progress = []
    author_stats = {}
    # 使用 set 來追蹤已經計數過的文章，避免重複計算
    counted_articles = {}

    for record in read_histories:
        author = record.article.author
        if author:
            author_name = author.first_name or author.username
            if author_name not in author_stats:
                # 計算該作者的總文章數
                total_articles = Article.objects.filter(author=author).count()
                author_stats[author_name] = {
                    'read': 0,
                    'total': total_articles,
                    'author': author_name,
                    'author_username': author.username,
                }
                counted_articles[author_name] = set()

            # 只計算未計數過的文章
            if record.article.id not in counted_articles[author_name]:
                author_stats[author_name]['read'] += 1
                counted_articles[author_name].add(record.article.id)

    # 轉換為列表並計算百分比
    for author_name, stats in author_stats.items():
        if stats['total'] > 0:
            progress = int((stats['read'] / stats['total']) * 100)
            author_progress.append({
                'author': author_name,
                'author_username': stats['author_username'],
                'read': stats['read'],
                'total': stats['total'],
                'progress': progress,
                'color': '#48bb78' if progress == 100 else '#667eea',
            })

    # 按進度排序
    author_progress = sorted(author_progress, key=lambda x: x['progress'], reverse=True)

    # 最近閱讀的文章（顯示最新10篇）
    recent_reads = read_histories[:10]

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
    }

    context = {
        'member': member_data,
        'is_own_profile': is_own_profile,
        'total_articles_read': total_articles_read,
        'total_read_count': total_read_count,
        'reading_hours': reading_hours,
        'reading_minutes': reading_minutes,
        'author_progress': author_progress,
        'recent_reads': recent_reads,
    }

    return render(request, 'blog/members/learning_progress.html', context)


def followers_list(request, username):
    """查看會員的追蹤者列表"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 取得追蹤者列表
    followers = Follow.objects.filter(following=target_user).select_related('follower', 'follower__profile').order_by('-created_at')

    # 分頁
    paginator = Paginator(followers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 如果當前用戶已登入，檢查是否追蹤了列表中的用戶
    following_status = {}
    if request.user.is_authenticated:
        for follow in page_obj:
            follower = follow.follower
            if follower != request.user:
                following_status[follower.id] = Follow.objects.filter(
                    follower=request.user,
                    following=follower
                ).exists()

    context = {
        'member': target_user,
        'is_own_profile': is_own_profile,
        'page_obj': page_obj,
        'following_status': following_status,
        'list_type': 'followers',
        'total_count': followers.count(),
    }

    return render(request, 'blog/members/follow_list.html', context)


def following_list(request, username):
    """查看會員的追蹤中列表"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 取得追蹤中列表
    following = Follow.objects.filter(follower=target_user).select_related('following', 'following__profile').order_by('-created_at')

    # 分頁
    paginator = Paginator(following, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 如果當前用戶已登入，檢查是否追蹤了列表中的用戶
    following_status = {}
    if request.user.is_authenticated:
        for follow in page_obj:
            following_user = follow.following
            if following_user != request.user:
                following_status[following_user.id] = Follow.objects.filter(
                    follower=request.user,
                    following=following_user
                ).exists()

    context = {
        'member': target_user,
        'is_own_profile': is_own_profile,
        'page_obj': page_obj,
        'following_status': following_status,
        'list_type': 'following',
        'total_count': following.count(),
    }

    return render(request, 'blog/members/follow_list.html', context)


@login_required
def follow_user(request, username):
    """
    追蹤/取消追蹤使用者
    - 使用者可以追蹤其他使用者
    - 不能追蹤自己
    - 再次點擊取消追蹤
    - 返回 JSON 格式的響應
    """
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '無效的請求方法'}, status=405)

    target_user = get_object_or_404(User, username=username)

    # 檢查是否為自己
    if target_user == request.user:
        return JsonResponse({
            'success': False,
            'error': '不能追蹤自己'
        }, status=403)

    # 檢查是否已經追蹤
    follow_exists = Follow.objects.filter(follower=request.user, following=target_user).first()

    if follow_exists:
        # 取消追蹤
        follow_exists.delete()
        is_following = False
        message = '已取消追蹤'
    else:
        # 新增追蹤
        Follow.objects.create(follower=request.user, following=target_user)
        is_following = True
        message = '追蹤成功'

        # 發送通知給被追蹤的用戶
        notify_follower(target_user, request.user)

    # 獲取最新的追蹤數量
    followers_count = target_user.followers.count()
    following_count = target_user.following.count()

    return JsonResponse({
        'success': True,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'message': message
    })


def member_articles(request, username):
    """查看會員發表的所有文章"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 取得該用戶的所有文章（公開發表的）
    articles_list = Article.objects.filter(author=target_user).order_by('-created_at')

    # 分頁設定
    paginator = Paginator(articles_list, 10)  # 每頁顯示 10 篇
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
    }

    context = {
        'member': member_data,
        'is_own_profile': is_own_profile,
        'articles': page_obj,
        'page_obj': page_obj,
        'total_count': articles_list.count(),
    }

    return render(request, 'blog/members/articles.html', context)


def member_comments(request, username):
    """查看會員的所有評論"""
    target_user = get_object_or_404(User, username=username)

    # 判斷是否為本人
    is_own_profile = request.user.is_authenticated and request.user == target_user

    # 取得該用戶的所有評論，並預載相關的文章資料
    comments_list = Comment.objects.filter(
        author=target_user
    ).select_related('article', 'article__author').order_by('-created_at')

    # 分頁設定
    paginator = Paginator(comments_list, 15)  # 每頁顯示 15 條評論
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
    }

    context = {
        'member': member_data,
        'is_own_profile': is_own_profile,
        'comments': page_obj,
        'page_obj': page_obj,
        'total_count': comments_list.count(),
    }

    return render(request, 'blog/members/comments.html', context)


def get_user_api(request, username):
    """
    API: 獲取用戶基本資訊（用於即時聊天）
    """
    from django.http import JsonResponse

    try:
        user = User.objects.get(username=username)
        profile = user.profile

        # 獲取顯示名稱
        display_name = user.first_name if user.first_name else user.username

        # 獲取頭像 URL
        if profile.avatar:
            avatar_url = profile.get_avatar_url()
        else:
            from django.templatetags.static import static
            avatar_url = static('blog/images/大頭綠.JPG')

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'display_name': display_name,
                'avatar_url': request.build_absolute_uri(avatar_url) if avatar_url else None
            }
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': '用戶不存在'
        }, status=404)


@login_required
def get_chat_list_api(request):
    """
    API: 獲取即時聊天列表
    返回所有聊天對話，包含最後訊息、未讀數等資訊
    """
    from django.http import JsonResponse
    from django.db.models import Q, Max, Count, Case, When, IntegerField
    from ..models import ChatMessage

    # 獲取所有與當前用戶相關的聊天訊息
    # 找出所有與用戶有聊天記錄的其他用戶
    chat_users = ChatMessage.objects.filter(
        Q(sender=request.user) | Q(recipient=request.user)
    ).values_list('sender', 'recipient').distinct()

    # 提取所有唯一的對話用戶 ID
    user_ids = set()
    for sender_id, recipient_id in chat_users:
        if sender_id != request.user.id:
            user_ids.add(sender_id)
        if recipient_id != request.user.id:
            user_ids.add(recipient_id)

    # 獲取每個用戶的聊天資訊
    chat_list = []
    for user_id in user_ids:
        other_user = User.objects.get(id=user_id)

        # 獲取最後一則訊息
        last_message = ChatMessage.objects.filter(
            Q(sender=request.user, recipient=other_user) |
            Q(sender=other_user, recipient=request.user)
        ).order_by('-created_at').first()

        # 獲取未讀訊息數
        unread_count = ChatMessage.objects.filter(
            sender=other_user,
            recipient=request.user,
            is_read=False
        ).count()

        # 獲取顯示名稱
        display_name = other_user.first_name if other_user.first_name else other_user.username

        # 獲取頭像 URL
        try:
            profile = other_user.profile
            if profile.avatar:
                avatar_url = profile.get_avatar_url()
            else:
                from django.templatetags.static import static
                avatar_url = static('blog/images/大頭綠.JPG')
        except:
            from django.templatetags.static import static
            avatar_url = static('blog/images/大頭綠.JPG')

        chat_list.append({
            'user_id': other_user.id,
            'username': other_user.username,
            'display_name': display_name,
            'avatar_url': request.build_absolute_uri(avatar_url) if avatar_url else None,
            'last_message': {
                'content': last_message.content if last_message else '',
                'timestamp': last_message.created_at.isoformat() if last_message else None,
                'is_from_me': last_message.sender == request.user if last_message else False
            },
            'unread_count': unread_count
        })

    # 按最後訊息時間排序（最新的在前面）
    chat_list.sort(key=lambda x: x['last_message']['timestamp'] or '', reverse=True)

    return JsonResponse({
        'success': True,
        'chats': chat_list,
        'total': len(chat_list)
    })


@login_required
def subscribe_push(request):
    """
    API: 訂閱 Web Push 推播通知
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '僅支援 POST 請求'}, status=405)

    try:
        data = json.loads(request.body)
        subscription_data = data.get('subscription')

        if not subscription_data:
            return JsonResponse({'success': False, 'error': '缺少訂閱資料'}, status=400)

        from ..models import PushSubscription

        # 提取訂閱資訊
        endpoint = subscription_data.get('endpoint')
        keys = subscription_data.get('keys', {})
        p256dh = keys.get('p256dh')
        auth = keys.get('auth')

        if not all([endpoint, p256dh, auth]):
            return JsonResponse({'success': False, 'error': '訂閱資料不完整'}, status=400)

        # 獲取或創建訂閱
        subscription, created = PushSubscription.objects.update_or_create(
            endpoint=endpoint,
            defaults={
                'user': request.user,
                'p256dh': p256dh,
                'auth': auth,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'is_active': True,
                'failure_count': 0
            }
        )

        # 檢測裝置類型
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
            subscription.device_type = 'mobile'
        elif 'tablet' in user_agent or 'ipad' in user_agent:
            subscription.device_type = 'tablet'
        else:
            subscription.device_type = 'desktop'
        subscription.save()

        return JsonResponse({
            'success': True,
            'message': '訂閱成功' if created else '訂閱已更新',
            'created': created
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '無效的 JSON 資料'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def unsubscribe_push(request):
    """
    API: 取消訂閱 Web Push 推播通知
    """
    from django.http import JsonResponse
    import json

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': '僅支援 POST 請求'}, status=405)

    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')

        if not endpoint:
            return JsonResponse({'success': False, 'error': '缺少端點資訊'}, status=400)

        from ..models import PushSubscription

        # 刪除訂閱
        deleted_count, _ = PushSubscription.objects.filter(
            user=request.user,
            endpoint=endpoint
        ).delete()

        if deleted_count > 0:
            return JsonResponse({
                'success': True,
                'message': '取消訂閱成功'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': '找不到對應的訂閱'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': '無效的 JSON 資料'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def test_push_notification_view(request):
    """
    API: 測試推播通知
    """
    from django.http import JsonResponse
    from ..utils.push_notifications import test_push_notification

    result = test_push_notification(request.user)

    if result['success'] > 0:
        return JsonResponse({
            'success': True,
            'message': f'測試通知已發送到 {result["success"]} 個裝置'
        })
    else:
        return JsonResponse({
            'success': False,
            'message': '沒有可用的訂閱或發送失敗',
            'result': result
        })
