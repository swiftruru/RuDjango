"""
會員相關的 Forms
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from ..models import UserProfile, Skill


class CustomAuthenticationForm(AuthenticationForm):
    """自訂登入表單，添加樣式"""
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


class CustomUserCreationForm(UserCreationForm):
    """自訂註冊表單，添加暱稱欄位"""
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


class UserProfileForm(forms.ModelForm):
    """使用者資料編輯表單"""
    first_name = forms.CharField(
        max_length=150,
        required=False,
        label='暱稱',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入您的暱稱'
        })
    )

    email = forms.EmailField(
        required=False,
        label='電子信箱',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )

    skills = forms.CharField(
        required=False,
        label='技能標籤',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'skills-input',
            'placeholder': '輸入技能後按 Enter 或逗號新增'
        }),
        help_text='輸入您擅長的技能，如 Python、Django、JavaScript 等'
    )

    class Meta:
        model = UserProfile
        fields = ['bio', 'avatar', 'school', 'grade', 'location', 'birthday', 'website', 'github']
        labels = {
            'bio': '個人簡介',
            'avatar': '頭像',
            'school': '學校',
            'grade': '年級',
            'location': '地點',
            'birthday': '生日',
            'website': '個人網站',
            'github': 'GitHub 帳號',
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '介紹一下你自己...',
                'rows': 4
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'school': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：台北第一女子高級中學'
            }),
            'grade': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：高二'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '例如：Taipei, Taiwan'
            }),
            'birthday': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://yourwebsite.com'
            }),
            'github': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'yourusername'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['email'].initial = self.user.email
            # 載入用戶當前的技能
            current_skills = self.user.skills.all()
            self.fields['skills'].initial = ','.join([skill.name for skill in current_skills])

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            if commit:
                self.user.save()
        if commit:
            profile.save()
            # 處理技能標籤
            if self.user:
                self._save_skills()
        return profile

    def _save_skills(self):
        """處理技能標籤的保存"""
        skills_data = self.cleaned_data.get('skills', '')

        # 清除當前所有技能
        self.user.skills.clear()

        if skills_data:
            # 分割技能字符串（支援逗號和分號分隔）
            skill_names = [s.strip() for s in skills_data.replace(';', ',').split(',') if s.strip()]

            # 為每個技能創建或獲取 Skill 對象，並添加到用戶
            for skill_name in skill_names:
                # 限制技能名稱長度
                if len(skill_name) <= 50:
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    self.user.skills.add(skill)


class MessageForm(forms.Form):
    """私人訊息表單"""
    recipient_username = forms.CharField(
        max_length=150,
        required=True,
        label='收件者',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入收件者的使用者名稱'
        })
    )
    subject = forms.CharField(
        max_length=200,
        required=True,
        label='主旨',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '請輸入訊息主旨'
        })
    )
    content = forms.CharField(
        required=True,
        label='內容',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '請輸入訊息內容',
            'rows': 8
        })
    )

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        self.recipient = kwargs.pop('recipient', None)
        super().__init__(*args, **kwargs)

        # 如果有指定收件者，預填並設為唯讀
        if self.recipient:
            self.fields['recipient_username'].initial = self.recipient.username
            self.fields['recipient_username'].widget.attrs['readonly'] = True

    def clean_recipient_username(self):
        username = self.cleaned_data.get('recipient_username')

        # 如果已有指定收件者，使用指定的
        if self.recipient:
            return self.recipient.username

        # 檢查用戶是否存在
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('找不到此使用者')

        # 不能發送訊息給自己
        if self.sender and username == self.sender.username:
            raise forms.ValidationError('不能發送訊息給自己')

        return username


class MessageReplyForm(forms.Form):
    """訊息回覆表單（簡化版，只需要內容）"""
    content = forms.CharField(
        required=True,
        label='回覆內容',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': '請輸入回覆內容',
            'rows': 6
        })
    )
