"""
Blog app 的 Models 模組
按功能分類組織
"""

# 文章相關 models
from .article import Tag, Article, ArticleReadHistory, Comment, Like, Bookmark, ArticleShare

# 會員相關 models
from .member import (
    UserProfile,
    Skill,
    Achievement,
    UserAchievement,
    LearningCourse,
    UserCourseProgress,
    Activity,
    Follow,
    Message,
)

# 通知相關 models
from .notification import Notification, NotificationPreference

# 社群互動相關 models
from .social import (
    Mention,
    ArticleCollaborator,
    ArticleEditHistory,
    UserGroup,
    GroupMembership,
    GroupPost,
    Event,
    EventParticipant,
    Announcement,
)

__all__ = [
    # 文章相關
    'Tag',
    'Article',
    'ArticleReadHistory',
    'Comment',
    'Like',
    'Bookmark',
    'ArticleShare',
    # 會員相關
    'UserProfile',
    'Skill',
    'Achievement',
    'UserAchievement',
    'LearningCourse',
    'UserCourseProgress',
    'Activity',
    'Follow',
    'Message',
    # 通知相關
    'Notification',
    'NotificationPreference',
    # 社群互動相關
    'Mention',
    'ArticleCollaborator',
    'ArticleEditHistory',
    'UserGroup',
    'GroupMembership',
    'GroupPost',
    'Event',
    'EventParticipant',
    'Announcement',
]
