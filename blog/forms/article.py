"""
文章相關的 Forms
"""
from django import forms
from ..models import Article


class ArticleForm(forms.ModelForm):
    """
    文章表單
    用於新增和編輯文章
    """
    class Meta:
        model = Article
        fields = ['title', 'content']
        labels = {
            'title': '文章標題',
            'content': '文章內容',
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '請輸入文章標題',
                'maxlength': '100'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '請輸入文章內容',
                'rows': 10
            }),
        }
        help_texts = {
            'title': '標題最多 100 個字元',
            'content': '支援 Markdown 語法（# 標題、**粗體**、*斜體*、[連結](URL)、```程式碼區塊```）',
        }
