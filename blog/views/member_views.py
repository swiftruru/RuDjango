"""
會員相關的視圖函數
處理會員中心、個人資料、會員列表等功能
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from ..forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from ..models import UserProfile, Activity, UserAchievement, UserCourseProgress, Follow


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
    stats = {
        'posts': target_user.articles.count(),
        'comments': 0,
        'likes_received': 0,
        'followers': target_user.followers.count(),
        'following': target_user.following.count(),
        'projects': 0,
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
    learning_progress = []
    if is_own_profile:
        learning_progress = UserCourseProgress.objects.filter(user=target_user).select_related('course').order_by('-last_activity')[:3]

    # 取得最近發表的文章（公開，所有人都能看到）
    recent_articles = target_user.articles.order_by('-created_at')[:5]

    # 準備會員資料
    member_data = {
        'name': target_user.first_name or target_user.username,
        'username': target_user.username,
        'email': target_user.email if is_own_profile else '',  # 只有本人能看到 email
        'school': profile.school,
        'grade': profile.grade,
        'bio': profile.bio,
        'location': profile.location,
        'birthday': profile.birthday if is_own_profile else None,  # 只有本人能看到生日
        'joined_date': target_user.date_joined.strftime('%Y-%m-%d'),
        'level': profile.level,
        'points': profile.points,
        'next_level_points': profile.get_next_level_points(),
        'stats': stats,
        'recent_activities': recent_activities,
        'skills': user_skills,
        'achievements': user_achievements,
        'learning_progress': learning_progress,
        'recent_articles': recent_articles,
    }

    context = {
        'member': member_data,
        'is_own_profile': is_own_profile,
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
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # 使用暱稱（first_name）顯示，如果沒有則顯示帳號名
                display_name = user.first_name if user.first_name else username
                messages.success(request, f'✅ 歡迎回來，{display_name}！')
                # 重定向到 next 參數指定的頁面，或預設到部落格首頁
                next_url = request.GET.get('next', '/blog/')
                return redirect(next_url)
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