"""
自定義模板過濾器
提供文字高亮顯示和 Markdown 渲染功能
"""
from django import template
from django.utils.safestring import mark_safe
import markdown
import re

register = template.Library()


@register.filter(name='highlight')
def highlight(text, search_query):
    """
    將文字中的搜尋關鍵字標記為黃色螢光筆效果
    
    使用方式：
    {{ article.title|highlight:search_query }}
    """
    if not search_query:
        return text
    
    # 使用正則表達式進行不分大小寫的替換
    # 並保留原始字母的大小寫
    pattern = re.compile(re.escape(search_query), re.IGNORECASE)
    highlighted = pattern.sub(
        lambda m: f'<mark class="highlight">{m.group()}</mark>',
        str(text)
    )
    
    # mark_safe 告訴 Django 這段 HTML 是安全的，不需要跳脫
    return mark_safe(highlighted)


@register.filter(name='markdown')
def markdown_format(text):
    """
    將 Markdown 格式的文字轉換為 HTML

    支援 LaTeX 數學公式（使用 $ 和 $$ 符號）
    支援 Mermaid 圖表

    使用方式：
    {{ article.content|markdown }}
    """
    if not text:
        return ''

    text = str(text)

    # 步驟 1: 保護數學公式，避免被 Markdown 處理
    protected_blocks = []

    def protect_block(match):
        """將數學公式替換為安全的佔位符"""
        protected_blocks.append(match.group(0))
        # 使用 HTML 註釋作為佔位符，Markdown 不會處理它
        return f'<!--MATH_{len(protected_blocks)-1}-->'

    # 保護 display math ($$...$$)
    text = re.sub(r'\$\$([\s\S]+?)\$\$', protect_block, text)

    # 保護 inline math ($...$) - 不跨行
    text = re.sub(r'(?<!\$)\$([^\$\n]+?)\$(?!\$)', protect_block, text)

    # 步驟 2: 正常處理 Markdown
    md = markdown.Markdown(extensions=[
        'extra',      # 支援表格、定義列表等
        'codehilite', # 代碼高亮
        'fenced_code', # 圍欄式代碼塊
        'nl2br',      # 換行轉 <br>
    ], extension_configs={
        'codehilite': {
            'guess_lang': True,  # 自動猜測語言
            'css_class': 'codehilite',  # CSS 類名
            'linenums': False,  # 不顯示行號
        }
    })

    html = md.convert(text)

    # 步驟 3: 還原數學公式
    for i, math_content in enumerate(protected_blocks):
        placeholder = f'<!--MATH_{i}-->'
        html = html.replace(placeholder, math_content)

    return mark_safe(html)


@register.filter(name='author_display')
def author_display(user):
    """
    顯示作者名稱，格式為「暱稱（帳號）」
    如果沒有暱稱則只顯示帳號
    
    使用方式：
    {{ article.author|author_display }}
    """
    if not user:
        return ''
    
    if user.first_name:
        return f'{user.first_name}（{user.username}）'
    return user.username


@register.simple_tag
def selected_if_equal(value1, value2):
    """
    如果兩個值相等則返回 'selected'
    
    使用方式：
    <option value="all" {% selected_if_equal search_type 'all' %}>全部</option>
    """
    if str(value1) == str(value2):
        return 'selected'
    return ''


@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    從字典中獲取指定鍵的值

    使用方式：
    {{ my_dict|get_item:key_variable }}
    """
    if not dictionary:
        return None
    return dictionary.get(key)


@register.simple_tag
def activity_title_with_link(activity):
    """
    將活動標題中的文章名稱轉換為連結
    例如：「發表了文章《Django 教學》」會變成「發表了文章<a>《Django 教學》</a>」

    使用方式：
    {% activity_title_with_link activity %}
    """
    title = activity.title

    # 如果是發表文章類型且有相關物件ID
    if activity.activity_type == 'post' and activity.related_object_id:
        # 使用正則表達式找出《》內的文章名稱
        pattern = r'(《.*?》)'
        match = re.search(pattern, title)

        if match:
            article_title = match.group(1)
            # 將《》內的文字替換為連結
            from django.urls import reverse
            article_url = reverse('article_detail', kwargs={'id': activity.related_object_id})
            linked_title = title.replace(
                article_title,
                f'<a href="{article_url}" class="activity-link">{article_title}</a>'
            )
            return mark_safe(linked_title)

    # 其他情況直接返回原標題
    return title


@register.filter(name='avatar_url')
def avatar_url(profile):
    """
    獲取帶有版本參數的頭像 URL，解決瀏覽器緩存問題

    使用方式：
    <img src="{{ request.user.profile|avatar_url }}" alt="Avatar">

    原理：在 URL 後面加上時間戳記參數（?v=timestamp），
    當頭像更新時，時間戳記會改變，瀏覽器就會重新下載新圖片
    """
    if not profile:
        return ''

    # 使用 UserProfile 模型的 get_avatar_url() 方法
    return profile.get_avatar_url() or ''


@register.filter(name='highlight_mentions')
def highlight_mentions(text):
    """
    將文字中的 @username 轉換為可點擊的連結

    使用方式：
    {{ article.content|highlight_mentions|markdown }}
    """
    if not text:
        return ''

    from ..utils.mention_parser import highlight_mentions as highlight
    return mark_safe(highlight(str(text)))


@register.simple_tag
def render_mention_context(mention):
    """
    渲染提及的上下文內容，並高亮顯示 @username

    使用方式：
    {% render_mention_context mention %}
    """
    if not mention or not mention.context:
        return ''

    context = mention.context
    username = mention.mentioned_user.username

    # 高亮顯示被提及的使用者名稱
    pattern = f'@{username}'
    highlighted = context.replace(
        pattern,
        f'<span class="font-bold text-blue-600">@{username}</span>'
    )

    return mark_safe(highlighted)
