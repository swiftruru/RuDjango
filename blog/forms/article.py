"""
文章相關的 Forms
"""
from django import forms
from ..models import Article, Comment, Tag


class ArticleForm(forms.ModelForm):
    """
    文章表單
    用於新增和編輯文章
    """
    tags_input = forms.CharField(
        required=False,
        label='標籤',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '輸入標籤，用逗號或空格分隔 (例如: Python, Django, Web開發)',
            'id': 'tags-input'
        }),
        help_text='用逗號或空格分隔多個標籤，系統會自動建立新標籤'
    )

    class Meta:
        model = Article
        fields = ['title', 'content', 'status', 'publish_at']
        labels = {
            'title': '文章標題',
            'content': '文章內容',
            'status': '發布狀態',
            'publish_at': '排程發布時間',
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
            'status': forms.Select(attrs={
                'class': 'form-control',
                'id': 'status-select'
            }),
            'publish_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'publish-at-input'
            }),
        }
        help_texts = {
            'title': '標題最多 100 個字元',
            'content': '支援 Markdown 語法（# 標題、**粗體**、*斜體**、[連結](URL)、```程式碼區塊```）',
            'status': '選擇文章狀態：立即發布、儲存草稿或排程發布',
            'publish_at': '選擇文章的發布時間（僅在「排程發布」時需要）',
        }

    def __init__(self, *args, **kwargs):
        # 如果是已發布文章且有草稿，先將草稿內容複製到 instance，再初始化表單
        instance = kwargs.get('instance')
        if instance and instance.pk and instance.status == 'published' and instance.has_draft:
            import json
            # 暫時將草稿內容覆蓋到 instance（不儲存到資料庫）
            instance.title = instance.draft_title
            instance.content = instance.draft_content
            # 注意：這裡不處理 tags，因為 tags 是 ManyToMany 關係

        super().__init__(*args, **kwargs)

        # 如果是編輯現有文章，預填標籤
        if self.instance and self.instance.pk:
            # 如果是已發布文章且有草稿，載入草稿標籤
            if self.instance.status == 'published' and self.instance.has_draft:
                import json
                # 載入草稿標籤
                if self.instance.draft_tags_json:
                    try:
                        tag_names = json.loads(self.instance.draft_tags_json)
                        self.fields['tags_input'].initial = ', '.join(tag_names)
                    except:
                        tag_names = ', '.join([tag.name for tag in self.instance.tags.all()])
                        self.fields['tags_input'].initial = tag_names
                else:
                    tag_names = ', '.join([tag.name for tag in self.instance.tags.all()])
                    self.fields['tags_input'].initial = tag_names
            else:
                # 正常載入已發布或草稿文章的標籤
                tag_names = ', '.join([tag.name for tag in self.instance.tags.all()])
                self.fields['tags_input'].initial = tag_names

            # 如果文章已經發布，清空排程時間（因為已經不需要了）
            if self.instance.status == 'published':
                self.fields['publish_at'].initial = None

    def clean(self):
        """驗證表單數據"""
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        publish_at = cleaned_data.get('publish_at')

        # 只有在選擇排程發布時才驗證排程時間
        if status == 'scheduled':
            if not publish_at:
                raise forms.ValidationError('排程發布必須設定發布時間')

            # 排程時間不能是過去
            from django.utils import timezone
            if publish_at <= timezone.now():
                raise forms.ValidationError('排程時間必須是未來的時間')

        return cleaned_data

    def save(self, commit=True):
        article = super().save(commit=False)
        if commit:
            article.save()
            # 處理標籤
            self._save_tags(article)
            self.save_m2m()  # 儲存 ManyToMany 關聯
        return article

    def _save_tags(self, article):
        """處理標籤的儲存"""
        tags_input = self.cleaned_data.get('tags_input', '')
        article.tags.clear()  # 清除現有標籤

        if tags_input:
            # 分割標籤（支援逗號和空格）
            tag_names = [name.strip() for name in tags_input.replace(',', ' ').split() if name.strip()]

            for tag_name in tag_names:
                # 標籤名稱不能太長
                if len(tag_name) > 50:
                    continue
                # 取得或建立標籤
                tag, created = Tag.objects.get_or_create(name=tag_name)
                article.tags.add(tag)


class CommentForm(forms.ModelForm):
    """
    留言表單
    用於新增和回覆留言
    """
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '留言內容',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': '請輸入您的留言...',
                'rows': 4
            }),
        }
        help_texts = {
            'content': '分享您的想法和意見',
        }
