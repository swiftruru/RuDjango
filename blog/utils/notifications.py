"""
通知系統工具函數
用於在各種事件發生時創建通知
"""
from django.contrib.contenttypes.models import ContentType
from blog.models import Notification, NotificationPreference
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone


def create_notification(user, notification_type, message, sender=None, link='', content_object=None):
    """
    創建通知的統一接口

    Args:
        user: 接收通知的用戶
        notification_type: 通知類型 (comment, like, follower, message, share)
        message: 通知訊息
        sender: 觸發通知的用戶 (可選)
        link: 相關連結 (可選)
        content_object: 相關物件 (可選，使用 GenericForeignKey)

    Returns:
        Notification 物件或 None (如果用戶停用了該類型通知)
    """
    # 檢查用戶是否啟用該類型通知
    preference = NotificationPreference.get_or_create_for_user(user)

    if not preference.is_notification_enabled(notification_type):
        return None

    # 避免自己通知自己
    if sender and sender == user:
        return None

    # 創建通知
    notification_data = {
        'user': user,
        'sender': sender,
        'notification_type': notification_type,
        'message': message,
        'link': link,
    }

    # 如果有相關物件，設置 GenericForeignKey
    if content_object:
        notification_data['content_type'] = ContentType.objects.get_for_model(content_object)
        notification_data['object_id'] = content_object.id

    notification = Notification.objects.create(**notification_data)

    # Send real-time notification via WebSocket
    send_realtime_notification(user, notification)

    return notification


def send_realtime_notification(user, notification):
    """
    Send real-time notification to user via WebSocket

    Args:
        user: The user to send notification to
        notification: The notification object
    """
    channel_layer = get_channel_layer()

    # Get notification type icon
    notification_icons = {
        'comment': '💬',
        'like': '❤️',
        'follower': '👤',
        'message': '✉️',
        'share': '🔗',
        'mention': '@',
    }

    # Prepare notification data
    notification_data = {
        'id': notification.id,
        'message': notification.message,
        'notification_type': notification.notification_type,
        'link': notification.link,
        'icon': notification_icons.get(notification.notification_type, '🔔'),
        'time_since': notification.get_time_since(),
        'created_at': notification.created_at.isoformat(),
    }

    # Send to user's notification group
    group_name = f'notifications_{user.id}'

    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_message',
                'notification': notification_data
            }
        )

        # Also send updated count
        unread_count = Notification.objects.filter(user=user, is_read=False).count()

        # Get unread message count
        from blog.models import Message
        unread_messages = Message.objects.filter(recipient=user, is_read=False).count()

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'notification_count',
                'unread_count': unread_count,
                'unread_messages_count': unread_messages
            }
        )
    except Exception as e:
        # If channel layer is not available, fail silently
        # This allows the system to work without WebSocket
        print(f"Failed to send WebSocket notification: {e}")
        pass


def notify_comment(article, comment):
    """
    當有人留言時通知文章作者

    Args:
        article: 被留言的文章
        comment: 留言物件
    """
    # 通知文章作者（如果留言者不是作者自己）
    if comment.author != article.author:
        message = f"{comment.author.username} 在您的文章「{article.title}」中留言"
        link = f"/blog/article/{article.id}/#comment-{comment.id}"

        create_notification(
            user=article.author,
            notification_type='comment',
            message=message,
            sender=comment.author,
            link=link,
            content_object=comment
        )


def notify_like(article, user):
    """
    當有人按讚時通知文章作者

    Args:
        article: 被按讚的文章
        user: 按讚的用戶
    """
    if user != article.author:
        message = f"{user.username} 讚了您的文章「{article.title}」"
        link = f"/blog/article/{article.id}/"

        create_notification(
            user=article.author,
            notification_type='like',
            message=message,
            sender=user,
            link=link,
            content_object=article
        )


def notify_follower(followed_user, follower):
    """
    當有人追蹤時通知被追蹤者

    Args:
        followed_user: 被追蹤的用戶
        follower: 追蹤者
    """
    message = f"{follower.username} 開始追蹤您"
    link = f"/blog/member/{follower.username}/"

    create_notification(
        user=followed_user,
        notification_type='follower',
        message=message,
        sender=follower,
        link=link
    )


def notify_message(recipient, sender, message_obj):
    """
    當收到私訊時通知接收者

    Args:
        recipient: 接收訊息的用戶
        sender: 發送訊息的用戶
        message_obj: 訊息物件
    """
    message = f"{sender.username} 發送了一則訊息給您"
    link = f"/blog/messages/{message_obj.id}/"

    return create_notification(
        user=recipient,
        notification_type='message',
        message=message,
        sender=sender,
        link=link,
        content_object=message_obj
    )


def notify_share(article, user):
    """
    當有人分享文章時通知作者

    Args:
        article: 被分享的文章
        user: 分享者
    """
    if user != article.author:
        message = f"{user.username} 分享了您的文章「{article.title}」"
        link = f"/blog/article/{article.id}/"

        create_notification(
            user=article.author,
            notification_type='share',
            message=message,
            sender=user,
            link=link,
            content_object=article
        )


def notify_mention(mentioned_user, mentioning_user, content_type, content_object, article):
    """
    當有人提及使用者時發送通知

    Args:
        mentioned_user: 被提及的使用者
        mentioning_user: 提及者
        content_type: 提及的內容類型 ('article' 或 'comment')
        content_object: 提及的內容物件（Article 或 Comment）
        article: 相關的文章
    """
    # 不通知自己
    if mentioned_user == mentioning_user:
        return None

    # 根據內容類型產生訊息和連結
    if content_type == 'article':
        message = f"{mentioning_user.username} 在文章「{article.title}」中提及了您"
        link = f"/blog/article/{article.id}/"
    elif content_type == 'comment':
        message = f"{mentioning_user.username} 在文章「{article.title}」的留言中提及了您"
        link = f"/blog/article/{article.id}/#comment-{content_object.id}"
    else:
        return None

    return create_notification(
        user=mentioned_user,
        notification_type='mention',
        message=message,
        sender=mentioning_user,
        link=link,
        content_object=content_object
    )
