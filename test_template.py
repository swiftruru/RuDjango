#!/usr/bin/env python
"""測試模板渲染"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import UserProfile

user = User.objects.get(username='ruru')

# 模擬視圖中的 stats 計算
stats = {
    'posts': user.articles.count(),
    'comments': user.comments.count(),
    'likes_received': 0,
    'followers': user.followers.count(),
    'following': user.following.count(),
}

print("Stats 字典內容：")
print(stats)
print(f"\n訪問方式測試：")
print(f"stats['posts'] = {stats['posts']}")
print(f"stats['comments'] = {stats['comments']}")
print(f"stats['likes_received'] = {stats['likes_received']}")
print(f"stats['followers'] = {stats['followers']}")
print(f"stats['following'] = {stats['following']}")
