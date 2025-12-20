"""
Django 表單定義
處理文章的新增和編輯表單
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from .models import Article


class CustomAuthenticationForm(AuthenticationForm):
    """
    自訂登入表單，添加樣式
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請輸入使用者名稱'
        })
        self.fields['username'].label = '使用者名稱'
        
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請輸入密碼'
        })
        self.fields['password'].label = '密碼'


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


class CustomUserCreationForm(UserCreationForm):
    """
    自訂註冊表單，添加暱稱欄位
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        label='使用者名稱',
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9]+$',
                message='使用者名稱只能包含字母和數字',
                code='invalid_username'
            )
        ],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入使用者名稱'
        }),
        help_text='必填。150 個字元以內。只能包含字母和數字。'
    )
    
    first_name = forms.CharField(
        max_length=150,
        required=True,
        label='暱稱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入您的暱稱'
        }),
        help_text='這是您在網站上顯示的名稱'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 為密碼欄位添加樣式和簡化說明文字
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請輸入密碼'
        })
        self.fields['password1'].help_text = '密碼至少 8 個字元，不能全是數字或太常見。'
        
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '請再次輸入密碼'
        })
        self.fields['password2'].help_text = '請再次輸入相同的密碼以確認。'
