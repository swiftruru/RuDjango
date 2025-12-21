#!/usr/bin/env python
"""檢查用戶統計資料"""
import os
import django

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RuDjangoProject.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Article, Comment

# 檢查 ruru 用戶的統計
user = User.objects.get(username='ruru')
print(f'用戶: {user.username}')
print(f'文章數: {user.articles.count()}')
print(f'評論數: {user.comments.count()}')
print(f'追蹤者: {user.followers.count()}')
print(f'追蹤中: {user.following.count()}')

# 列出所有文章
print('\n文章列表：')
for article in user.articles.all():
    print(f'  - {article.title}')

# 列出所有評論
print('\n評論列表：')
for comment in user.comments.all():
    print(f'  - {comment.content[:50]}...')
