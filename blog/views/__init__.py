"""
Blog app 的 views 模組
將各個 views 模組的函數匯入，讓外部可以直接從 views 引用
"""

# 文章相關 views
from .article_views import (
    home,
    about,
    article_detail,
    article_create,
    article_edit,
    article_delete,
    draft_publish,
    draft_discard,
    article_like,
    article_bookmark,
    article_share,
    article_autosave,
    my_articles,
    my_bookmarks,
    my_drafts,
    comment_delete,
    tags_list,
    tag_articles,
    advanced_search,
    search_suggestions,
    quick_search
)

# 會員相關 views
from .member_views import (
    member,
    member_edit,
    member_profile,
    member_activities,
    member_achievements,
    learning_progress,
    member_articles,
    member_comments,
    user_login,
    user_register,
    user_logout,
    edit_skills,
    follow_user,
    followers_list,
    following_list
)

# 訊息相關 views
from .message_views import (
    inbox,
    outbox,
    message_compose,
    message_detail,
    message_delete,
    mark_all_read,
    message_recall,
    bulk_mark_read,
    bulk_delete,
    outbox_bulk_delete
)

# 通知相關 views
from .notification_views import (
    notifications_center,
    notification_mark_read,
    notification_mark_all_read,
    notification_delete,
    notification_delete_all_read,
    notification_count,
    notification_preferences
)

__all__ = [
    # 文章相關
    'home',
    'about',
    'article_detail',
    'article_create',
    'article_edit',
    'article_delete',
    'draft_publish',
    'draft_discard',
    'article_like',
    'article_bookmark',
    'article_share',
    'article_autosave',
    'my_articles',
    'my_bookmarks',
    'my_drafts',
    'comment_delete',
    'tags_list',
    'tag_articles',
    'advanced_search',
    'search_suggestions',
    'quick_search',
    # 會員相關
    'member',
    'member_edit',
    'member_profile',
    'member_activities',
    'member_achievements',
    'learning_progress',
    'member_articles',
    'member_comments',
    'user_login',
    'user_register',
    'user_logout',
    'edit_skills',
    'follow_user',
    'followers_list',
    'following_list',
    # 訊息相關
    'inbox',
    'outbox',
    'message_compose',
    'message_detail',
    'message_delete',
    'mark_all_read',
    'message_recall',
    'bulk_mark_read',
    'bulk_delete',
    'outbox_bulk_delete',
    # 通知相關
    'notifications_center',
    'notification_mark_read',
    'notification_mark_all_read',
    'notification_delete',
    'notification_delete_all_read',
    'notification_count',
    'notification_preferences',
]
