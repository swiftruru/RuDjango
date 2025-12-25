from django.urls import path

from . import views

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
]

# 靜態頁面路由
page_patterns = [
    path('about', views.about),
]

# 合併所有路由
urlpatterns = article_patterns + member_patterns + message_patterns + tag_patterns + search_patterns + page_patterns
