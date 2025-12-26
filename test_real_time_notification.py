#!/usr/bin/env python
"""
測試即時通知功能
在另一個瀏覽器視窗登入不同帳號，執行此腳本創建通知
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.utils.notifications import create_notification

def main():
    print("=== 即時通知測試腳本 ===\n")

    # 獲取所有用戶
    users = User.objects.all()
    print("可用的使用者：")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user.username} (ID: {user.id})")

    # 選擇接收通知的使用者
    recipient_index = input("\n請選擇接收通知的使用者編號: ")
    try:
        recipient = users[int(recipient_index) - 1]
    except (ValueError, IndexError):
        print("無效的選擇！")
        return

    # 選擇發送者（可選）
    use_sender = input("是否指定發送者？(y/n): ").lower() == 'y'
    sender = None
    if use_sender:
        sender_index = input("請選擇發送者編號: ")
        try:
            sender = users[int(sender_index) - 1]
        except (ValueError, IndexError):
            print("無效的選擇！使用匿名發送者")

    # 選擇通知類型
    print("\n通知類型：")
    print("1. 留言 (comment)")
    print("2. 按讚 (like)")
    print("3. 追蹤 (follower)")
    print("4. 私訊 (message)")
    print("5. 分享 (share)")
    print("6. 提及 (mention)")

    type_choice = input("請選擇通知類型編號: ")
    type_map = {
        '1': 'comment',
        '2': 'like',
        '3': 'follower',
        '4': 'message',
        '5': 'share',
        '6': 'mention'
    }
    notification_type = type_map.get(type_choice, 'comment')

    # 輸入訊息
    message = input("請輸入通知訊息: ")

    # 輸入連結（可選）
    link = input("請輸入通知連結（可選，直接按 Enter 跳過）: ") or ''

    # 創建通知
    notification = create_notification(
        user=recipient,
        notification_type=notification_type,
        message=message,
        sender=sender,
        link=link
    )

    if notification:
        print(f"\n✅ 通知創建成功！")
        print(f"接收者: {recipient.username}")
        print(f"發送者: {sender.username if sender else '系統'}")
        print(f"類型: {notification_type}")
        print(f"訊息: {message}")
        print(f"連結: {link or '無'}")
        print(f"\n提示：{recipient.username} 的瀏覽器應該在 10 秒內收到即時通知！")
    else:
        print("\n❌ 通知創建失敗（可能該使用者已停用此類型通知）")

if __name__ == '__main__':
    main()
