from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # 用戶管理
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.user_toggle_status, name='user_toggle_status'),
    path('users/<int:user_id>/toggle-staff/', views.user_toggle_staff, name='user_toggle_staff'),

    # 文章管理
    path('articles/', views.article_list, name='article_list'),
    path('articles/<int:article_id>/', views.article_detail, name='article_detail'),
    path('articles/<int:article_id>/delete/', views.article_delete, name='article_delete'),

    # 留言管理
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),

    # 標籤管理
    path('tags/', views.tag_list, name='tag_list'),
    path('tags/<int:tag_id>/', views.tag_detail, name='tag_detail'),
    path('tags/<int:tag_id>/delete/', views.tag_delete, name='tag_delete'),

    # 聊天管理
    path('chats/', views.chat_list, name='chat_list'),
    path('chats/<str:room_id>/', views.chat_detail, name='chat_detail'),
    path('chats/<str:room_id>/delete/', views.chat_delete, name='chat_delete'),

    # 通知管理
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/batch-delete/', views.notification_batch_delete, name='notification_batch_delete'),
    path('notifications/batch-mark-read/', views.notification_batch_mark_read, name='notification_batch_mark_read'),

    # 群組管理
    path('groups/', views.group_list, name='group_list'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/delete/', views.group_delete, name='group_delete'),
    path('groups/<int:group_id>/members/<int:user_id>/remove/', views.group_member_remove, name='group_member_remove'),
    path('groups/<int:group_id>/members/<int:user_id>/change-role/', views.group_member_change_role, name='group_member_change_role'),
    path('groups/posts/<int:post_id>/delete/', views.group_post_delete, name='group_post_delete'),

    # 數據分析
    path('analytics/search/', views.search_analytics, name='search_analytics'),

    # 系統設定
    path('system/settings/', views.system_settings, name='system_settings'),
    path('system/logs/', views.system_logs, name='system_logs'),
]
