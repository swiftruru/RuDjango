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
    
    使用方式：
    {{ article.content|markdown }}
    """
    if not text:
        return ''
    
    # 使用 markdown 套件轉換，啟用常用擴展
    md = markdown.Markdown(extensions=[
        'extra',      # 支援表格、定義列表等
        'codehilite', # 代碼高亮
        'fenced_code', # 圍欄式代碼塊
        'nl2br',      # 換行轉 <br>
    ])
    
    html = md.convert(str(text))
    return mark_safe(html)
