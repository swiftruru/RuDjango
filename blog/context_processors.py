"""
自訂 Context Processor
在所有模板中提供額外的 context 變數
"""


def user_display_name(request):
    """
    提供使用者的顯示名稱
    優先使用暱稱 (first_name)，沒有則使用用戶名
    """
    if request.user.is_authenticated:
        display_name = request.user.first_name or request.user.username
    else:
        display_name = ''
    
    return {
        'user_display_name': display_name
    }
