from django.urls import path

from . import views

# 文章相關路由
article_patterns = [
    path('', views.home, name='blog_home'),
    path('home', views.home),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
]

# 會員相關路由
member_patterns = [
    path('member', views.member, name='member'),
]

# 靜態頁面路由
page_patterns = [
    path('about', views.about),
]

# 合併所有路由
urlpatterns = article_patterns + member_patterns + page_patterns
