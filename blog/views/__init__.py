# 將各個 views 模組的函數匯入，讓外部可以直接從 views 引用
from .article_views import home, about, article_detail, article_create, article_edit, article_delete, my_articles
from .member_views import member

# 保留測試用的 hello views（之後可以刪除）
from django.http import HttpResponse

def hello(request):
    return HttpResponse('hello, world')

def hello2(request):
    return HttpResponse('hello, world2')
