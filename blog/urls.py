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
    path('my-articles/', views.my_articles, name='my_articles'),
]

# 會員相關路由
member_patterns = [
    path('member/', views.member, name='member'),
    path('member/edit/', views.member_edit, name='member_edit'),
    path('member/skills/edit/', views.edit_skills, name='edit_skills'),
    path('member/<str:username>/', views.member_profile, name='member_profile'),
    path('member/<str:username>/activities/', views.member_activities, name='member_activities'),
    path('member/<str:username>/achievements/', views.member_achievements, name='member_achievements'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.user_register, name='user_register'),
    path('logout/', views.user_logout, name='user_logout'),
]

# 靜態頁面路由
page_patterns = [
    path('about', views.about),
]

# 合併所有路由
urlpatterns = article_patterns + member_patterns + page_patterns
