"""
通知系統相關 views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone

from blog.models import Notification, NotificationPreference


@login_required
def notifications_center(request):
    """
    通知中心
    顯示所有通知，支援已讀/未讀篩選
    """
    # 取得篩選參數
    filter_type = request.GET.get('filter', 'all')  # all, unread, read
    notification_type = request.GET.get('type', 'all')  # all, comment, like, follower, message, share

    # 基本查詢
    notifications = Notification.objects.filter(user=request.user)

    # 篩選狀態
    if filter_type == 'unread':
        notifications = notifications.filter(is_read=False)
    elif filter_type == 'read':
        notifications = notifications.filter(is_read=True)

    # 篩選通知類型
    if notification_type != 'all':
        notifications = notifications.filter(notification_type=notification_type)

    # 分頁
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # 統計數據
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'page_obj': page_obj,
        'notifications': page_obj,
        'filter_type': filter_type,
        'notification_type': notification_type,
        'unread_count': unread_count,
    }

    return render(request, 'blog/notifications/center.html', context)


@login_required
def notification_mark_read(request, notification_id):
    """
    標記單一通知為已讀
    """
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()

    # 如果是 AJAX 請求，返回 JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': '已標記為已讀',
            'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
        })

    # 否則重導向到通知中心
    return redirect('notifications_center')


@login_required
def notification_mark_all_read(request):
    """
    標記所有通知為已讀
    """
    if request.method == 'POST':
        updated_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).update(is_read=True, read_at=timezone.now())

        # 如果是 AJAX 請求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'已將 {updated_count} 則通知標記為已讀',
                'updated_count': updated_count,
                'unread_count': 0
            })

        return redirect('notifications_center')

    return redirect('notifications_center')


@login_required
def notification_delete(request, notification_id):
    """
    刪除單一通知
    """
    if request.method == 'POST':
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.delete()

        # 如果是 AJAX 請求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '通知已刪除',
                'unread_count': Notification.objects.filter(user=request.user, is_read=False).count()
            })

        return redirect('notifications_center')

    return redirect('notifications_center')


@login_required
def notification_delete_all_read(request):
    """
    刪除所有已讀通知
    """
    if request.method == 'POST':
        deleted_count = Notification.objects.filter(
            user=request.user,
            is_read=True
        ).delete()[0]

        # 如果是 AJAX 請求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'已刪除 {deleted_count} 則已讀通知',
                'deleted_count': deleted_count
            })

        return redirect('notifications_center')

    return redirect('notifications_center')


@login_required
def notification_count(request):
    """
    取得未讀通知數量和未讀訊息數量（API）
    用於即時更新導航欄的通知和訊息圖示
    """
    from blog.models import Message

    # 未讀通知數量
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    # 未讀訊息數量
    unread_messages_count = Message.objects.filter(
        recipient=request.user,
        is_read=False,
        recipient_deleted=False
    ).count()

    # 取得最近的未讀通知（最多 5 則）
    recent_notifications = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).order_by('-created_at')[:5]

    notifications_data = []
    for notification in recent_notifications:
        notifications_data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'icon': notification.get_icon(),
            'message': notification.message,
            'link': notification.link,
            'time_since': notification.get_time_since(),
            'created_at': notification.created_at.isoformat(),
        })

    return JsonResponse({
        'success': True,
        'unread_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count,
        'recent_notifications': notifications_data
    })


@login_required
def notification_preferences(request):
    """
    通知偏好設定頁面
    """
    # 取得或建立用戶的通知偏好
    preference = NotificationPreference.get_or_create_for_user(request.user)

    if request.method == 'POST':
        # 更新偏好設定
        preference.enable_comment_notifications = request.POST.get('enable_comment_notifications') == 'on'
        preference.enable_like_notifications = request.POST.get('enable_like_notifications') == 'on'
        preference.enable_follower_notifications = request.POST.get('enable_follower_notifications') == 'on'
        preference.enable_message_notifications = request.POST.get('enable_message_notifications') == 'on'
        preference.enable_share_notifications = request.POST.get('enable_share_notifications') == 'on'
        preference.enable_email_notifications = request.POST.get('enable_email_notifications') == 'on'
        preference.save()

        # 如果是 AJAX 請求，返回 JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': '通知設定已更新'
            })

        return redirect('notification_preferences')

    context = {
        'preference': preference
    }

    return render(request, 'blog/notifications/preferences.html', context)
