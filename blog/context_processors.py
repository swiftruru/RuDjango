"""
自訂 Context Processor
在所有模板中提供額外的 context 變數
"""
from django.conf import settings
from .version import get_version_info
from .models import Message


def user_display_name(request):
    """
    提供使用者的顯示名稱
    優先使用暱稱 (first_name)，沒有則使用用戶名
    """
    if request.user.is_authenticated:
        # 優先使用 first_name (暱稱)
        # 如果 first_name 為空字串或 None，則使用 username
        display_name = (request.user.first_name.strip() if request.user.first_name else '') or request.user.username
    else:
        display_name = ''
    
    return {
        'user_display_name': display_name
    }


def version_context(request):
    """將系統版本資訊加入所有模板的 context"""
    return {
        'system_version': get_version_info()
    }


def unread_messages(request):
    """
    提供未讀訊息數量
    """
    if request.user.is_authenticated:
        unread_count = Message.objects.filter(
            recipient=request.user,
            is_read=False,
            recipient_deleted=False
        ).count()
    else:
        unread_count = 0

    return {
        'unread_message_count': unread_count
    }


def vapid_public_key(request):
    """
    提供 VAPID 公鑰給前端 Web Push 使用
    """
    return {
        'VAPID_PUBLIC_KEY': settings.VAPID_PUBLIC_KEY
    }
