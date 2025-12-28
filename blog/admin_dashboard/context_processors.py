"""
Admin Dashboard Context Processors
提供給所有後台模板使用的全域變數
"""
from blog.models import Notification


def admin_notifications(request):
    """
    為管理後台提供系統通知相關的 context 變數
    只顯示後台管理專屬的通知（用戶舉報、系統警告、數據異動、安全警報、系統錯誤）
    """
    if request.user.is_authenticated and request.user.is_staff:
        # 後台管理專屬通知類型
        admin_notification_types = ['user_report', 'system_warning', 'data_change', 'security_alert', 'system_error']

        # 獲取未讀管理通知數量
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False,
            notification_type__in=admin_notification_types
        ).count()

        # 獲取最近5條管理通知
        recent_notifications = Notification.objects.filter(
            user=request.user,
            notification_type__in=admin_notification_types
        ).order_by('-created_at')[:5]

        return {
            'admin_unread_notifications_count': unread_count,
            'admin_recent_notifications': recent_notifications,
        }

    return {
        'admin_unread_notifications_count': 0,
        'admin_recent_notifications': [],
    }
