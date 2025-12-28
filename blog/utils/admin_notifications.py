"""
後台管理通知工具函數
提供創建各種後台管理通知的便捷方法
"""
from django.contrib.auth.models import User
from blog.models import Notification


def create_user_report_notification(admin_users, reporter, reported_content, report_reason):
    """
    創建用戶舉報通知

    Args:
        admin_users: 要接收通知的管理員列表
        reporter: 舉報者
        reported_content: 被舉報的內容（文章、留言等）
        report_reason: 舉報原因
    """
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            sender=reporter,
            notification_type='user_report',
            message=f"用戶 {reporter.username} 舉報了內容：{report_reason}",
            link=f"/admin/dashboard/reports/",  # 可以調整為實際的舉報詳情頁面
        )


def create_system_warning_notification(admin_users, warning_message, link=''):
    """
    創建系統警告通知

    Args:
        admin_users: 要接收通知的管理員列表
        warning_message: 警告訊息
        link: 相關連結（可選）
    """
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type='system_warning',
            message=warning_message,
            link=link,
        )


def create_data_change_notification(admin_users, change_description, link=''):
    """
    創建數據異動通知

    Args:
        admin_users: 要接收通知的管理員列表
        change_description: 異動描述
        link: 相關連結（可選）
    """
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type='data_change',
            message=change_description,
            link=link,
        )


def create_security_alert_notification(admin_users, alert_message, link=''):
    """
    創建安全警報通知

    Args:
        admin_users: 要接收通知的管理員列表
        alert_message: 警報訊息
        link: 相關連結（可選）
    """
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type='security_alert',
            message=alert_message,
            link=link,
        )


def create_system_error_notification(admin_users, error_message, link=''):
    """
    創建系統錯誤通知

    Args:
        admin_users: 要接收通知的管理員列表
        error_message: 錯誤訊息
        link: 相關連結（可選）
    """
    for admin in admin_users:
        Notification.objects.create(
            user=admin,
            notification_type='system_error',
            message=error_message,
            link=link,
        )


def get_all_admin_users():
    """
    獲取所有管理員用戶

    Returns:
        QuerySet of User objects with is_staff=True
    """
    return User.objects.filter(is_staff=True, is_active=True)


def get_superusers():
    """
    獲取所有超級管理員

    Returns:
        QuerySet of User objects with is_superuser=True
    """
    return User.objects.filter(is_superuser=True, is_active=True)


# 使用範例：
#
# from blog.utils.admin_notifications import (
#     create_user_report_notification,
#     create_system_warning_notification,
#     create_security_alert_notification,
#     get_all_admin_users
# )
#
# # 創建用戶舉報通知
# admins = get_all_admin_users()
# create_user_report_notification(
#     admin_users=admins,
#     reporter=request.user,
#     reported_content="不當文章標題",
#     report_reason="包含不當內容"
# )
#
# # 創建系統警告通知
# create_system_warning_notification(
#     admin_users=admins,
#     warning_message="資料庫連接異常，已自動切換至備用連接",
#     link="/admin/dashboard/system/database/"
# )
#
# # 創建安全警報通知
# superusers = get_superusers()
# create_security_alert_notification(
#     admin_users=superusers,
#     alert_message="偵測到異常登入嘗試：IP 192.168.1.100 在5分鐘內嘗試登入失敗20次",
#     link="/admin/dashboard/security/login-attempts/"
# )
