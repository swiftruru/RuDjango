"""
Web Push 推播通知工具函數
"""

import json
import logging
from typing import Optional, Dict, List
from django.conf import settings
from pywebpush import webpush, WebPushException

logger = logging.getLogger(__name__)


def send_push_notification(
    user,
    title: str,
    body: str,
    url: str = '/blog/notifications/',
    icon: str = '/static/blog/images/icons/icon-192x192.png',
    badge: str = '/static/blog/images/icons/badge-72x72.png',
    tag: Optional[str] = None,
    require_interaction: bool = False,
    actions: Optional[List[Dict]] = None
) -> Dict[str, int]:
    """
    發送推播通知給指定用戶的所有裝置

    Args:
        user: Django User 物件
        title: 通知標題
        body: 通知內容
        url: 點擊通知後導向的 URL
        icon: 通知圖示
        badge: 通知徽章
        tag: 通知標籤（用於分組/替換）
        require_interaction: 是否需要用戶互動才關閉
        actions: 通知操作按鈕列表

    Returns:
        Dict[str, int]: {'success': 成功數, 'failed': 失敗數}
    """
    from ..models import PushSubscription

    # 獲取用戶的所有啟用訂閱
    subscriptions = PushSubscription.objects.filter(
        user=user,
        is_active=True
    )

    if not subscriptions.exists():
        logger.info(f'User {user.username} has no active push subscriptions')
        return {'success': 0, 'failed': 0}

    # 準備推播資料
    notification_data = {
        'title': title,
        'body': body,
        'icon': icon,
        'badge': badge,
        'tag': tag or 'notification',
        'requireInteraction': require_interaction,
        'data': {
            'url': url
        }
    }

    # 添加操作按鈕
    if actions:
        notification_data['actions'] = actions

    # 統計結果
    success_count = 0
    failed_count = 0

    # 發送給每個訂閱
    for subscription in subscriptions:
        try:
            result = _send_to_subscription(subscription, notification_data)
            if result:
                success_count += 1
                subscription.mark_as_used()
                subscription.reset_failures()
            else:
                failed_count += 1
                subscription.mark_as_failed()
        except Exception as e:
            logger.error(f'Failed to send push to subscription {subscription.id}: {e}')
            failed_count += 1
            subscription.mark_as_failed()

    logger.info(f'Push notification sent to {user.username}: {success_count} success, {failed_count} failed')

    return {
        'success': success_count,
        'failed': failed_count
    }


def send_push_to_multiple_users(
    users: List,
    title: str,
    body: str,
    url: str = '/blog/notifications/',
    **kwargs
) -> Dict[str, int]:
    """
    發送推播通知給多個用戶

    Args:
        users: Django User 物件列表
        title: 通知標題
        body: 通知內容
        url: 點擊通知後導向的 URL
        **kwargs: 其他推播參數

    Returns:
        Dict[str, int]: {'success': 總成功數, 'failed': 總失敗數}
    """
    total_success = 0
    total_failed = 0

    for user in users:
        result = send_push_notification(user, title, body, url, **kwargs)
        total_success += result['success']
        total_failed += result['failed']

    return {
        'success': total_success,
        'failed': total_failed
    }


def _send_to_subscription(subscription, notification_data: Dict) -> bool:
    """
    發送推播到單一訂閱

    Args:
        subscription: PushSubscription 物件
        notification_data: 通知資料

    Returns:
        bool: 是否成功
    """
    try:
        # 準備訂閱資訊
        subscription_info = {
            'endpoint': subscription.endpoint,
            'keys': {
                'p256dh': subscription.p256dh,
                'auth': subscription.auth
            }
        }

        # 準備 VAPID Claims
        vapid_claims = {
            "sub": settings.VAPID_CLAIMS.get('sub', 'mailto:admin@example.com')
        }

        # 發送推播
        response = webpush(
            subscription_info=subscription_info,
            data=json.dumps(notification_data),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims=vapid_claims
        )

        return response.status_code in [200, 201]

    except WebPushException as e:
        logger.error(f'WebPush exception: {e}')

        # 410 Gone 或 404 Not Found 表示訂閱已失效
        if e.response and e.response.status_code in [410, 404]:
            subscription.is_active = False
            subscription.save()

        return False

    except Exception as e:
        logger.error(f'Error sending push: {e}')
        return False


def create_notification_with_push(
    user,
    notification_type: str,
    message: str,
    link: str,
    **push_kwargs
):
    """
    創建通知並發送推播
    整合現有的通知系統

    Args:
        user: Django User 物件
        notification_type: 通知類型
        message: 通知訊息
        link: 通知連結
        **push_kwargs: 額外的推播參數
    """
    from ..utils.notifications import create_notification
    from ..models import NotificationPreference

    # 創建資料庫通知
    notification = create_notification(
        user=user,
        notification_type=notification_type,
        message=message,
        link=link
    )

    # 檢查用戶是否啟用推播通知
    try:
        preference = NotificationPreference.objects.get(user=user)
        push_enabled = getattr(preference, f'{notification_type}_push_enabled', False)
    except NotificationPreference.DoesNotExist:
        push_enabled = True  # 預設啟用

    # 如果用戶啟用推播，發送推播通知
    if push_enabled:
        # 準備推播標題
        title_map = {
            'comment': '新評論',
            'like': '新讚',
            'follow': '新粉絲',
            'message': '新訊息',
            'share': '文章被分享',
            'mention': '提到你',
        }
        title = push_kwargs.get('title', title_map.get(notification_type, '新通知'))

        send_push_notification(
            user=user,
            title=title,
            body=message,
            url=link,
            tag=notification_type,
            **push_kwargs
        )

    return notification


def test_push_notification(user):
    """
    測試推播通知

    Args:
        user: Django User 物件

    Returns:
        Dict: 測試結果
    """
    return send_push_notification(
        user=user,
        title='測試推播通知',
        body='如果您看到此通知，表示推播功能正常運作！',
        url='/blog/notifications/',
        tag='test'
    )
