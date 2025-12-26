from django.urls import path

from . import views
from .feeds import LatestArticlesFeed, LatestArticlesAtomFeed, ArticlesByAuthorFeed, ArticlesByTagFeed

# 文章相關路由
article_patterns = [
    path('', views.home, name='blog_home'),
    path('home', views.home),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('article/create/', views.article_create, name='article_create'),
    path('article/<int:id>/edit/', views.article_edit, name='article_edit'),
    path('article/<int:id>/delete/', views.article_delete, name='article_delete'),
    path('article/<int:id>/draft/publish/', views.draft_publish, name='draft_publish'),
    path('article/<int:id>/draft/discard/', views.draft_discard, name='draft_discard'),
    path('article/<int:id>/like/', views.article_like, name='article_like'),
    path('article/<int:id>/bookmark/', views.article_bookmark, name='article_bookmark'),
    path('article/<int:id>/share/', views.article_share, name='article_share'),
    path('article/autosave/', views.article_autosave, name='article_autosave_new'),
    path('article/<int:id>/autosave/', views.article_autosave, name='article_autosave'),
    path('my-articles/', views.my_articles, name='my_articles'),
    path('my-bookmarks/', views.my_bookmarks, name='my_bookmarks'),
    path('my-drafts/', views.my_drafts, name='my_drafts'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
]

# 會員相關路由
member_patterns = [
    path('member/', views.member, name='member'),
    path('member/edit/', views.member_edit, name='member_edit'),
    path('member/skills/edit/', views.edit_skills, name='edit_skills'),
    path('member/<str:username>/', views.member_profile, name='member_profile'),
    path('member/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('member/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('member/<str:username>/following/', views.following_list, name='following_list'),
    path('member/<str:username>/activities/', views.member_activities, name='member_activities'),
    path('member/<str:username>/achievements/', views.member_achievements, name='member_achievements'),
    path('member/<str:username>/learning/', views.learning_progress, name='learning_progress'),
    path('member/<str:username>/articles/', views.member_articles, name='member_articles'),
    path('member/<str:username>/comments/', views.member_comments, name='member_comments'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
]

# 私人訊息路由
message_patterns = [
    path('messages/inbox/', views.inbox, name='inbox'),
    path('messages/outbox/', views.outbox, name='outbox'),
    path('messages/compose/', views.message_compose, name='message_compose'),
    path('messages/compose/<str:username>/', views.message_compose, name='message_compose_to'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/<int:message_id>/delete/', views.message_delete, name='message_delete'),
    path('messages/<int:message_id>/recall/', views.message_recall, name='message_recall'),
    path('messages/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('messages/bulk-mark_read/', views.bulk_mark_read, name='bulk_mark_read'),
    path('messages/bulk-delete/', views.bulk_delete, name='bulk_delete'),
    path('messages/outbox/bulk-delete/', views.outbox_bulk_delete, name='outbox_bulk_delete'),
]

# 標籤相關路由
tag_patterns = [
    path('tags/', views.tags_list, name='tags_list'),
    path('tag/<str:slug>/', views.tag_articles, name='tag_articles'),
]

# 搜尋相關路由
search_patterns = [
    path('search/', views.advanced_search, name='advanced_search'),
    path('api/search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('api/search/quick/', views.quick_search, name='quick_search'),
    path('api/search/history/', views.get_search_history, name='get_search_history'),
    path('api/search/history/clear/', views.clear_search_history, name='clear_search_history'),
    path('api/search/history/delete/', views.delete_search_item, name='delete_search_item'),
]

# 通知相關路由
notification_patterns = [
    path('notifications/', views.notifications_center, name='notifications_center'),
    path('notifications/<int:notification_id>/read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/delete-all-read/', views.notification_delete_all_read, name='notification_delete_all_read'),
    path('api/notifications/count/', views.notification_count, name='notification_count'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
]

# 靜態頁面路由
page_patterns = [
    path('about', views.about),
]

# 社群互動路由
social_patterns = [
    # @提及功能
    path('mentions/', views.mention_list, name='mention_list'),
    path('api/mentions/count/', views.mention_count, name='mention_count'),
    path('api/mentions/search-users/', views.search_users_for_mention, name='search_users_for_mention'),

    # 用戶 API
    path('api/user/<str:username>/', views.get_user_api, name='get_user_api'),

    # 即時聊天 API
    path('api/chat/list/', views.get_chat_list_api, name='get_chat_list_api'),

    # Web Push 推播通知 API
    path('api/push/subscribe/', views.subscribe_push, name='subscribe_push'),
    path('api/push/unsubscribe/', views.unsubscribe_push, name='unsubscribe_push'),
    path('api/push/test/', views.test_push_notification_view, name='test_push_notification'),

    # 文章協作功能
    path('article/<int:article_id>/collaborators/', views.article_collaborators, name='article_collaborators'),
    path('article/<int:article_id>/collaborators/invite/', views.invite_collaborator, name='invite_collaborator'),
    path('collaborator/<int:collaborator_id>/accept/', views.accept_collaboration, name='accept_collaboration'),
    path('collaborator/<int:collaborator_id>/remove/', views.remove_collaborator, name='remove_collaborator'),
    path('article/<int:article_id>/history/', views.article_edit_history, name='article_edit_history'),

    # 群組功能
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.group_create, name='group_create'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.group_join, name='group_join'),
    path('groups/<int:group_id>/leave/', views.group_leave, name='group_leave'),
    path('groups/<int:group_id>/members/', views.group_members, name='group_members'),
    path('groups/<int:group_id>/post/create/', views.group_post_create, name='group_post_create'),
    path('groups/post/<int:post_id>/', views.group_post_detail, name='group_post_detail'),
    path('my-groups/', views.my_groups, name='my_groups'),

    # 活動功能
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/register/', views.event_register, name='event_register'),
    path('events/<int:event_id>/cancel/', views.event_cancel_registration, name='event_cancel_registration'),
    path('my-events/', views.my_events, name='my_events'),

    # 公告功能
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:announcement_id>/', views.announcement_detail, name='announcement_detail'),
]

# RSS Feed 路由
feed_patterns = [
    path('feed/rss/', LatestArticlesFeed(), name='article_feed_rss'),
    path('feed/atom/', LatestArticlesAtomFeed(), name='article_feed_atom'),
    path('feed/author/<str:username>/', ArticlesByAuthorFeed(), name='author_feed'),
    path('feed/tag/<int:tag_id>/', ArticlesByTagFeed(), name='tag_feed'),
]

# 推薦系統路由
recommendation_patterns = [
    # 個人化推薦頁面
    path('recommendations/', views.personalized_feed, name='personalized_feed'),

    # 推薦系統 API
    path('api/article/<int:id>/similar/', views.get_similar_articles_api, name='get_similar_articles_api'),
    path('api/recommendations/personalized/', views.get_personalized_recommendations_api, name='get_personalized_recommendations_api'),
    path('api/recommendations/', views.get_recommended_articles_api, name='get_recommended_articles_api'),
]

# 合併所有路由
urlpatterns = article_patterns + member_patterns + message_patterns + tag_patterns + search_patterns + notification_patterns + social_patterns + page_patterns + feed_patterns + recommendation_patterns
