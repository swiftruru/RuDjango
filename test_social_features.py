"""
社群互動功能測試腳本
用於快速測試新功能是否正常運作
"""

import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import (
    Article, UserGroup, GroupMembership, Event,
    EventParticipant, Mention
)
from blog.utils.mention_parser import (
    parse_mentions,
    create_mentions_from_article,
    highlight_mentions
)
from django.utils import timezone
from datetime import timedelta


def test_mention_parsing():
    """測試 @提及解析功能"""
    print("\n=== 測試 @提及解析 ===")

    text = "Hello @john, 這是給 @jane 和 @bob 的訊息！"
    mentions = parse_mentions(text)
    print(f"輸入文字: {text}")
    print(f"解析結果: {mentions}")
    print(f"✅ 成功解析 {len(mentions)} 個提及")

    # 測試高亮功能
    highlighted = highlight_mentions(text)
    print(f"高亮結果: {highlighted}")


def test_mention_creation():
    """測試提及記錄建立"""
    print("\n=== 測試提及記錄建立 ===")

    # 建立測試使用者（如果不存在）
    try:
        author = User.objects.get(username='testauthor')
    except User.DoesNotExist:
        author = User.objects.create_user(
            username='testauthor',
            password='testpass123'
        )
        print("✅ 建立測試作者")

    try:
        mentioned_user = User.objects.get(username='john')
    except User.DoesNotExist:
        mentioned_user = User.objects.create_user(
            username='john',
            password='testpass123'
        )
        print("✅ 建立測試使用者 john")

    # 建立測試文章
    article = Article.objects.create(
        title='測試文章',
        content='這是一篇測試文章，提及 @john',
        author=author,
        status='published'
    )
    print(f"✅ 建立測試文章: {article.title}")

    # 建立提及記錄
    mentions = create_mentions_from_article(article, author)
    print(f"✅ 建立 {len(mentions)} 個提及記錄")

    # 驗證
    mention = Mention.objects.filter(article=article).first()
    if mention:
        print(f"   提及者: {mention.mentioning_user.username}")
        print(f"   被提及者: {mention.mentioned_user.username}")
        print(f"   上下文: {mention.context}")


def test_user_group():
    """測試使用者群組功能"""
    print("\n=== 測試使用者群組 ===")

    # 建立測試使用者
    try:
        creator = User.objects.get(username='groupcreator')
    except User.DoesNotExist:
        creator = User.objects.create_user(
            username='groupcreator',
            password='testpass123'
        )
        print("✅ 建立群組創建者")

    # 建立群組
    group = UserGroup.objects.create(
        name='Django 學習小組',
        description='一起學習 Django 框架',
        group_type='public',
        creator=creator,
        tags='Python,Django,Web'
    )
    print(f"✅ 建立群組: {group.name}")

    # 加入創建者
    membership = GroupMembership.objects.create(
        group=group,
        user=creator,
        role='owner',
        join_method='created'
    )
    print(f"✅ 創建者加入群組，角色: {membership.role}")

    # 測試權限
    print(f"   是否為成員: {group.is_member(creator)}")
    print(f"   是否為管理員: {group.is_admin(creator)}")

    # 建立另一個使用者並加入群組
    try:
        member = User.objects.get(username='groupmember')
    except User.DoesNotExist:
        member = User.objects.create_user(
            username='groupmember',
            password='testpass123'
        )
        print("✅ 建立群組成員")

    if group.can_join(member):
        GroupMembership.objects.create(
            group=group,
            user=member,
            role='member',
            join_method='joined'
        )
        print(f"✅ {member.username} 加入群組")


def test_event():
    """測試活動功能"""
    print("\n=== 測試活動功能 ===")

    # 建立組織者
    try:
        organizer = User.objects.get(username='organizer')
    except User.DoesNotExist:
        organizer = User.objects.create_user(
            username='organizer',
            password='testpass123'
        )
        print("✅ 建立活動組織者")

    # 建立活動
    event = Event.objects.create(
        title='Django 線上工作坊',
        description='學習 Django 進階技巧',
        event_type='online_event',
        organizer=organizer,
        start_time=timezone.now() + timedelta(days=7),
        end_time=timezone.now() + timedelta(days=7, hours=2),
        registration_deadline=timezone.now() + timedelta(days=6),
        max_participants=50,
        status='published'
    )
    print(f"✅ 建立活動: {event.title}")
    print(f"   活動類型: {event.get_event_type_display()}")
    print(f"   開始時間: {event.start_time.strftime('%Y-%m-%d %H:%M')}")

    # 測試報名
    try:
        participant = User.objects.get(username='participant')
    except User.DoesNotExist:
        participant = User.objects.create_user(
            username='participant',
            password='testpass123'
        )
        print("✅ 建立參與者")

    if event.can_register():
        EventParticipant.objects.create(
            event=event,
            user=participant,
            status='registered'
        )
        print(f"✅ {participant.username} 報名活動")

    # 更新參與人數
    event.participants_count = event.participants.count()
    event.save()
    print(f"   目前報名人數: {event.participants_count}")


def test_stats():
    """顯示統計資訊"""
    print("\n=== 系統統計 ===")

    stats = {
        '總使用者數': User.objects.count(),
        '總文章數': Article.objects.count(),
        '總群組數': UserGroup.objects.count(),
        '總活動數': Event.objects.count(),
        '總提及數': Mention.objects.count(),
    }

    for key, value in stats.items():
        print(f"{key}: {value}")


def cleanup_test_data():
    """清理測試資料"""
    print("\n=== 清理測試資料 ===")

    # 刪除測試使用者（及其相關資料會自動級聯刪除）
    test_users = ['testauthor', 'john', 'groupcreator', 'groupmember', 'organizer', 'participant']

    for username in test_users:
        try:
            user = User.objects.get(username=username)
            user.delete()
            print(f"✅ 刪除測試使用者: {username}")
        except User.DoesNotExist:
            pass

    print("✅ 清理完成")


if __name__ == '__main__':
    print("=" * 50)
    print("社群互動功能測試")
    print("=" * 50)

    try:
        # 執行測試
        test_mention_parsing()
        test_mention_creation()
        test_user_group()
        test_event()
        test_stats()

        print("\n" + "=" * 50)
        print("✅ 所有測試完成！")
        print("=" * 50)

        # 詢問是否清理測試資料
        response = input("\n是否要清理測試資料？(y/n): ")
        if response.lower() == 'y':
            cleanup_test_data()
        else:
            print("保留測試資料")

    except Exception as e:
        print(f"\n❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
