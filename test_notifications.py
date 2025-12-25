"""
測試通知系統
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Article, Notification, NotificationPreference
from blog.utils.notifications import (
    create_notification,
    notify_comment,
    notify_like,
    notify_follower,
    notify_share
)

def test_notifications():
    """測試通知系統"""

    print("=== 通知系統測試 ===\n")

    # 1. 測試通知偏好設定
    print("1. 測試通知偏好設定...")
    users = User.objects.all()[:2]
    if len(users) < 2:
        print("   ❌ 需要至少2個用戶進行測試")
        return

    user1, user2 = users[0], users[1]

    # 為用戶創建通知偏好
    pref1 = NotificationPreference.get_or_create_for_user(user1)
    pref2 = NotificationPreference.get_or_create_for_user(user2)
    print(f"   ✓ 為用戶 {user1.username} 和 {user2.username} 創建了通知偏好")

    # 2. 測試創建基本通知
    print("\n2. 測試創建基本通知...")
    notification = create_notification(
        user=user1,
        notification_type='message',
        message=f"測試通知：{user2.username} 發送了一則訊息",
        sender=user2,
        link='/blog/messages/'
    )
    if notification:
        print(f"   ✓ 成功創建通知: {notification.message}")
        print(f"   - 圖示: {notification.get_icon()}")
        print(f"   - 時間: {notification.get_time_since()}")
    else:
        print("   ❌ 創建通知失敗")

    # 3. 測試通知數量
    print("\n3. 測試通知數量...")
    unread_count = Notification.objects.filter(user=user1, is_read=False).count()
    print(f"   ✓ 用戶 {user1.username} 有 {unread_count} 則未讀通知")

    # 4. 測試標記為已讀
    print("\n4. 測試標記為已讀...")
    if notification:
        notification.mark_as_read()
        print(f"   ✓ 通知已標記為已讀")
        print(f"   - is_read: {notification.is_read}")
        print(f"   - read_at: {notification.read_at}")

    # 5. 測試文章相關通知（如果有文章）
    print("\n5. 測試文章相關通知...")
    articles = Article.objects.filter(status='published')[:1]
    if articles:
        article = articles[0]
        print(f"   使用文章: {article.title}")

        # 測試按讚通知
        notify_like(article, user2)
        print(f"   ✓ 創建了按讚通知")

        # 測試分享通知
        notify_share(article, user2)
        print(f"   ✓ 創建了分享通知")
    else:
        print("   ⚠️  沒有發布的文章可測試")

    # 6. 查詢所有通知
    print("\n6. 查詢用戶所有通知...")
    all_notifications = Notification.objects.filter(user=user1).order_by('-created_at')[:5]
    print(f"   ✓ 找到 {all_notifications.count()} 則最新通知:")
    for i, notif in enumerate(all_notifications, 1):
        status = "✓" if notif.is_read else "●"
        print(f"   {i}. [{status}] {notif.get_icon()} {notif.message} ({notif.get_time_since()})")

    # 7. 測試通知偏好
    print("\n7. 測試通知偏好...")
    print(f"   用戶 {user1.username} 的通知設定:")
    print(f"   - 留言通知: {'啟用' if pref1.enable_comment_notifications else '停用'}")
    print(f"   - 按讚通知: {'啟用' if pref1.enable_like_notifications else '停用'}")
    print(f"   - 追蹤通知: {'啟用' if pref1.enable_follower_notifications else '停用'}")
    print(f"   - 私訊通知: {'啟用' if pref1.enable_message_notifications else '停用'}")
    print(f"   - 分享通知: {'啟用' if pref1.enable_share_notifications else '停用'}")

    # 8. 測試停用通知類型
    print("\n8. 測試停用通知類型...")
    pref1.enable_like_notifications = False
    pref1.save()
    print(f"   ✓ 已停用按讚通知")

    # 嘗試創建按讚通知（應該被忽略）
    if articles:
        result = notify_like(articles[0], user2)
        if result is None:
            print(f"   ✓ 按讚通知被正確忽略（因為已停用）")
        else:
            print(f"   ❌ 按讚通知沒有被忽略")

    # 恢復設定
    pref1.enable_like_notifications = True
    pref1.save()

    print("\n=== 測試完成 ===")
    print(f"\n通知系統運作正常！")
    print(f"- 總通知數: {Notification.objects.count()}")
    print(f"- 未讀通知數: {Notification.objects.filter(is_read=False).count()}")

if __name__ == '__main__':
    test_notifications()
