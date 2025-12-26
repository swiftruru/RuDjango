"""
SEO 優化工具
自動生成 meta 描述、處理 SEO 相關功能
"""
import re
from django.utils.html import strip_tags
from django.utils.text import Truncator


def generate_meta_description(content, max_length=155):
    """
    自動生成 meta 描述

    Args:
        content: 文章內容（可能包含 Markdown 或 HTML）
        max_length: 描述最大長度（預設 155 字元，符合 Google 建議）

    Returns:
        str: 清理後的描述文字
    """
    if not content:
        return ""

    # 移除 HTML 標籤
    text = strip_tags(content)

    # 移除 Markdown 語法
    # 移除標題符號 (#)
    text = re.sub(r'#{1,6}\s+', '', text)
    # 移除連結 [text](url)
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # 移除圖片 ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)
    # 移除粗體和斜體 ** 或 *
    text = re.sub(r'\*{1,2}([^*]+)\*{1,2}', r'\1', text)
    # 移除程式碼區塊 ```
    text = re.sub(r'```[\s\S]*?```', '', text)
    # 移除行內程式碼 `
    text = re.sub(r'`([^`]+)`', r'\1', text)
    # 移除引用符號 >
    text = re.sub(r'>\s+', '', text)

    # 移除多餘的空白和換行
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    # 截斷到指定長度
    truncator = Truncator(text)
    description = truncator.chars(max_length, truncate='...')

    return description


def generate_keywords(article):
    """
    生成文章關鍵字

    Args:
        article: Article 物件

    Returns:
        str: 逗號分隔的關鍵字字串
    """
    keywords = []

    # 從標籤獲取關鍵字
    for tag in article.tags.all():
        keywords.append(tag.name)

    # 從分類獲取關鍵字（如果模型有 category 欄位）
    if hasattr(article, 'category') and article.category:
        keywords.append(article.category.name)

    return ', '.join(keywords)


def get_og_image(article):
    """
    獲取 Open Graph 圖片 URL
    優先使用文章的首圖，沒有則使用預設圖片

    Args:
        article: Article 物件

    Returns:
        str: 圖片 URL
    """
    # 這裡可以從文章內容中提取第一張圖片
    # 或使用作者頭像
    # 或使用網站預設圖片

    # 簡單實作：如果文章有封面圖就使用，否則返回 None
    # 之後可以從 Markdown 內容中提取第一張圖片
    return None


def extract_first_image_from_markdown(content):
    """
    從 Markdown 內容中提取第一張圖片

    Args:
        content: Markdown 內容

    Returns:
        str or None: 圖片 URL
    """
    if not content:
        return None

    # 匹配 Markdown 圖片語法: ![alt](url)
    match = re.search(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
    if match:
        return match.group(2)

    # 匹配 HTML img 標籤
    match = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)

    return None


def get_reading_time(content):
    """
    計算閱讀時間（分鐘）
    假設平均閱讀速度為每分鐘 200 字

    Args:
        content: 文章內容

    Returns:
        int: 預估閱讀時間（分鐘）
    """
    if not content:
        return 0

    # 移除 HTML 和 Markdown 語法
    text = strip_tags(content)
    text = re.sub(r'[#*`>\[\]()]', '', text)

    # 計算字數（包含中英文）
    # 中文字算 1 個字，英文單詞也算 1 個字
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    english_words = len(re.findall(r'[a-zA-Z]+', text))

    total_words = chinese_chars + english_words

    # 每分鐘 200 字
    reading_time = max(1, round(total_words / 200))

    return reading_time
