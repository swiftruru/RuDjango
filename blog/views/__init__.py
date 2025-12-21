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
    my_articles,
    comment_delete
)

# 會員相關 views
from .member_views import (
    member,
    member_edit,
    member_profile,
    member_activities,
    member_achievements,
    learning_progress,
    user_login,
    user_register,
    user_logout,
    edit_skills
)

__all__ = [
    # 文章相關
    'home',
    'about',
    'article_detail',
    'article_create',
    'article_edit',
    'article_delete',
    'my_articles',
    'comment_delete',
    # 會員相關
    'member',
    'member_edit',
    'member_profile',
    'member_activities',
    'member_achievements',
    'learning_progress',
    'user_login',
    'user_register',
    'user_logout',
    'edit_skills',
]
