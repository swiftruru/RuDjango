/**
 * Markdown 即時預覽功能
 * 使用 marked.js 解析 Markdown
 */

(function() {
    'use strict';

    let previewVisible = false;
    let debounceTimer = null;

    // 初始化
    function init() {
        const toggleBtn = document.getElementById('toggle-preview');
        const previewPane = document.getElementById('preview-pane');
        const contentTextarea = document.getElementById('id_content');
        const previewContent = document.getElementById('preview-content');

        if (!toggleBtn || !previewPane || !contentTextarea || !previewContent) {
            console.warn('Preview elements not found');
            return;
        }

        // 初始化 Mermaid
        if (window.mermaid) {
            mermaid.initialize({
                startOnLoad: false,
                theme: 'dark',
                securityLevel: 'loose'
            });
        }

        // 切換預覽顯示
        toggleBtn.addEventListener('click', function() {
            previewVisible = !previewVisible;

            if (previewVisible) {
                previewPane.style.display = 'block';
                toggleBtn.querySelector('.preview-text').textContent = '隱藏預覽';
                toggleBtn.querySelector('.preview-icon').textContent = '🙈';
                updatePreview();
            } else {
                previewPane.style.display = 'none';
                toggleBtn.querySelector('.preview-text').textContent = '顯示預覽';
                toggleBtn.querySelector('.preview-icon').textContent = '👁️';
            }
        });

        // 監聽內容變化
        contentTextarea.addEventListener('input', function() {
            if (previewVisible) {
                // 使用 debounce 避免頻繁更新
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(updatePreview, 300);
            }
        });

        // 同步捲動
        let isEditorScrolling = false;
        let isPreviewScrolling = false;

        contentTextarea.addEventListener('scroll', function() {
            if (isPreviewScrolling) {
                isPreviewScrolling = false;
                return;
            }

            isEditorScrolling = true;
            syncScroll(contentTextarea, previewContent);
        });

        previewContent.addEventListener('scroll', function() {
            if (isEditorScrolling) {
                isEditorScrolling = false;
                return;
            }

            isPreviewScrolling = true;
            syncScroll(previewContent, contentTextarea);
        });

        // 更新預覽內容
        async function updatePreview() {
            const markdown = contentTextarea.value;

            if (!markdown.trim()) {
                previewContent.innerHTML = '<div class="preview-placeholder">在左側輸入 Markdown 內容，這裡會即時顯示預覽</div>';
                return;
            }

            try {
                // 設定 marked.js 選項
                marked.setOptions({
                    breaks: false,  // 關閉自動換行，避免破壞 $$...$$ 區塊公式
                    gfm: true       // 啟用 GitHub Flavored Markdown
                });

                // 使用 marked 解析 Markdown
                const html = marked.parse(markdown);
                previewContent.innerHTML = html;

                // 處理 @mention 連結
                highlightMentions();

                // 為程式碼區塊添加語法高亮（如果有 highlight.js）
                if (window.hljs) {
                    previewContent.querySelectorAll('pre code:not(.language-mermaid)').forEach((block) => {
                        // 移除之前的高亮類別（如果有的話）
                        block.removeAttribute('data-highlighted');
                        // 應用語法高亮
                        hljs.highlightElement(block);
                    });
                }

                // 渲染 Mermaid 圖表
                if (window.mermaid) {
                    const mermaidBlocks = previewContent.querySelectorAll('pre code.language-mermaid');
                    for (let i = 0; i < mermaidBlocks.length; i++) {
                        const block = mermaidBlocks[i];
                        const code = block.textContent;
                        const id = `mermaid-${Date.now()}-${i}`;

                        try {
                            const { svg } = await mermaid.render(id, code);
                            const container = document.createElement('div');
                            container.className = 'mermaid-container';
                            container.innerHTML = svg;
                            block.parentElement.replaceWith(container);
                        } catch (err) {
                            console.error('Mermaid render error:', err);
                            block.parentElement.innerHTML = `<div class="mermaid-error">Mermaid 渲染錯誤: ${err.message}</div>`;
                        }
                    }
                }

                // 渲染數學公式（KaTeX）
                if (window.renderMathInElement) {
                    renderMathInElement(previewContent, {
                        delimiters: [
                            {left: '$$', right: '$$', display: true},
                            {left: '$', right: '$', display: false},
                            {left: '\\[', right: '\\]', display: true},
                            {left: '\\(', right: '\\)', display: false}
                        ],
                        throwOnError: false
                    });
                }
            } catch (error) {
                console.error('Markdown parse error:', error);
                previewContent.innerHTML = '<div class="preview-placeholder" style="color: #e53e3e;">解析錯誤：' + error.message + '</div>';
            }
        }

        // 同步捲動
        function syncScroll(source, target) {
            const sourceScrollRatio = source.scrollTop / (source.scrollHeight - source.clientHeight);
            target.scrollTop = sourceScrollRatio * (target.scrollHeight - target.clientHeight);
        }

        // 處理 @mention 高亮
        function highlightMentions() {
            const content = previewContent.innerHTML;

            // 匹配 @username 格式
            const mentionRegex = /@([a-zA-Z0-9_]+)/g;

            const highlightedContent = content.replace(mentionRegex, function(match, username) {
                return `<a href="/blog/member/${username}/" class="mention" title="${match}">@${username}</a>`;
            });

            previewContent.innerHTML = highlightedContent;
        }
    }

    // DOM 準備好後初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
