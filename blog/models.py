from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        # 定義物件的字串表示，讓後台顯示文章標題而不是 "Article object (1)"
        return self.title
    
    class Meta:
        # 設定模型的額外選項，ordering 用來指定預設排序方式
        # '-created_at' 表示依建立時間倒序排列（最新的在前面）
        ordering = ['-created_at']