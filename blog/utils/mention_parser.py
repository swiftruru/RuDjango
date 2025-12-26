"""
@提及功能的工具函數
用於解析文字中的 @username 提及，並建立提及記錄
"""
import re
from django.contrib.auth.models import User
from ..models import Mention, Article, Comment


def parse_mentions(text):
    """
    從文字中解析出所有的 @username 提及

    Args:
        text: 要解析的文字內容

    Returns:
        list: 被提及的使用者名稱列表（去重）
    """
    # 正則表達式匹配 @username
    # 支援英文、數字、底線、中文
    pattern = r'@([\w\u4e00-\u9fa5]+)'
    mentions = re.findall(pattern, text)

    # 去重並返回
    return list(set(mentions))


def get_mention_context(text, username, max_length=200):
    """
    獲取提及的上下文內容

    Args:
        text: 完整文字內容
        username: 被提及的使用者名稱
        max_length: 最大上下文長度

    Returns:
        str: 提及的上下文
    """
    mention_pattern = f'@{username}'
    index = text.find(mention_pattern)

    if index == -1:
        return ''

    # 計算上下文範圍
    start = max(0, index - max_length // 2)
    end = min(len(text), index + len(mention_pattern) + max_length // 2)

    context = text[start:end]

    # 如果不是從開頭開始，加上省略號
    if start > 0:
        context = '...' + context

    # 如果不是到結尾，加上省略號
    if end < len(text):
        context = context + '...'

    return context


def create_mentions_from_article(article, mentioning_user):
    """
    從文章內容中建立提及記錄

    Args:
        article: Article 物件
        mentioning_user: 提及者（User 物件）

    Returns:
        list: 建立的 Mention 物件列表
    """
    # 解析文章標題和內容中的提及
    all_text = f"{article.title} {article.content}"
    usernames = parse_mentions(all_text)

    created_mentions = []

    for username in usernames:
        try:
            # 獲取被提及的使用者
            mentioned_user = User.objects.get(username=username)

            # 不能提及自己
            if mentioned_user == mentioning_user:
                continue

            # 檢查是否已經存在相同的提及記錄
            existing_mention = Mention.objects.filter(
                article=article,
                mentioned_user=mentioned_user,
                mentioning_user=mentioning_user
            ).first()

            if existing_mention:
                # 如果已存在，更新上下文
                existing_mention.context = get_mention_context(all_text, username)
                existing_mention.save()
                created_mentions.append(existing_mention)
            else:
                # 建立新的提及記錄
                mention = Mention.objects.create(
                    mentioned_user=mentioned_user,
                    mentioning_user=mentioning_user,
                    mention_type='article',
                    article=article,
                    context=get_mention_context(all_text, username)
                )
                created_mentions.append(mention)

        except User.DoesNotExist:
            # 使用者不存在，跳過
            continue

    return created_mentions


def create_mentions_from_comment(comment, mentioning_user):
    """
    從留言內容中建立提及記錄

    Args:
        comment: Comment 物件
        mentioning_user: 提及者（User 物件）

    Returns:
        list: 建立的 Mention 物件列表
    """
    usernames = parse_mentions(comment.content)

    created_mentions = []

    for username in usernames:
        try:
            # 獲取被提及的使用者
            mentioned_user = User.objects.get(username=username)

            # 不能提及自己
            if mentioned_user == mentioning_user:
                continue

            # 檢查是否已經存在相同的提及記錄
            existing_mention = Mention.objects.filter(
                comment=comment,
                mentioned_user=mentioned_user,
                mentioning_user=mentioning_user
            ).first()

            if existing_mention:
                # 如果已存在，更新上下文
                existing_mention.context = get_mention_context(comment.content, username)
                existing_mention.save()
                created_mentions.append(existing_mention)
            else:
                # 建立新的提及記錄
                mention = Mention.objects.create(
                    mentioned_user=mentioned_user,
                    mentioning_user=mentioning_user,
                    mention_type='comment',
                    article=comment.article,
                    comment=comment,
                    context=get_mention_context(comment.content, username)
                )
                created_mentions.append(mention)

        except User.DoesNotExist:
            # 使用者不存在，跳過
            continue

    return created_mentions


def highlight_mentions(text):
    """
    將文字中的 @username 轉換為可點擊的連結（HTML）
    顯示使用者的暱稱（如果有）或使用者名稱

    Args:
        text: 原始文字

    Returns:
        str: 處理後的 HTML 文字
    """
    # 正則表達式匹配 @username
    pattern = r'@([\w\u4e00-\u9fa5]+)'

    def replace_mention(match):
        username = match.group(1)
        # 檢查使用者是否存在
        try:
            user = User.objects.get(username=username)
            # 使用暱稱（first_name）或使用者名稱
            display_name = user.first_name if user.first_name else user.username
            # 如果存在，返回連結（顯示暱稱但連結到使用者頁面）
            return f'<a href="/blog/member/{username}/" class="mention" title="@{username}">@{display_name}</a>'
        except User.DoesNotExist:
            # 如果不存在，返回原文
            return f'@{username}'

    return re.sub(pattern, replace_mention, text)


def get_mentionable_users(current_user=None, search_query='', limit=10):
    """
    獲取可以被提及的使用者列表（用於自動完成）

    Args:
        current_user: 當前使用者（排除自己）
        search_query: 搜尋關鍵字
        limit: 返回數量限制

    Returns:
        QuerySet: 使用者查詢集
    """
    users = User.objects.filter(is_active=True)

    # 排除當前使用者
    if current_user and current_user.is_authenticated:
        users = users.exclude(id=current_user.id)

    # 搜尋過濾
    if search_query:
        users = users.filter(username__icontains=search_query)

    # 限制數量
    users = users.order_by('username')[:limit]

    return users


def delete_mentions_for_article(article):
    """
    刪除文章相關的所有提及記錄
    （當文章被刪除時使用）

    Args:
        article: Article 物件
    """
    Mention.objects.filter(article=article).delete()


def delete_mentions_for_comment(comment):
    """
    刪除留言相關的所有提及記錄
    （當留言被刪除時使用）

    Args:
        comment: Comment 物件
    """
    Mention.objects.filter(comment=comment).delete()


def update_article_mentions(article):
    """
    更新文章的提及記錄
    （當文章被編輯時使用）

    Args:
        article: Article 物件
    """
    # 刪除舊的提及記錄
    Mention.objects.filter(
        article=article,
        mention_type='article'
    ).delete()

    # 重新建立提及記錄
    if article.author:
        create_mentions_from_article(article, article.author)


def update_comment_mentions(comment):
    """
    更新留言的提及記錄
    （當留言被編輯時使用）

    Args:
        comment: Comment 物件
    """
    # 刪除舊的提及記錄
    Mention.objects.filter(
        comment=comment,
        mention_type='comment'
    ).delete()

    # 重新建立提及記錄
    create_mentions_from_comment(comment, comment.author)
